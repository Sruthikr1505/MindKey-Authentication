"""
Training pipeline for BiLSTM encoder with warmup and metric learning.
"""

import os
import argparse
import logging
from pathlib import Path
import numpy as np
import torch
import pytorch_lightning as pl
from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping
from pytorch_metric_learning import losses, miners

from model import BiLSTMEncoder
from dataset import make_dataloaders
from prototypes import compute_user_prototypes, save_prototypes
from calibration import fit_platt, save_calibrator
from spoof_detector import train_autoencoder, compute_spoof_threshold, save_spoof_model
from inference_utils import batch_compute_embeddings, score_vs_prototypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_warmup(
    model: BiLSTMEncoder,
    train_loader,
    val_loader,
    epochs: int,
    device: str = 'cpu'
):
    """
    Warmup training with classification loss.
    
    Args:
        model: BiLSTM encoder model
        train_loader: Training dataloader
        val_loader: Validation dataloader
        epochs: Number of warmup epochs
        device: Device to train on
    """
    logger.info(f"Starting warmup training for {epochs} epochs...")
    
    model.set_warmup_mode(True)
    
    # Callbacks
    checkpoint_callback = ModelCheckpoint(
        dirpath='checkpoints',
        filename='warmup-{epoch:02d}-{val_acc:.4f}',
        monitor='val_acc',
        mode='max',
        save_top_k=1
    )
    
    # Trainer
    trainer = pl.Trainer(
        max_epochs=epochs,
        accelerator='gpu' if device == 'cuda' else 'cpu',
        devices=1,
        callbacks=[checkpoint_callback],
        enable_progress_bar=True,
        log_every_n_steps=10
    )
    
    # Train
    trainer.fit(model, train_loader, val_loader)
    
    logger.info("Warmup training complete")


def train_metric_learning(
    model: BiLSTMEncoder,
    train_loader,
    val_loader,
    epochs: int,
    metric_loss: str = 'proxyanchor',
    device: str = 'cpu'
):
    """
    Metric learning training.
    
    Args:
        model: BiLSTM encoder model
        train_loader: Training dataloader
        val_loader: Validation dataloader
        epochs: Number of metric learning epochs
        metric_loss: Type of metric loss ('proxyanchor', 'triplet')
        device: Device to train on
    """
    logger.info(f"Starting metric learning training for {epochs} epochs with {metric_loss} loss...")
    
    model.set_warmup_mode(False)
    
    # Create metric loss
    num_classes = model.num_classes
    embedding_size = model.embedding_size
    
    if metric_loss == 'proxyanchor':
        loss_fn = losses.ProxyAnchorLoss(
            num_classes=num_classes,
            embedding_size=embedding_size,
            margin=0.1,
            alpha=32
        ).to(device)
    elif metric_loss == 'triplet':
        loss_fn = losses.TripletMarginLoss(margin=0.2)
        miner = miners.TripletMarginMiner(margin=0.2)
    else:
        raise ValueError(f"Unknown metric loss: {metric_loss}")
    
    model.set_metric_loss(loss_fn)
    
    # Callbacks
    checkpoint_callback = ModelCheckpoint(
        dirpath='checkpoints',
        filename='metric-{epoch:02d}',
        monitor='train_metric_loss',
        mode='min',
        save_top_k=1
    )
    
    early_stop_callback = EarlyStopping(
        monitor='train_metric_loss',
        patience=7,
        mode='min'
    )
    
    # Trainer
    trainer = pl.Trainer(
        max_epochs=epochs,
        accelerator='gpu' if device == 'cuda' else 'cpu',
        devices=1,
        callbacks=[checkpoint_callback, early_stop_callback],
        enable_progress_bar=True,
        log_every_n_steps=10
    )
    
    # Train
    trainer.fit(model, train_loader, val_loader)
    
    logger.info("Metric learning training complete")


def compute_and_save_prototypes(
    model: BiLSTMEncoder,
    train_loader,
    subject_ids: list,
    k: int = 2,
    device: str = 'cpu'
):
    """
    Compute and save user prototypes.
    
    Args:
        model: Trained encoder model
        train_loader: Training dataloader
        subject_ids: List of subject IDs
        k: Number of prototypes per user
        device: Device to run on
    """
    logger.info("Computing user prototypes...")
    
    # Compute embeddings
    embeddings, labels = batch_compute_embeddings(model, train_loader, device)
    
    # Group by user
    embeddings_by_user = {}
    for subject_id in subject_ids:
        user_idx = subject_id - 1  # 0-indexed
        mask = labels == user_idx
        embeddings_by_user[subject_id] = embeddings[mask]
        logger.info(f"User {subject_id}: {embeddings[mask].shape[0]} embeddings")
    
    # Compute prototypes
    prototypes = compute_user_prototypes(embeddings_by_user, k=k, method='kmeans')
    
    # Save
    os.makedirs('models', exist_ok=True)
    save_prototypes(prototypes, 'models/prototypes.npz')
    
    logger.info(f"Saved prototypes for {len(prototypes)} users")


