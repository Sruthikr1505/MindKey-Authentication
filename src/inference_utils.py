"""
Inference Utilities
Helper functions for computing similarity scores and making authentication decisions.
"""

import numpy as np
import torch
from typing import Optional


def cos_sim(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Args:
        a: Vector 1
        b: Vector 2
        
    Returns:
        similarity: Cosine similarity in [-1, 1]
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)


def score_vs_prototypes(
    probe_embedding: np.ndarray,
    prototypes_user: np.ndarray,
    aggregation: str = 'max'
) -> float:
    """
    Compute similarity score between probe and user prototypes.
    
    Args:
        probe_embedding: (embedding_dim,) probe embedding
        prototypes_user: (k, embedding_dim) user prototypes
        aggregation: How to aggregate scores ('max', 'mean', 'min')
        
    Returns:
        score: Aggregated similarity score
    """
    similarities = []
    for prototype in prototypes_user:
        sim = cos_sim(probe_embedding, prototype)
        similarities.append(sim)
    
    similarities = np.array(similarities)
    
    if aggregation == 'max':
        return similarities.max()
    elif aggregation == 'mean':
        return similarities.mean()
    elif aggregation == 'min':
        return similarities.min()
    else:
        raise ValueError(f"Unknown aggregation: {aggregation}")


def calibrated_probability(
    score: float,
    calibrator
) -> float:
    """
    Convert similarity score to calibrated probability.
    
    Args:
        score: Raw similarity score
        calibrator: Fitted calibrator (from calibration.py)
        
    Returns:
        probability: Calibrated probability in [0, 1]
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.isotonic import IsotonicRegression
    
    score_array = np.array([[score]])
    
    if isinstance(calibrator, LogisticRegression):
        prob = calibrator.predict_proba(score_array)[0, 1]
    elif isinstance(calibrator, IsotonicRegression):
        prob = calibrator.predict([score])[0]
    else:
        # No calibrator, return score clipped to [0, 1]
        prob = np.clip(score, 0, 1)
    
    return float(prob)


def make_decision(
    score: float,
    threshold: float,
    calibrator = None,
    spoof_error: Optional[float] = None,
    spoof_threshold: Optional[float] = None
) -> dict:
    """
    Make authentication decision based on score and optional spoof detection.
    
    Args:
        score: Similarity score
        threshold: Decision threshold
        calibrator: Optional calibrator
        spoof_error: Optional reconstruction error for spoof detection
        spoof_threshold: Optional spoof detection threshold
        
    Returns:
        result: Dict with 'authenticated', 'score', 'probability', 'is_spoof'
    """
    # Check spoof
    is_spoof = False
    if spoof_error is not None and spoof_threshold is not None:
        is_spoof = spoof_error > spoof_threshold
    
    # Compute probability
    if calibrator is not None:
        probability = calibrated_probability(score, calibrator)
    else:
        probability = score
    
    # Make decision
    authenticated = (not is_spoof) and (score >= threshold)
    
    return {
        'authenticated': authenticated,
        'score': float(score),
        'probability': float(probability),
        'is_spoof': is_spoof,
        'spoof_error': float(spoof_error) if spoof_error is not None else None
    }


if __name__ == "__main__":
    # Demo
    print("Testing inference utilities...")
    
    # Test cosine similarity
    a = np.array([1, 0, 0])
    b = np.array([0, 1, 0])
    c = np.array([1, 0, 0])
    
    print(f"cos_sim(a, b) = {cos_sim(a, b):.3f} (should be ~0)")
    print(f"cos_sim(a, c) = {cos_sim(a, c):.3f} (should be ~1)")
    
    # Test prototype scoring
    probe = np.random.randn(128)
    probe = probe / np.linalg.norm(probe)
    
    prototypes = np.random.randn(3, 128)
    prototypes = prototypes / np.linalg.norm(prototypes, axis=1, keepdims=True)
    
    score_max = score_vs_prototypes(probe, prototypes, aggregation='max')
    score_mean = score_vs_prototypes(probe, prototypes, aggregation='mean')
    
    print(f"Score vs prototypes (max): {score_max:.3f}")
    print(f"Score vs prototypes (mean): {score_mean:.3f}")
    
    # Test decision making
    decision = make_decision(
        score=0.85,
        threshold=0.7,
        calibrator=None,
        spoof_error=0.01,
        spoof_threshold=0.05
    )
    
    print(f"Decision: {decision}")
    
    print("Inference utilities tests passed!")
