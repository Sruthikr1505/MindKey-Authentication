"""
Score calibration for converting similarity scores to probabilities.
"""

import numpy as np
import joblib
from typing import Optional, Tuple
from pathlib import Path
import logging
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression

logger = logging.getLogger(__name__)


def fit_platt(
    similarities: np.ndarray,
    labels: np.ndarray
) -> LogisticRegression:
    """
    Fit Platt scaling (logistic regression) for score calibration.
    
    Args:
        similarities: Similarity scores (n_samples,)
        labels: Binary labels (1 for genuine, 0 for impostor)
    
    Returns:
        Fitted LogisticRegression model
    """
    # Reshape for sklearn
    X = similarities.reshape(-1, 1)
    y = labels
    
    # Fit logistic regression
    calibrator = LogisticRegression(random_state=42, max_iter=1000)
    calibrator.fit(X, y)
    
    logger.info(f"Fitted Platt scaling with {len(similarities)} samples")
    return calibrator


def fit_isotonic(
    similarities: np.ndarray,
    labels: np.ndarray
) -> IsotonicRegression:
    """
    Fit isotonic regression for score calibration.
    
    Args:
        similarities: Similarity scores (n_samples,)
        labels: Binary labels (1 for genuine, 0 for impostor)
    
    Returns:
        Fitted IsotonicRegression model
    """
    calibrator = IsotonicRegression(out_of_bounds='clip')
    calibrator.fit(similarities, labels)
    
    logger.info(f"Fitted isotonic regression with {len(similarities)} samples")
    return calibrator


def apply_calibration(
    calibrator,
    similarities: np.ndarray
) -> np.ndarray:
    """
    Apply calibration to similarity scores.
    
    Args:
        calibrator: Fitted calibrator (LogisticRegression or IsotonicRegression)
        similarities: Similarity scores (n_samples,)
    
    Returns:
        Calibrated probabilities (n_samples,)
    """
    if isinstance(calibrator, LogisticRegression):
        X = similarities.reshape(-1, 1)
        probs = calibrator.predict_proba(X)[:, 1]
    elif isinstance(calibrator, IsotonicRegression):
        probs = calibrator.predict(similarities)
    else:
        raise ValueError(f"Unknown calibrator type: {type(calibrator)}")
    
    return probs


def save_calibrator(calibrator, save_path: str):
    """
    Save calibrator to file.
    
    Args:
        calibrator: Fitted calibrator
        save_path: Path to save .pkl file
    """
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(calibrator, save_path)
    logger.info(f"Saved calibrator to {save_path}")


def load_calibrator(load_path: str):
    """
    Load calibrator from file.
    
    Args:
        load_path: Path to .pkl file
    
    Returns:
        Loaded calibrator
    """
    calibrator = joblib.load(load_path)
    logger.info(f"Loaded calibrator from {load_path}")
    return calibrator


def evaluate_calibration(
    calibrator,
    similarities: np.ndarray,
    labels: np.ndarray,
    n_bins: int = 10
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Evaluate calibration quality using reliability diagram.
    
    Args:
        calibrator: Fitted calibrator
        similarities: Similarity scores
        labels: True binary labels
        n_bins: Number of bins for reliability diagram
    
    Returns:
        bin_centers: Center of each probability bin
        bin_accuracies: Actual accuracy in each bin
    """
    # Get calibrated probabilities
    probs = apply_calibration(calibrator, similarities)
    
    # Create bins
    bins = np.linspace(0, 1, n_bins + 1)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    bin_accuracies = np.zeros(n_bins)
    
    # Compute accuracy in each bin
    for i in range(n_bins):
        mask = (probs >= bins[i]) & (probs < bins[i+1])
        if mask.sum() > 0:
            bin_accuracies[i] = labels[mask].mean()
        else:
            bin_accuracies[i] = np.nan
    
    return bin_centers, bin_accuracies


# Demo
if __name__ == "__main__":
    print("Testing calibration functions...")
    
    # Create dummy data
    np.random.seed(42)
    
    # Genuine scores (higher similarity)
    genuine_scores = np.random.beta(8, 2, 500)
    genuine_labels = np.ones(500)
    
    # Impostor scores (lower similarity)
    impostor_scores = np.random.beta(2, 8, 500)
    impostor_labels = np.zeros(500)
    
    # Combine
    similarities = np.concatenate([genuine_scores, impostor_scores])
    labels = np.concatenate([genuine_labels, impostor_labels])
    
    # Shuffle
    indices = np.random.permutation(len(similarities))
    similarities = similarities[indices]
    labels = labels[indices]
    
    print(f"Created {len(similarities)} samples")
    print(f"Genuine: {genuine_labels.sum()}, Impostor: {impostor_labels.sum()}")
    
    # Split train/test
    n_train = 800
    train_sim, test_sim = similarities[:n_train], similarities[n_train:]
    train_labels, test_labels = labels[:n_train], labels[n_train:]
    
    # Fit Platt scaling
    print("\n=== Platt Scaling ===")
    platt_calibrator = fit_platt(train_sim, train_labels)
    platt_probs = apply_calibration(platt_calibrator, test_sim)
    print(f"Test probabilities: min={platt_probs.min():.3f}, max={platt_probs.max():.3f}")
    
    # Fit isotonic regression
    print("\n=== Isotonic Regression ===")
    isotonic_calibrator = fit_isotonic(train_sim, train_labels)
    isotonic_probs = apply_calibration(isotonic_calibrator, test_sim)
    print(f"Test probabilities: min={isotonic_probs.min():.3f}, max={isotonic_probs.max():.3f}")
    
    # Save and load
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(suffix='.pkl', delete=False)
    
    save_calibrator(platt_calibrator, temp_file.name)
    loaded_calibrator = load_calibrator(temp_file.name)
    
    # Verify
    loaded_probs = apply_calibration(loaded_calibrator, test_sim)
    assert np.allclose(platt_probs, loaded_probs)
    print("\nCalibrator save/load successful!")
    
    # Evaluate calibration
    bin_centers, bin_accs = evaluate_calibration(platt_calibrator, test_sim, test_labels, n_bins=10)
    print(f"\nCalibration evaluation:")
    print(f"Bin centers: {bin_centers}")
    print(f"Bin accuracies: {bin_accs}")
    
    # Cleanup
    import os
    os.unlink(temp_file.name)
    
    print("\nAll calibration tests passed!")