def train_and_save_calibrator(
    model: BiLSTMEncoder,
    val_loader,
    prototypes: dict,
    device: str = 'cpu'
):
    """
    Train and save score calibrator.
    
    Args:
        model: Trained encoder model
        val_loader: Validation dataloader
        prototypes: User prototypes
        device: Device to run on
    """
    logger.info("Training calibrator...")
    
    # Compute validation embeddings
    embeddings, labels = batch_compute_embeddings(model, val_loader, device)
    
    # Compute similarities and labels for calibration
    similarities = []
    binary_labels = []
    
    for emb, label in zip(embeddings, labels):
        user_id = label + 1  # Convert back to 1-indexed
        
        # Genuine score
        if user_id in prototypes:
            genuine_score = score_vs_prototypes(emb, prototypes[user_id], aggregation='max')
            similarities.append(genuine_score)
            binary_labels.append(1)
        
        # Impostor scores (sample a few other users)
        other_users = [uid for uid in prototypes.keys() if uid != user_id]
        for other_user in np.random.choice(other_users, min(3, len(other_users)), replace=False):
            impostor_score = score_vs_prototypes(emb, prototypes[other_user], aggregation='max')
            similarities.append(impostor_score)
            binary_labels.append(0)
    
    similarities = np.array(similarities)
    binary_labels = np.array(binary_labels)
    
    logger.info(f"Calibration data: {len(similarities)} samples "
               f"({binary_labels.sum()} genuine, {(1-binary_labels).sum()} impostor)")
    
    # Fit calibrator
    calibrator = fit_platt(similarities, binary_labels)
    
    # Save
    save_calibrator(calibrator, 'models/calibrator.pkl')
    
    logger.info("Saved calibrator")


def train_and_save_spoof_detector(
    model: BiLSTMEncoder,
    train_loader,
    device: str = 'cpu'
):
    """
    Train and save spoof detector.
    
    Args:
        model: Trained encoder model
        train_loader: Training dataloader
        device: Device to run on
    """
    logger.info("Training spoof detector...")
    
    # Compute training embeddings
    embeddings, _ = batch_compute_embeddings(model, train_loader, device)
    
    # Train autoencoder
    spoof_model, val_errors = train_autoencoder(
        embeddings,
        emb_dim=model.embedding_size,
        epochs=50,
        batch_size=64,
        device=device
    )
    
    # Compute threshold
    threshold = compute_spoof_threshold(val_errors, percentile=99.0)
    
    # Save
    save_spoof_model(spoof_model, threshold, 'models/spoof_model.pth')
    
    logger.info("Saved spoof detector")


def main():
    parser = argparse.ArgumentParser(description="Train BiLSTM encoder for EEG authentication")
    parser.add_argument('--data_dir', type=str, default='data/processed',
                       help='Directory containing processed .npy files')
    parser.add_argument('--subjects', type=int, nargs='+', default=list(range(1, 11)),
                       help='Subject IDs to use')
    parser.add_argument('--batch_size', type=int, default=64,
                       help='Batch size')
    parser.add_argument('--warmup_epochs', type=int, default=3,
                       help='Number of warmup epochs')
    parser.add_argument('--metric_epochs', type=int, default=30,
                       help='Number of metric learning epochs')
    parser.add_argument('--lr', type=float, default=1e-3,
                       help='Learning rate')
    parser.add_argument('--metric_loss', type=str, default='proxyanchor',
                       choices=['proxyanchor', 'triplet'],
                       help='Metric learning loss')
    parser.add_argument('--use_attention', action='store_true', default=True,
                       help='Use temporal attention')
    parser.add_argument('--n_channels', type=int, default=48,
                       help='Number of EEG channels')
    parser.add_argument('--device', type=str, default='cpu',
                       choices=['cpu', 'cuda'],
                       help='Device to train on')
    parser.add_argument('--fast', action='store_true',
                       help='Fast mode for demo (fewer epochs)')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed')
    
    args = parser.parse_args()
    
    # Set seeds
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    pl.seed_everything(args.seed)
    
    # Fast mode
    if args.fast:
        args.warmup_epochs = 1
        args.metric_epochs = 1
        logger.info("Fast mode: using reduced epochs")
    
    # Create dataloaders
    logger.info("Creating dataloaders...")
    train_loader, val_loader, test_loader = make_dataloaders(
        processed_dir=args.data_dir,
        subject_ids=args.subjects,
        batch_size=args.batch_size,
        num_workers=0,  # Set to 0 for Windows compatibility
        seed=args.seed
    )
    
    # Create model
    logger.info("Creating model...")
    model = BiLSTMEncoder(
        n_channels=args.n_channels,
        hidden_size=128,
        num_layers=2,
        embedding_size=128,
        use_attention=args.use_attention,
        num_classes=len(args.subjects),
        learning_rate=args.lr
    )
    
    # Warmup training
    if args.warmup_epochs > 0:
        train_warmup(model, train_loader, val_loader, args.warmup_epochs, args.device)
    
    # Metric learning training
    train_metric_learning(model, train_loader, val_loader, args.metric_epochs, 
                         args.metric_loss, args.device)
    
    # Save final model
    os.makedirs('checkpoints', exist_ok=True)
    torch.save(model.state_dict(), 'checkpoints/best.ckpt')
    logger.info("Saved final model to checkpoints/best.ckpt")
    
    # Compute and save prototypes
    from prototypes import load_prototypes
    compute_and_save_prototypes(model, train_loader, args.subjects, k=2, device=args.device)
    prototypes = load_prototypes('models/prototypes.npz')
    
    # Train and save calibrator
    train_and_save_calibrator(model, val_loader, prototypes, device=args.device)
    
    # Train and save spoof detector
    train_and_save_spoof_detector(model, train_loader, device=args.device)
    
    logger.info("Training pipeline complete!")


if __name__ == "__main__":
    main()
