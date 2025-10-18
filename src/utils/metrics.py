"""
Metrics for biometric authentication evaluation.
"""

import numpy as np
from typing import Tuple, List
from scipy.optimize import brentq
from scipy.interpolate import interp1d


def compute_far_frr(
    genuine_scores: np.ndarray,
    impostor_scores: np.ndarray,
    thresholds: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute False Accept Rate (FAR) and False Reject Rate (FRR) at given thresholds.
    
    Args:
        genuine_scores: Similarity scores for genuine attempts (higher = more similar)
        impostor_scores: Similarity scores for impostor attempts
        thresholds: Array of thresholds to evaluate
    
    Returns:
        far: False Accept Rate at each threshold
        frr: False Reject Rate at each threshold
    """
    far = np.zeros(len(thresholds))
    frr = np.zeros(len(thresholds))
    
    for i, threshold in enumerate(thresholds):
        # FAR: proportion of impostors accepted (score >= threshold)
        far[i] = np.mean(impostor_scores >= threshold)
        
        # FRR: proportion of genuine users rejected (score < threshold)
        frr[i] = np.mean(genuine_scores < threshold)
    
    return far, frr


def compute_eer(
    genuine_scores: np.ndarray,
    impostor_scores: np.ndarray
) -> Tuple[float, float]:
    """
    Compute Equal Error Rate (EER) and corresponding threshold.
    
    Args:
        genuine_scores: Similarity scores for genuine attempts
        impostor_scores: Similarity scores for impostor attempts
    
    Returns:
        eer: Equal Error Rate
        eer_threshold: Threshold at EER
    """
    # Create thresholds
    all_scores = np.concatenate([genuine_scores, impostor_scores])
    thresholds = np.linspace(all_scores.min(), all_scores.max(), 1000)
    
    # Compute FAR and FRR
    far, frr = compute_far_frr(genuine_scores, impostor_scores, thresholds)
    
    # Find EER (where FAR == FRR)
    # Interpolate to find exact crossing point
    abs_diff = np.abs(far - frr)
    min_idx = np.argmin(abs_diff)
    
    # Use interpolation for more precise EER
    if min_idx > 0 and min_idx < len(thresholds) - 1:
        # Linear interpolation
        try:
            interp_fn = interp1d([thresholds[min_idx-1], thresholds[min_idx], thresholds[min_idx+1]],
                                [abs_diff[min_idx-1], abs_diff[min_idx], abs_diff[min_idx+1]],
                                kind='quadratic')
            
            # Find zero crossing
            eer_threshold = brentq(
                lambda t: np.interp(t, thresholds, far) - np.interp(t, thresholds, frr),
                thresholds[min_idx-1],
                thresholds[min_idx+1]
            )
            eer = np.interp(eer_threshold, thresholds, far)
        except:
            # Fallback to simple method
            eer_threshold = thresholds[min_idx]
            eer = (far[min_idx] + frr[min_idx]) / 2
    else:
        eer_threshold = thresholds[min_idx]
        eer = (far[min_idx] + frr[min_idx]) / 2
    
    return eer, eer_threshold


def compute_accuracy_at_threshold(
    genuine_scores: np.ndarray,
    impostor_scores: np.ndarray,
    threshold: float
) -> Tuple[float, float, float]:
    """
    Compute accuracy metrics at a given threshold.
    
    Args:
        genuine_scores: Similarity scores for genuine attempts
        impostor_scores: Similarity scores for impostor attempts
        threshold: Decision threshold
    
    Returns:
        accuracy: Overall accuracy
        genuine_accept_rate: True Accept Rate (1 - FRR)
        impostor_reject_rate: True Reject Rate (1 - FAR)
    """
    # Genuine accept rate (TAR)
    genuine_accept_rate = np.mean(genuine_scores >= threshold)
    
    # Impostor reject rate (TRR)
    impostor_reject_rate = np.mean(impostor_scores < threshold)
    
    # Overall accuracy
    n_genuine = len(genuine_scores)
    n_impostor = len(impostor_scores)
    n_total = n_genuine + n_impostor
    
    accuracy = (genuine_accept_rate * n_genuine + impostor_reject_rate * n_impostor) / n_total
    
    return accuracy, genuine_accept_rate, impostor_reject_rate


def compute_roc_curve(
    genuine_scores: np.ndarray,
    impostor_scores: np.ndarray,
    n_points: int = 1000
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute ROC curve (FAR vs TAR).
    
    Args:
        genuine_scores: Similarity scores for genuine attempts
        impostor_scores: Similarity scores for impostor attempts
        n_points: Number of points in ROC curve
    
    Returns:
        far: False Accept Rate
        tar: True Accept Rate (1 - FRR)
        thresholds: Corresponding thresholds
    """
    all_scores = np.concatenate([genuine_scores, impostor_scores])
    thresholds = np.linspace(all_scores.min(), all_scores.max(), n_points)
    
    far, frr = compute_far_frr(genuine_scores, impostor_scores, thresholds)
    tar = 1 - frr
    
    return far, tar, thresholds


def compute_det_curve(
    genuine_scores: np.ndarray,
    impostor_scores: np.ndarray,
    n_points: int = 1000
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute DET curve (FAR vs FRR in normal deviate scale).
    
    Args:
        genuine_scores: Similarity scores for genuine attempts
        impostor_scores: Similarity scores for impostor attempts
        n_points: Number of points in DET curve
    
    Returns:
        far: False Accept Rate
        frr: False Reject Rate
    """
    all_scores = np.concatenate([genuine_scores, impostor_scores])
    thresholds = np.linspace(all_scores.min(), all_scores.max(), n_points)
    
    far, frr = compute_far_frr(genuine_scores, impostor_scores, thresholds)
    
    return far, frr


# Demo
if __name__ == "__main__":
    print("Testing metrics...")
    
    # Create dummy scores
    np.random.seed(42)
    genuine_scores = np.random.normal(0.8, 0.1, 1000)
    impostor_scores = np.random.normal(0.4, 0.15, 1000)
    
    print(f"Genuine scores: mean={genuine_scores.mean():.3f}, std={genuine_scores.std():.3f}")
    print(f"Impostor scores: mean={impostor_scores.mean():.3f}, std={impostor_scores.std():.3f}")
    
    # Compute EER
    eer, eer_threshold = compute_eer(genuine_scores, impostor_scores)
    print(f"\nEER: {eer*100:.2f}%")
    print(f"EER threshold: {eer_threshold:.3f}")
    
    # Compute accuracy at EER threshold
    acc, tar, trr = compute_accuracy_at_threshold(genuine_scores, impostor_scores, eer_threshold)
    print(f"\nAt EER threshold:")
    print(f"Accuracy: {acc*100:.2f}%")
    print(f"True Accept Rate: {tar*100:.2f}%")
    print(f"True Reject Rate: {trr*100:.2f}%")
    
    # Compute ROC curve
    far, tar_roc, thresholds = compute_roc_curve(genuine_scores, impostor_scores, n_points=100)
    print(f"\nROC curve computed with {len(far)} points")
    
    # Compute DET curve
    far_det, frr_det = compute_det_curve(genuine_scores, impostor_scores, n_points=100)
    print(f"DET curve computed with {len(far_det)} points")
    
    print("\nAll metrics tests passed!")
