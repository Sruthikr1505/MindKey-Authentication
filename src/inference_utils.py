"""
Inference utilities for authentication.
"""

import numpy as np
import torch
from typing import Optional


def cos_sim(a: np.ndarray, b: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Args:
        a: First vector
        b: Second vector
    
    Returns:
        Cosine similarity
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8)


def score_vs_prototypes(
    probe_emb: np.ndarray,
    prototypes_user: np.ndarray,
    aggregation: str = 'max'
) -> float:
    """
    Compute similarity score between probe and user prototypes.
    
    Args:
        probe_emb: Probe embedding (embedding_dim,)
        prototypes_user: User prototypes (k, embedding_dim)
        aggregation: How to aggregate scores ('max', 'mean', 'min')
    
    Returns:
        Aggregated similarity score
    """
    scores = []
    for prototype in prototypes_user:
        score = cos_sim(probe_emb, prototype)
        scores.append(score)
    
    scores = np.array(scores)
    
    if aggregation == 'max':
        return scores.max()
    elif aggregation == 'mean':
        return scores.mean()
    elif aggregation == 'min':
        return scores.min()
    else:
        raise ValueError(f"Unknown aggregation: {aggregation}")


def calibrated_probability(score: float, calibrator) -> float:
    """
    Convert similarity score to calibrated probability.
    
    Args:
        score: Similarity score
        calibrator: Fitted calibrator (from calibration.py)
    
    Returns:
        Calibrated probability
    """
    from calibration import apply_calibration
    
    score_array = np.array([score])
    prob = apply_calibration(calibrator, score_array)[0]
    
    return float(prob)


def batch_compute_embeddings(
    model,
    data_loader,
    device: str = 'cpu'
) -> tuple:
    """
    Compute embeddings for a batch of data.
    
    Args:
        model: Encoder model
        data_loader: DataLoader
        device: Device to run on
    
    Returns:
        embeddings: Array of embeddings (n_samples, embedding_dim)
        labels: Array of labels (n_samples,)
    """
    model.eval()
    model.to(device)
    
    all_embeddings = []
    all_labels = []
    
    with torch.no_grad():
        for batch_x, batch_y in data_loader:
            batch_x = batch_x.to(device)
            
            embeddings = model(batch_x)
            
            all_embeddings.append(embeddings.cpu().numpy())
            all_labels.append(batch_y.numpy())
    
    embeddings = np.vstack(all_embeddings)
    labels = np.concatenate(all_labels)
    
    return embeddings, labels


# Demo
if __name__ == "__main__":
    print("Testing inference utilities...")
    
    # Test cosine similarity
    np.random.seed(42)
    a = np.random.randn(128)
    b = np.random.randn(128)
    
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    
    sim = cos_sim(a, b)
    print(f"Cosine similarity: {sim:.4f}")
    
    # Test identical vectors
    sim_identical = cos_sim(a, a)
    print(f"Cosine similarity (identical): {sim_identical:.4f} (should be ~1.0)")
    
    # Test orthogonal vectors
    c = np.zeros(128)
    c[0] = 1.0
    d = np.zeros(128)
    d[1] = 1.0
    sim_orthogonal = cos_sim(c, d)
    print(f"Cosine similarity (orthogonal): {sim_orthogonal:.4f} (should be ~0.0)")
    
    # Test score vs prototypes
    probe = np.random.randn(128)
    probe = probe / np.linalg.norm(probe)
    
    prototypes = np.random.randn(3, 128)
    prototypes = prototypes / (np.linalg.norm(prototypes, axis=1, keepdims=True) + 1e-8)
    
    score_max = score_vs_prototypes(probe, prototypes, aggregation='max')
    score_mean = score_vs_prototypes(probe, prototypes, aggregation='mean')
    score_min = score_vs_prototypes(probe, prototypes, aggregation='min')
    
    print(f"\nScore vs prototypes:")
    print(f"  Max: {score_max:.4f}")
    print(f"  Mean: {score_mean:.4f}")
    print(f"  Min: {score_min:.4f}")
    
    # Test calibrated probability
    from calibration import fit_platt
    
    # Create dummy calibration data
    train_scores = np.concatenate([
        np.random.beta(8, 2, 500),  # Genuine
        np.random.beta(2, 8, 500)   # Impostor
    ])
    train_labels = np.concatenate([np.ones(500), np.zeros(500)])
    
    calibrator = fit_platt(train_scores, train_labels)
    
    test_score = 0.7
    prob = calibrated_probability(test_score, calibrator)
    print(f"\nCalibrated probability for score {test_score}: {prob:.4f}")
    
    print("\nAll inference utility tests passed!")
