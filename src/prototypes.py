"""
User prototype computation and management.
"""

import numpy as np
from typing import Dict, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def compute_user_prototypes(
    embeddings_by_user: Dict[int, np.ndarray],
    k: int = 2,
    method: str = 'kmeans'
) -> Dict[int, np.ndarray]:
    """
    Compute k prototypes for each user from their embeddings.
    
    Args:
        embeddings_by_user: Dict mapping user_id -> embeddings array (n_samples, embedding_dim)
        k: Number of prototypes per user
        method: Method for computing prototypes ('kmeans', 'mean', 'median')
    
    Returns:
        prototypes: Dict mapping user_id -> prototypes array (k, embedding_dim)
    """
    from sklearn.cluster import KMeans
    
    prototypes = {}
    
    for user_id, embeddings in embeddings_by_user.items():
        if len(embeddings) < k:
            logger.warning(f"User {user_id} has fewer embeddings ({len(embeddings)}) than k={k}")
            # Pad with mean
            user_prototypes = np.vstack([embeddings, 
                                        np.tile(embeddings.mean(axis=0), (k - len(embeddings), 1))])
        elif method == 'kmeans':
            # K-means clustering
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(embeddings)
            user_prototypes = kmeans.cluster_centers_
        elif method == 'mean':
            # Simple mean (replicate k times)
            mean_emb = embeddings.mean(axis=0, keepdims=True)
            user_prototypes = np.tile(mean_emb, (k, 1))
        elif method == 'median':
            # Median (replicate k times)
            median_emb = np.median(embeddings, axis=0, keepdims=True)
            user_prototypes = np.tile(median_emb, (k, 1))
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Normalize prototypes
        user_prototypes = user_prototypes / (np.linalg.norm(user_prototypes, axis=1, keepdims=True) + 1e-8)
        
        prototypes[user_id] = user_prototypes
        logger.info(f"Computed {k} prototypes for user {user_id}")
    
    return prototypes


def save_prototypes(prototypes: Dict[int, np.ndarray], save_path: str):
    """
    Save prototypes to file.
    
    Args:
        prototypes: Dict mapping user_id -> prototypes array
        save_path: Path to save .npz file
    """
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to saveable format
    save_dict = {f'user_{user_id}': protos for user_id, protos in prototypes.items()}
    
    np.savez(save_path, **save_dict)
    logger.info(f"Saved prototypes for {len(prototypes)} users to {save_path}")


def load_prototypes(load_path: str) -> Dict[int, np.ndarray]:
    """
    Load prototypes from file.
    
    Args:
        load_path: Path to .npz file
    
    Returns:
        prototypes: Dict mapping user_id -> prototypes array
    """
    data = np.load(load_path)
    
    prototypes = {}
    for key in data.files:
        user_id = int(key.split('_')[1])
        prototypes[user_id] = data[key]
    
    logger.info(f"Loaded prototypes for {len(prototypes)} users from {load_path}")
    return prototypes


def get_user_prototype(prototypes: Dict[int, np.ndarray], user_id: int) -> np.ndarray:
    """
    Get prototypes for a specific user.
    
    Args:
        prototypes: Dict mapping user_id -> prototypes array
        user_id: User ID
    
    Returns:
        User prototypes (k, embedding_dim)
    """
    if user_id not in prototypes:
        raise ValueError(f"User {user_id} not found in prototypes")
    
    return prototypes[user_id]


def add_user_prototype(
    prototypes: Dict[int, np.ndarray],
    user_id: int,
    embeddings: np.ndarray,
    k: int = 2
) -> Dict[int, np.ndarray]:
    """
    Add or update prototypes for a user.
    
    Args:
        prototypes: Existing prototypes dict
        user_id: User ID
        embeddings: User embeddings (n_samples, embedding_dim)
        k: Number of prototypes
    
    Returns:
        Updated prototypes dict
    """
    user_prototypes = compute_user_prototypes({user_id: embeddings}, k=k)
    prototypes[user_id] = user_prototypes[user_id]
    
    logger.info(f"Added/updated prototypes for user {user_id}")
    return prototypes


# Demo
if __name__ == "__main__":
    print("Testing prototype functions...")
    
    # Create dummy embeddings
    np.random.seed(42)
    embeddings_by_user = {
        1: np.random.randn(50, 128),
        2: np.random.randn(45, 128),
        3: np.random.randn(60, 128)
    }
    
    # Normalize embeddings
    for user_id in embeddings_by_user:
        embeddings_by_user[user_id] = embeddings_by_user[user_id] / \
            (np.linalg.norm(embeddings_by_user[user_id], axis=1, keepdims=True) + 1e-8)
    
    print(f"Created embeddings for {len(embeddings_by_user)} users")
    
    # Compute prototypes
    prototypes = compute_user_prototypes(embeddings_by_user, k=2, method='kmeans')
    print(f"\nComputed prototypes:")
    for user_id, protos in prototypes.items():
        print(f"User {user_id}: {protos.shape}")
    
    # Save prototypes
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(suffix='.npz', delete=False)
    save_prototypes(prototypes, temp_file.name)
    
    # Load prototypes
    loaded_prototypes = load_prototypes(temp_file.name)
    print(f"\nLoaded prototypes for {len(loaded_prototypes)} users")
    
    # Verify loaded prototypes
    for user_id in prototypes:
        assert np.allclose(prototypes[user_id], loaded_prototypes[user_id])
    print("Prototypes match after save/load!")
    
    # Get specific user prototype
    user_1_protos = get_user_prototype(loaded_prototypes, 1)
    print(f"\nUser 1 prototypes shape: {user_1_protos.shape}")
    
    # Add new user
    new_embeddings = np.random.randn(30, 128)
    new_embeddings = new_embeddings / (np.linalg.norm(new_embeddings, axis=1, keepdims=True) + 1e-8)
    
    updated_prototypes = add_user_prototype(loaded_prototypes, 4, new_embeddings, k=2)
    print(f"\nAdded user 4, total users: {len(updated_prototypes)}")
    
    # Cleanup
    import os
    os.unlink(temp_file.name)
    
    print("\nAll prototype tests passed!")
