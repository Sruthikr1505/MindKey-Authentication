"""
Evaluation script for computing FAR, FRR, EER, and generating plots.
"""

import os
import argparse
import json
import logging
from pathlib import Path
import numpy as np
import torch

from model import BiLSTMEncoder
from dataset import make_dataloaders
from prototypes import load_prototypes
from calibration import load_calibrator
from inference_utils import batch_compute_embeddings, score_vs_prototypes
from utils.metrics import compute_eer, compute_far_frr, compute_roc_curve, compute_det_curve
from utils.viz import plot_roc_curve, plot_det_curve, plot_score_distribution

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def evaluate_authentication(
    model: BiLSTMEncoder,
    test_loader,
    prototypes: dict,
    device: str = 'cpu'
):
    """
    Evaluate authentication performance.
    
    Args:
        model: Trained encoder model
        test_loader: Test dataloader
        prototypes: User prototypes
        device: Device to run on
    
    Returns:
        results: Dictionary containing evaluation metrics
    """
    logger.info("Computing test embeddings...")
    
    # Compute test embeddings
    embeddings, labels = batch_compute_embeddings(model, test_loader, device)
    
    # Compute genuine and impostor scores
    genuine_scores = []
    impostor_scores = []
    
    logger.info("Computing similarity scores...")
    
    for emb, label in zip(embeddings, labels):
        user_id = label + 1  # Convert to 1-indexed
        
        if user_id not in prototypes:
            continue
        
        # Genuine score
        genuine_score = score_vs_prototypes(emb, prototypes[user_id], aggregation='max')
        genuine_scores.append(genuine_score)
        
        # Impostor scores (against all other users)
        for other_user in prototypes.keys():
            if other_user != user_id:
                impostor_score = score_vs_prototypes(emb, prototypes[other_user], aggregation='max')
                impostor_scores.append(impostor_score)
    
    genuine_scores = np.array(genuine_scores)
    impostor_scores = np.array(impostor_scores)
    
    logger.info(f"Genuine scores: {len(genuine_scores)}")
    logger.info(f"Impostor scores: {len(impostor_scores)}")
    
    # Compute EER
    eer, eer_threshold = compute_eer(genuine_scores, impostor_scores)
    
    logger.info(f"EER: {eer*100:.2f}%")
    logger.info(f"EER Threshold: {eer_threshold:.4f}")
    
    # Compute FAR/FRR at various thresholds
    thresholds = np.linspace(genuine_scores.min(), genuine_scores.max(), 100)
    far, frr = compute_far_frr(genuine_scores, impostor_scores, thresholds)
    
    # Find FAR at specific FRR values
    frr_targets = [0.01, 0.05, 0.10]
    far_at_frr = {}
    for frr_target in frr_targets:
        idx = np.argmin(np.abs(frr - frr_target))
        far_at_frr[f'FAR@FRR={frr_target}'] = float(far[idx])
    
    # Compute ROC curve
    far_roc, tar_roc, _ = compute_roc_curve(genuine_scores, impostor_scores)
    
    # Compute DET curve
    far_det, frr_det = compute_det_curve(genuine_scores, impostor_scores)
    
    # Compile results
    results = {
        'eer': float(eer),
        'eer_threshold': float(eer_threshold),
        'genuine_scores': {
            'mean': float(genuine_scores.mean()),
            'std': float(genuine_scores.std()),
            'min': float(genuine_scores.min()),
            'max': float(genuine_scores.max())
        },
        'impostor_scores': {
            'mean': float(impostor_scores.mean()),
            'std': float(impostor_scores.std()),
            'min': float(impostor_scores.min()),
            'max': float(impostor_scores.max())
        },
        'far_at_frr': far_at_frr,
        'n_genuine': len(genuine_scores),
        'n_impostor': len(impostor_scores)
    }
    
    return results, genuine_scores, impostor_scores, far_roc, tar_roc, far_det, frr_det, eer


