"""
Score Calibration Module
Calibrate similarity scores to probabilities using Platt scaling or isotonic regression.
"""

import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
import joblib


def fit_platt(
    similarities: np.ndarray,
    labels: np.ndarray,
    seed: int = 42
) -> LogisticRegression:
    """
    Fit Platt scaling (logistic regression) to calibrate scores.
    
    Args:
        similarities: (n_samples,) similarity scores
        labels: (n_samples,) binary labels (1=genuine, 0=impostor)
        seed: Random seed
        
    Returns:
        calibrator: Fitted LogisticRegression model
    """
    calibrator = LogisticRegression(random_state=seed, max_iter=1000)
    calibrator.fit(similarities.reshape(-1, 1), labels)
    return calibrator


def fit_isotonic(
    similarities: np.ndarray,
    labels: np.ndarray
) -> IsotonicRegression:
    """
    Fit isotonic regression for calibration.
    
    Args:
        similarities: (n_samples,) similarity scores
        labels: (n_samples,) binary labels (1=genuine, 0=impostor)
        
    Returns:
        calibrator: Fitted IsotonicRegression model
    """
    calibrator = IsotonicRegression(out_of_bounds='clip')
    calibrator.fit(similarities, labels)
    return calibrator


def save_calibrator(calibrator, path: str):
    """
    Save calibrator to disk.
    
    Args:
        calibrator: Fitted calibrator model
        path: Path to save .pkl file
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(calibrator, path)
    print(f"Saved calibrator to {path}")


def load_calibrator(path: str):
    """
    Load calibrator from disk.
    
    Args:
        path: Path to .pkl file
        
    Returns:
        calibrator: Loaded calibrator model
    """
    calibrator = joblib.load(path)
    print(f"Loaded calibrator from {path}")
    return calibrator


def calibrate_scores(
    calibrator,
    similarities: np.ndarray
) -> np.ndarray:
    """
    Apply calibrator to convert similarities to probabilities.
    
    Args:
        calibrator: Fitted calibrator (LogisticRegression or IsotonicRegression)
        similarities: (n_samples,) similarity scores
        
    Returns:
        probabilities: (n_samples,) calibrated probabilities
    """
    if isinstance(calibrator, LogisticRegression):
        probs = calibrator.predict_proba(similarities.reshape(-1, 1))[:, 1]
    elif isinstance(calibrator, IsotonicRegression):
        probs = calibrator.predict(similarities)
    else:
        raise ValueError(f"Unknown calibrator type: {type(calibrator)}")
    
    return probs


if __name__ == "__main__":
    # Demo
    print("Testing calibration...")
    
    import tempfile
    
    # Create dummy scores
    np.random.seed(42)
    genuine_scores = np.random.beta(8, 2, 500)
    impostor_scores = np.random.beta(2, 8, 500)
    
    similarities = np.concatenate([genuine_scores, impostor_scores])
    labels = np.concatenate([np.ones(500), np.zeros(500)])
    
    # Test Platt scaling
    platt_calibrator = fit_platt(similarities, labels, seed=42)
    platt_probs = calibrate_scores(platt_calibrator, similarities)
    print(f"Platt calibration: mean prob for genuine = {platt_probs[:500].mean():.3f}, impostor = {platt_probs[500:].mean():.3f}")
    
    # Test isotonic regression
    isotonic_calibrator = fit_isotonic(similarities, labels)
    isotonic_probs = calibrate_scores(isotonic_calibrator, similarities)
    print(f"Isotonic calibration: mean prob for genuine = {isotonic_probs[:500].mean():.3f}, impostor = {isotonic_probs[500:].mean():.3f}")
    
    # Test save/load
    with tempfile.TemporaryDirectory() as tmpdir:
        platt_path = f"{tmpdir}/platt.pkl"
        save_calibrator(platt_calibrator, platt_path)
        loaded_calibrator = load_calibrator(platt_path)
        
        # Verify
        loaded_probs = calibrate_scores(loaded_calibrator, similarities)
        assert np.allclose(platt_probs, loaded_probs)
    
    print("Calibration tests passed!")
