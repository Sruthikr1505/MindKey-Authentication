"""
Training Pipeline
Warmup classification -> Metric learning -> Compute prototypes -> Train spoof detector -> Calibration
"""

import os
import argparse
from pathlib import Path
import numpy as np
import torch
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
from pytorch_metric_learning import losses, miners
from tqdm import tqdm

from dataset import make_dataloaders
from model import BiLSTMEncoder
from prototypes import compute_user_prototypes, compute_embeddings_by_user, save_prototypes
from calibration import fit_platt, save_calibrator
from spoof_detector import train_autoencoder, compute_reconstruction_errors, choose_spoof_threshold, save_spoof_model


def extract_embeddings(model, dataloader, device='cpu'):
    """Extract embeddings and labels from dataloader"""
    model.eval()
    model.to(device)
    
    all_embeddings = []
    all_labels = []
    
    with torch.no_grad():
        for batch_x, batch_y in tqdm(dataloader, desc='Extracting embeddings'):
            batch_x = batch_x.to(device)
            embeddings = model(batch_x)
            all_embeddings.append(embeddings.cpu().numpy())
            all_labels.append(batch_y.numpy())
    
    all_embeddings = np.concatenate(all_embeddings, axis=0)
    all_labels = np.concatenate(all_labels, axis=0)
    
    return all_embeddings, all_labels


def warmup_training(
    model,
    train_loader,
    val_loader,
    epochs,
    device,
    checkpoint_dir
):
    """Warmup training with classification loss"""
    print("\n=== Warmup Training (Classification) ===")
    
    model.set_training_mode('warmup')
    
    checkpoint_callback = ModelCheckpoint(
        dirpath=checkpoint_dir,
        filename='warmup-{epoch:02d}-{val_acc:.3f}',
        monitor='val_acc',
        mode='max',
        save_top_k=1
    )
    
    early_stop_callback = EarlyStopping(
        monitor='val_loss',
        patience=5,
        mode='min'
    )
    
    trainer = pl.Trainer(
        max_epochs=epochs,
        accelerator='gpu' if device == 'cuda' else 'cpu',
        devices=1,
        callbacks=[checkpoint_callback, early_stop_callback],
        enable_progress_bar=True,
        log_every_n_steps=10
    )
    
    trainer.fit(model, train_loader, val_loader)
    
    # Load best checkpoint
    best_model_path = checkpoint_callback.best_model_path
    print(f"Best warmup model: {best_model_path}")
    
    return model


def metric_training(
    model,
    train_loader,
    val_loader,
    epochs,
    device,
    checkpoint_dir,
    metric_loss_type='proxyanchor'
):
    """Metric learning training"""
    print(f"\n=== Metric Learning Training ({metric_loss_type}) ===")
    
    model.set_training_mode('metric')
    
    # Create metric loss
    if metric_loss_type == 'proxyanchor':
        loss_fn = losses.ProxyAnchorLoss(
            num_classes=model.num_classes,
            embedding_size=model.embedding_size,
            margin=0.1,
            alpha=32
        ).to(device)
    elif metric_loss_type == 'triplet':
        loss_fn = losses.TripletMarginLoss(margin=0.2)
        miner = miners.MultiSimilarityMiner()
    else:
        raise ValueError(f"Unknown metric loss: {metric_loss_type}")
    
    # Wrap loss function
    def metric_loss_wrapper(embeddings, labels):
        if metric_loss_type == 'triplet':
            hard_pairs = miner(embeddings, labels)
            return loss_fn(embeddings, labels, hard_pairs)
        else:
            return loss_fn(embeddings, labels)
    
    model.set_metric_loss(metric_loss_wrapper)
    
    checkpoint_callback = ModelCheckpoint(
        dirpath=checkpoint_dir,
        filename='metric-{epoch:02d}',
        monitor='train_metric_loss',
        mode='min',
        save_top_k=1
    )
    
    trainer = pl.Trainer(
        max_epochs=epochs,
        accelerator='gpu' if device == 'cuda' else 'cpu',
        devices=1,
        callbacks=[checkpoint_callback],
        enable_progress_bar=True,
        log_every_n_steps=10
    )
    
    trainer.fit(model, train_loader, val_loader)
    
    # Load best checkpoint
    best_model_path = checkpoint_callback.best_model_path
    print(f"Best metric model: {best_model_path}")
    
    # Load best weights
    checkpoint = torch.load(best_model_path, map_location=device)
    model.load_state_dict(checkpoint['state_dict'])
    
    return model


