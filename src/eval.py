"""
Evaluation Script
Compute FAR, FRR, EER on test set and generate visualizations.
"""

import os
import argparse
import json
from pathlib import Path
import numpy as np
import torch
from tqdm import tqdm

from dataset import make_dataloaders
from model import BiLSTMEncoder
from prototypes import load_prototypes
from calibration import load_calibrator
from inference_utils import score_vs_prototypes
from utils.metrics import compute_eer, compute_metrics_at_thresholds
from utils.viz import plot_roc_curve, plot_det_curve, plot_score_distribution


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


def main():
    parser = argparse.ArgumentParser(description='Evaluate BiLSTM authentication model')
    parser.add_argument('--data_dir', type=str, default='data/processed', help='Processed data directory')
    parser.add_argument('--models_dir', type=str, default='models', help='Models directory')
    parser.add_argument('--output_dir', type=str, default='outputs', help='Output directory')
    parser.add_argument('--batch_size', type=int, default=64, help='Batch size')
    parser.add_argument('--device', type=str, default='cpu', help='Device (cpu or cuda)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    models_dir = Path(args.models_dir)
    
    # Load config
    with open(models_dir / 'config.json', 'r') as f:
        config = json.load(f)
    
    print(f"Config: {config}")
    
    # Create dataloaders
    print(f"Loading data for subjects: {config['subjects']}")
    _, _, test_loader = make_dataloaders(
        processed_dir=args.data_dir,
        subject_ids=config['subjects'],
        batch_size=args.batch_size,
        num_workers=0,
        seed=args.seed
    )
    
    # Load model
    print("Loading model...")
    model = BiLSTMEncoder(
        n_channels=config['n_channels'],
        hidden_size=config['hidden_size'],
        embedding_size=config['embedding_size'],
        num_layers=config['num_layers'],
        use_attention=config['use_attention'],
        num_classes=config['num_classes']
    )
    
    model.load_state_dict(torch.load(models_dir / 'encoder.pth', map_location=args.device))
    model.eval()
    model.to(args.device)
    
    # Load prototypes
    print("Loading prototypes...")
    prototypes = load_prototypes(str(models_dir / 'prototypes.npz'))
    
    # Extract test embeddings
    print("Extracting test embeddings...")
    test_embeddings, test_labels = extract_embeddings(model, test_loader, device=args.device)
    print(f"Test embeddings: {test_embeddings.shape}")
    
    # Compute scores
    print("Computing similarity scores...")
    genuine_scores = []
    impostor_scores = []
    
    for i, (emb, label) in enumerate(tqdm(zip(test_embeddings, test_labels), total=len(test_embeddings))):
        user_id = int(label)
        
        if user_id not in prototypes:
            continue
        
        # Genuine score
        genuine_score = score_vs_prototypes(emb, prototypes[user_id], aggregation='max')
        genuine_scores.append(genuine_score)
        
        # Impostor scores (vs all other users)
        for other_user_id in prototypes:
            if other_user_id != user_id:
                impostor_score = score_vs_prototypes(emb, prototypes[other_user_id], aggregation='max')
                impostor_scores.append(impostor_score)
    
    genuine_scores = np.array(genuine_scores)
    impostor_scores = np.array(impostor_scores)
    
    print(f"Genuine scores: {len(genuine_scores)}")
    print(f"Impostor scores: {len(impostor_scores)}")
    
    # Compute EER
    print("\n=== Computing Metrics ===")
    eer, eer_threshold = compute_eer(genuine_scores, impostor_scores)
    print(f"EER: {eer:.4f} at threshold {eer_threshold:.4f}")
    
    # Compute FAR/FRR at multiple thresholds
    thresholds = [0.3, 0.5, 0.6, 0.7, 0.8, eer_threshold]
    metrics = compute_metrics_at_thresholds(genuine_scores, impostor_scores, thresholds)
    
    print("\nFAR/FRR at different thresholds:")
    for i, thresh in enumerate(thresholds):
        print(f"  Threshold {thresh:.3f}: FAR={metrics['far'][i]:.4f}, FRR={metrics['frr'][i]:.4f}")
    
    # Save results
    results = {
        'eer': float(eer),
        'eer_threshold': float(eer_threshold),
        'genuine_scores_mean': float(genuine_scores.mean()),
        'genuine_scores_std': float(genuine_scores.std()),
        'impostor_scores_mean': float(impostor_scores.mean()),
        'impostor_scores_std': float(impostor_scores.std()),
        'thresholds': thresholds,
        'far': metrics['far'].tolist(),
        'frr': metrics['frr'].tolist()
    }
    
    with open(output_dir / 'eval_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {output_dir / 'eval_results.json'}")
    
    # Generate plots
    print("\n=== Generating Plots ===")
    
    plot_roc_curve(genuine_scores, impostor_scores, save_path=str(output_dir / 'roc.png'))
    print(f"ROC curve saved to {output_dir / 'roc.png'}")
    
    plot_det_curve(genuine_scores, impostor_scores, save_path=str(output_dir / 'det.png'))
    print(f"DET curve saved to {output_dir / 'det.png'}")
    
    plot_score_distribution(genuine_scores, impostor_scores, save_path=str(output_dir / 'score_dist.png'))
    print(f"Score distribution saved to {output_dir / 'score_dist.png'}")
    
    print("\n=== Evaluation Complete ===")


if __name__ == "__main__":
    main()