def main():
    parser = argparse.ArgumentParser(description="Evaluate EEG authentication system")
    parser.add_argument('--data_dir', type=str, default='data/processed',
                       help='Directory containing processed .npy files')
    parser.add_argument('--checkpoint', type=str, default='checkpoints/best.ckpt',
                       help='Path to model checkpoint')
    parser.add_argument('--prototypes', type=str, default='models/prototypes.npz',
                       help='Path to prototypes file')
    parser.add_argument('--subjects', type=int, nargs='+', default=list(range(1, 11)),
                       help='Subject IDs to evaluate')
    parser.add_argument('--batch_size', type=int, default=64,
                       help='Batch size')
    parser.add_argument('--n_channels', type=int, default=48,
                       help='Number of EEG channels')
    parser.add_argument('--device', type=str, default='cpu',
                       choices=['cpu', 'cuda'],
                       help='Device to run on')
    parser.add_argument('--output_dir', type=str, default='outputs',
                       help='Output directory for results')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed')
    
    args = parser.parse_args()
    
    # Set seeds
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load model
    logger.info("Loading model...")
    model = BiLSTMEncoder(
        n_channels=args.n_channels,
        hidden_size=128,
        num_layers=2,
        embedding_size=128,
        use_attention=True,
        num_classes=len(args.subjects)
    )
    
    # Load checkpoint
    checkpoint = torch.load(args.checkpoint, map_location=args.device)
    # Filter out metric_loss_fn keys if present
    model_state = {k: v for k, v in checkpoint.items() if not k.startswith('metric_loss_fn.')}
    model.load_state_dict(model_state, strict=False)
    model.eval()
    model.to(args.device)
    
    # Load prototypes
    logger.info("Loading prototypes...")
    prototypes = load_prototypes(args.prototypes)
    
    # Create test dataloader
    logger.info("Creating test dataloader...")
    _, _, test_loader = make_dataloaders(
        processed_dir=args.data_dir,
        subject_ids=args.subjects,
        batch_size=args.batch_size,
        num_workers=0,
        seed=args.seed
    )
    
    # Evaluate
    results, genuine_scores, impostor_scores, far_roc, tar_roc, far_det, frr_det, eer = \
        evaluate_authentication(model, test_loader, prototypes, args.device)
    
    # Save results
    results_path = os.path.join(args.output_dir, 'eval_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Saved results to {results_path}")
    
    # Print summary
    print("\n" + "="*50)
    print("EVALUATION RESULTS")
    print("="*50)
    print(f"EER: {results['eer']*100:.2f}%")
    print(f"EER Threshold: {results['eer_threshold']:.4f}")
    print(f"\nGenuine Scores: mean={results['genuine_scores']['mean']:.4f}, "
          f"std={results['genuine_scores']['std']:.4f}")
    print(f"Impostor Scores: mean={results['impostor_scores']['mean']:.4f}, "
          f"std={results['impostor_scores']['std']:.4f}")
    print(f"\nFAR at specific FRR values:")
    for key, value in results['far_at_frr'].items():
        print(f"  {key}: {value*100:.2f}%")
    print("="*50 + "\n")
    
    # Generate plots
    logger.info("Generating plots...")
    
    # ROC curve
    plot_roc_curve(
        far_roc, tar_roc, eer=eer,
        title="ROC Curve - EEG Authentication",
        save_path=os.path.join(args.output_dir, 'roc.png')
    )
    
    # DET curve
    plot_det_curve(
        far_det, frr_det, eer=eer,
        title="DET Curve - EEG Authentication",
        save_path=os.path.join(args.output_dir, 'det.png')
    )
    
    # Score distribution
    plot_score_distribution(
        genuine_scores, impostor_scores,
        threshold=results['eer_threshold'],
        title="Score Distribution",
        save_path=os.path.join(args.output_dir, 'score_distribution.png')
    )
    
    logger.info("Evaluation complete!")


if __name__ == "__main__":
    main()
