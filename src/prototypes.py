"""
Prototype Computation and Management
Compute per-user prototype embeddings using k-means clustering.
"""

import numpy as np
from pathlib import Path
from typing import Dict, List
from sklearn.cluster import KMeans
import joblib


def compute_user_prototypes(
    embeddings_by_user: Dict[int, np.ndarray],
    k: int = 2,
    seed: int = 42
) -> Dict[int, np.ndarray]:
    """
    Compute k prototypes per user using k-means clustering.
    
    Args:
        embeddings_by_user: Dict mapping user_id -> (n_samples, embedding_dim) array
        k: Number of prototypes per user
        seed: Random seed
        
    Returns:
        prototypes: Dict mapping user_id -> (k, embedding_dim) prototypes
    """
    prototypes = {}
    
    for user_id, embeddings in embeddings_by_user.items():
        if len(embeddings) < k:
            # If fewer samples than k, use all samples as prototypes
            prototypes[user_id] = embeddings
        else:
            # K-means clustering
            kmeans = KMeans(n_clusters=k, random_state=seed, n_init=10)
            kmeans.fit(embeddings)
            prototypes[user_id] = kmeans.cluster_centers_
    
    return prototypes


def save_prototypes(prototypes: Dict[int, np.ndarray], path: str):
    """
    Save prototypes to disk.
    
    Args:
        prototypes: Dict mapping user_id -> prototypes array
        path: Path to save .npz file
    """
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to dict with string keys for npz
    save_dict = {f'user_{user_id}': protos for user_id, protos in prototypes.items()}
    np.savez(path, **save_dict)
    print(f"Saved prototypes for {len(prototypes)} users to {path}")


def load_prototypes(path: str) -> Dict[int, np.ndarray]:
    """
    Load prototypes from disk.
    
    Args:
        path: Path to .npz file
        
    Returns:
        prototypes: Dict mapping user_id -> prototypes array
    """
    data = np.load(path)
    prototypes = {}
    
    for key in data.files:
        user_id = int(key.split('_')[1])
        prototypes[user_id] = data[key]
    
    print(f"Loaded prototypes for {len(prototypes)} users from {path}")
    return prototypes


def compute_embeddings_by_user(
    embeddings: np.ndarray,
    labels: np.ndarray
) -> Dict[int, np.ndarray]:
    """
    Group embeddings by user label.
    
    Args:
        embeddings: (n_samples, embedding_dim) array
        labels: (n_samples,) array of user IDs
        
    Returns:
        embeddings_by_user: Dict mapping user_id -> embeddings
    """
    embeddings_by_user = {}
    unique_users = np.unique(labels)
    
    for user_id in unique_users:
        mask = labels == user_id
        embeddings_by_user[int(user_id)] = embeddings[mask]
    
    return embeddings_by_user


if __name__ == "__main__":
    # Demo
    print("Testing prototype computation...")
    
    import tempfile
    
    # Create dummy embeddings
    np.random.seed(42)
    n_users = 5
    n_samples_per_user = 100
    embedding_dim = 128
    
    embeddings_by_user = {}
    for user_id in range(n_users):
        # Generate embeddings clustered around user-specific center
        center = np.random.randn(embedding_dim)
        embeddings = center + 0.1 * np.random.randn(n_samples_per_user, embedding_dim)
        embeddings_by_user[user_id] = embeddings
    
    # Compute prototypes
    prototypes = compute_user_prototypes(embeddings_by_user, k=2, seed=42)
    print(f"Computed prototypes for {len(prototypes)} users")
    
    for user_id, protos in prototypes.items():
        print(f"User {user_id}: {protos.shape}")
    
    # Test save/load
    with tempfile.TemporaryDirectory() as tmpdir:
        proto_path = f"{tmpdir}/prototypes.npz"
        save_prototypes(prototypes, proto_path)
        loaded_prototypes = load_prototypes(proto_path)
        
        # Verify
        assert len(loaded_prototypes) == len(prototypes)
        for user_id in prototypes:
            assert np.allclose(prototypes[user_id], loaded_prototypes[user_id])
    
    print("Prototype tests passed!")