def main():
    parser = argparse.ArgumentParser(description='Train BiLSTM authentication model')
    parser.add_argument('--data_dir', type=str, default='data/processed', help='Processed data directory')
    parser.add_argument('--subjects', type=int, nargs='+', default=list(range(1, 11)), help='Subject IDs')
    parser.add_argument('--batch_size', type=int, default=64, help='Batch size')
    parser.add_argument('--warmup_epochs', type=int, default=3, help='Warmup epochs')
    parser.add_argument('--metric_epochs', type=int, default=20, help='Metric learning epochs')
    parser.add_argument('--lr', type=float, default=1e-3, help='Learning rate')
    parser.add_argument('--metric_loss', type=str, default='proxyanchor', choices=['proxyanchor', 'triplet'])
    parser.add_argument('--use_attention', action='store_true', help='Use temporal attention')
    parser.add_argument('--fast', action='store_true', help='Fast mode: fewer epochs')
    parser.add_argument('--device', type=str, default='cpu', help='Device (cpu or cuda)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    
    args = parser.parse_args()
    
    # Fast mode
    if args.fast:
        args.warmup_epochs = 1
        args.metric_epochs = 2
        print("Fast mode: reduced epochs")
    
    # Set seeds
    pl.seed_everything(args.seed)
    
    # Create directories
    checkpoint_dir = Path('checkpoints')
    checkpoint_dir.mkdir(exist_ok=True)
    
    models_dir = Path('models')
    models_dir.mkdir(exist_ok=True)
    
    # Create dataloaders
    print(f"Loading data for subjects: {args.subjects}")
    train_loader, val_loader, test_loader = make_dataloaders(
        processed_dir=args.data_dir,
        subject_ids=args.subjects,
        batch_size=args.batch_size,
        num_workers=0,  # Set to 0 for compatibility
        seed=args.seed
    )
    
    # Detect number of channels from first batch
    sample_batch = next(iter(train_loader))
    n_channels = sample_batch[0].shape[1]  # (batch, channels, timesteps)
    print(f"Detected {n_channels} channels from data")
    
    # Create model
    model = BiLSTMEncoder(
        n_channels=n_channels,
        hidden_size=128,
        embedding_size=128,
        num_layers=2,
        use_attention=args.use_attention,
        num_classes=len(args.subjects),
        lr=args.lr
    )
    
    # Warmup training
    model = warmup_training(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=args.warmup_epochs,
        device=args.device,
        checkpoint_dir=checkpoint_dir
    )
    
    # Metric learning training
    model = metric_training(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=args.metric_epochs,
        device=args.device,
        checkpoint_dir=checkpoint_dir,
        metric_loss_type=args.metric_loss
    )
    
    # Extract embeddings
    print("\n=== Extracting Embeddings ===")
    train_embeddings, train_labels = extract_embeddings(model, train_loader, device=args.device)
    val_embeddings, val_labels = extract_embeddings(model, val_loader, device=args.device)
    
    print(f"Train embeddings: {train_embeddings.shape}")
    print(f"Val embeddings: {val_embeddings.shape}")
    
    # Compute prototypes
    print("\n=== Computing Prototypes ===")
    train_emb_by_user = compute_embeddings_by_user(train_embeddings, train_labels)
    prototypes = compute_user_prototypes(train_emb_by_user, k=2, seed=args.seed)
    save_prototypes(prototypes, str(models_dir / 'prototypes.npz'))
    
    # Train spoof detector
    print("\n=== Training Spoof Detector ===")
    spoof_model = train_autoencoder(
        embeddings=train_embeddings,
        embedding_dim=128,
        epochs=30 if not args.fast else 5,
        batch_size=64,
        device=args.device,
        seed=args.seed
    )
    
    # Compute spoof threshold on validation set
    val_errors = compute_reconstruction_errors(spoof_model, val_embeddings, device=args.device)
    spoof_threshold = choose_spoof_threshold(val_errors, percentile=99.0)
    print(f"Spoof threshold (99th percentile): {spoof_threshold:.6f}")
    
    save_spoof_model(spoof_model, str(models_dir / 'spoof_model.pth'))
    np.save(str(models_dir / 'spoof_threshold.npy'), spoof_threshold)
    
    # Calibration
    print("\n=== Calibration ===")
    from inference_utils import score_vs_prototypes
    
    # Compute validation scores
    val_scores = []
    val_score_labels = []
    
    for i, (emb, label) in enumerate(zip(val_embeddings, val_labels)):
        user_id = int(label)
        if user_id in prototypes:
            # Genuine score
            genuine_score = score_vs_prototypes(emb, prototypes[user_id], aggregation='max')
            val_scores.append(genuine_score)
            val_score_labels.append(1)
            
            # Impostor scores (vs other users)
            for other_user_id in prototypes:
                if other_user_id != user_id:
                    impostor_score = score_vs_prototypes(emb, prototypes[other_user_id], aggregation='max')
                    val_scores.append(impostor_score)
                    val_score_labels.append(0)
    
    val_scores = np.array(val_scores)
    val_score_labels = np.array(val_score_labels)
    
    print(f"Validation scores: {len(val_scores)} (genuine: {val_score_labels.sum()}, impostor: {(1-val_score_labels).sum()})")
    
    # Fit calibrator
    calibrator = fit_platt(val_scores, val_score_labels, seed=args.seed)
    save_calibrator(calibrator, str(models_dir / 'calibrator.pkl'))
    
    # Save final model
    print("\n=== Saving Final Model ===")
    torch.save(model.state_dict(), str(models_dir / 'encoder.pth'))
    
    # Save config
    config = {
        'subjects': args.subjects,
        'n_channels': 32,
        'hidden_size': 128,
        'embedding_size': 128,
        'num_layers': 2,
        'use_attention': args.use_attention,
        'num_classes': len(args.subjects)
    }
    import json
    with open(models_dir / 'config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n=== Training Complete ===")
    print(f"Models saved to {models_dir}/")
    print("Files created:")
    print("  - encoder.pth (BiLSTM encoder)")
    print("  - prototypes.npz (user prototypes)")
    print("  - spoof_model.pth (spoof detector)")
    print("  - spoof_threshold.npy (spoof threshold)")
    print("  - calibrator.pkl (score calibrator)")
    print("  - config.json (model config)")


if __name__ == "__main__":
    main()
