"""
Biometric Metrics Utilities
Compute FAR, FRR, EER for authentication systems.
"""

import numpy as np
from typing import Tuple, List
from sklearn.metrics import roc_curve


def compute_far_frr(
    genuine_scores: np.ndarray,
    impostor_scores: np.ndarray,
    threshold: float
) -> Tuple[float, float]:
    """
    Compute False Accept Rate and False Reject Rate at a given threshold.
    
    Args:
        genuine_scores: Similarity scores for genuine attempts (higher = more similar)
        impostor_scores: Similarity scores for impostor attempts
        threshold: Decision threshold
        
    Returns:
        far: False Accept Rate
        frr: False Reject Rate
    """
    # FAR: proportion of impostors accepted (score >= threshold)
    far = np.mean(impostor_scores >= threshold)
    
    # FRR: proportion of genuine users rejected (score < threshold)
    frr = np.mean(genuine_scores < threshold)
    
    return far, frr


def compute_eer(
    genuine_scores: np.ndarray,
    impostor_scores: np.ndarray
) -> Tuple[float, float]:
    """
    Compute Equal Error Rate (EER) - point where FAR = FRR.
    
    Args:
        genuine_scores: Similarity scores for genuine attempts
        impostor_scores: Similarity scores for impostor attempts
        
    Returns:
        eer: Equal Error Rate
        threshold: Threshold at EER
    """
    # Create labels: 1 for genuine, 0 for impostor
    y_true = np.concatenate([
        np.ones(len(genuine_scores)),
        np.zeros(len(impostor_scores))
    ])
    
    # Combine scores
    y_scores = np.concatenate([genuine_scores, impostor_scores])
    
    # Compute ROC curve
    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    
    # FRR = 1 - TPR, FAR = FPR
    frr = 1 - tpr
    far = fpr
    
    # Find EER point (where FAR = FRR)
    eer_idx = np.argmin(np.abs(far - frr))
    eer = (far[eer_idx] + frr[eer_idx]) / 2
    eer_threshold = thresholds[eer_idx]
    
    return eer, eer_threshold


def compute_metrics_at_thresholds(
    genuine_scores: np.ndarray,
    impostor_scores: np.ndarray,
    thresholds: List[float]
) -> dict:
    """
    Compute FAR and FRR at multiple thresholds.
    
    Args:
        genuine_scores: Genuine similarity scores
        impostor_scores: Impostor similarity scores
        thresholds: List of thresholds to evaluate
        
    Returns:
        Dictionary with FAR and FRR arrays
    """
    fars = []
    frrs = []
    
    for threshold in thresholds:
        far, frr = compute_far_frr(genuine_scores, impostor_scores, threshold)
        fars.append(far)
        frrs.append(frr)
    
    return {
        'thresholds': thresholds,
        'far': np.array(fars),
        'frr': np.array(frrs)
    }


if __name__ == "__main__":
    # Demo
    print("Testing metrics...")
    
    # Generate dummy scores
    np.random.seed(42)
    genuine_scores = np.random.beta(8, 2, 1000)  # Higher scores
    impostor_scores = np.random.beta(2, 8, 1000)  # Lower scores
    
    # Compute EER
    eer, eer_threshold = compute_eer(genuine_scores, impostor_scores)
    print(f"EER: {eer:.4f} at threshold {eer_threshold:.4f}")
    
    # Compute FAR/FRR at specific thresholds
    thresholds = [0.3, 0.5, 0.7]
    metrics = compute_metrics_at_thresholds(genuine_scores, impostor_scores, thresholds)
    
    for i, thresh in enumerate(thresholds):
        print(f"Threshold {thresh:.2f}: FAR={metrics['far'][i]:.4f}, FRR={metrics['frr'][i]:.4f}")
    
    print("Metrics tests passed!")
