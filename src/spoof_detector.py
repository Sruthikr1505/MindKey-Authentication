"""
Embedding autoencoder for spoof/presentation attack detection.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from typing import Tuple, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class EmbeddingAutoencoder(nn.Module):
    """
    Autoencoder for embedding reconstruction.
    High reconstruction error indicates potential spoof/anomaly.
    """
    
    def __init__(self, emb_dim: int = 128, hidden_dim: int = 64, latent_dim: int = 32):
        """
        Args:
            emb_dim: Embedding dimension
            hidden_dim: Hidden layer dimension
            latent_dim: Latent dimension
        """
        super().__init__()
        
        self.emb_dim = emb_dim
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(emb_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim),
            nn.ReLU()
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, emb_dim)
        )
    
    def forward(self, x):
        """
        Forward pass.
        
        Args:
            x: Input embeddings (batch, emb_dim)
        
        Returns:
            reconstructed: Reconstructed embeddings (batch, emb_dim)
        """
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed
    
    def get_reconstruction_error(self, x):
        """
        Compute reconstruction error.
        
        Args:
            x: Input embeddings (batch, emb_dim)
        
        Returns:
            errors: Reconstruction errors (batch,)
        """
        with torch.no_grad():
            reconstructed = self(x)
            errors = torch.mean((x - reconstructed) ** 2, dim=1)
        return errors


def train_autoencoder(
    embeddings: np.ndarray,
    emb_dim: int = 128,
    hidden_dim: int = 64,
    latent_dim: int = 32,
    epochs: int = 50,
    batch_size: int = 64,
    lr: float = 1e-3,
    device: str = 'cpu',
    val_split: float = 0.2
) -> Tuple[EmbeddingAutoencoder, np.ndarray]:
    """
    Train autoencoder on genuine embeddings.
    
    Args:
        embeddings: Training embeddings (n_samples, emb_dim)
        emb_dim: Embedding dimension
        hidden_dim: Hidden dimension
        latent_dim: Latent dimension
        epochs: Number of training epochs
        batch_size: Batch size
        lr: Learning rate
        device: Device to train on
        val_split: Validation split ratio
    
    Returns:
        model: Trained autoencoder
        val_errors: Validation reconstruction errors
    """
    # Create model
    model = EmbeddingAutoencoder(emb_dim, hidden_dim, latent_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    # Split train/val
    n_val = int(len(embeddings) * val_split)
    indices = np.random.permutation(len(embeddings))
    train_indices = indices[n_val:]
    val_indices = indices[:n_val]
    
    train_embeddings = embeddings[train_indices]
    val_embeddings = embeddings[val_indices]
    
    # Create dataloaders
    train_dataset = TensorDataset(torch.FloatTensor(train_embeddings))
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    val_tensor = torch.FloatTensor(val_embeddings).to(device)
    
    logger.info(f"Training autoencoder on {len(train_embeddings)} samples, "
               f"validating on {len(val_embeddings)} samples")
    
    # Training loop
    model.train()
    for epoch in range(epochs):
        train_loss = 0.0
        for batch in train_loader:
            x = batch[0].to(device)
            
            # Forward pass
            reconstructed = model(x)
            loss = F.mse_loss(reconstructed, x)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        
        # Validation
        model.eval()
        with torch.no_grad():
            val_reconstructed = model(val_tensor)
            val_loss = F.mse_loss(val_reconstructed, val_tensor).item()
        model.train()
        
        if (epoch + 1) % 10 == 0:
            logger.info(f"Epoch {epoch+1}/{epochs}: train_loss={train_loss:.6f}, val_loss={val_loss:.6f}")
    
    # Compute validation errors
    model.eval()
    val_errors = model.get_reconstruction_error(val_tensor).cpu().numpy()
    
    logger.info(f"Training complete. Val error: mean={val_errors.mean():.6f}, "
               f"std={val_errors.std():.6f}")
    
    return model, val_errors


def compute_spoof_threshold(
    val_errors: np.ndarray,
    percentile: float = 99.0
) -> float:
    """
    Compute spoof detection threshold from validation errors.
    
    Args:
        val_errors: Validation reconstruction errors
        percentile: Percentile for threshold (e.g., 99 = 99th percentile)
    
    Returns:
        threshold: Spoof detection threshold
    """
    threshold = np.percentile(val_errors, percentile)
    logger.info(f"Spoof threshold at {percentile}th percentile: {threshold:.6f}")
    return threshold


def save_spoof_model(model: EmbeddingAutoencoder, threshold: float, save_path: str):
    """
    Save spoof detector model and threshold.
    
    Args:
        model: Trained autoencoder
        threshold: Spoof detection threshold
        save_path: Path to save .pth file
    """
    Path(save_path).parent.mkdir(parents=True, exist_ok=True)
    
    torch.save({
        'model_state_dict': model.state_dict(),
        'threshold': threshold,
        'emb_dim': model.emb_dim,
        'hidden_dim': model.hidden_dim,
        'latent_dim': model.latent_dim
    }, save_path)
    
    logger.info(f"Saved spoof detector to {save_path}")


def load_spoof_model(load_path: str, device: str = 'cpu', weights_only: bool = False) -> Tuple[EmbeddingAutoencoder, float]:
    """
    Load spoof detector model and threshold.
    
    Args:
        load_path: Path to .pth file
        device: Device to load model on
        weights_only: Whether to load only weights (safer but may fail with numpy objects)
    
    Returns:
        model: Loaded autoencoder
        threshold: Spoof detection threshold
    """
    checkpoint = torch.load(load_path, map_location=device, weights_only=weights_only)
    
    model = EmbeddingAutoencoder(
        emb_dim=checkpoint['emb_dim'],
        hidden_dim=checkpoint['hidden_dim'],
        latent_dim=checkpoint['latent_dim']
    ).to(device)
    
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    threshold = checkpoint['threshold']
    
    logger.info(f"Loaded spoof detector from {load_path}")
    return model, threshold


# Demo
if __name__ == "__main__":
    print("Testing spoof detector...")
    
    # Create dummy embeddings
    np.random.seed(42)
    torch.manual_seed(42)
    
    genuine_embeddings = np.random.randn(1000, 128)
    genuine_embeddings = genuine_embeddings / (np.linalg.norm(genuine_embeddings, axis=1, keepdims=True) + 1e-8)
    
    print(f"Created {len(genuine_embeddings)} genuine embeddings")
    
    # Train autoencoder
    model, val_errors = train_autoencoder(
        genuine_embeddings,
        emb_dim=128,
        epochs=20,
        batch_size=64,
        device='cpu'
    )
    
    print(f"\nValidation errors: mean={val_errors.mean():.6f}, std={val_errors.std():.6f}")
    
    # Compute threshold
    threshold = compute_spoof_threshold(val_errors, percentile=99)
    
    # Test on genuine samples
    test_genuine = torch.FloatTensor(genuine_embeddings[:100])
    genuine_errors = model.get_reconstruction_error(test_genuine).numpy()
    genuine_spoof_rate = (genuine_errors > threshold).mean()
    print(f"\nGenuine spoof rate: {genuine_spoof_rate*100:.2f}%")
    
    # Test on anomalous samples (random noise)
    anomalous_embeddings = np.random.randn(100, 128) * 2  # Higher variance
    anomalous_embeddings = anomalous_embeddings / (np.linalg.norm(anomalous_embeddings, axis=1, keepdims=True) + 1e-8)
    test_anomalous = torch.FloatTensor(anomalous_embeddings)
    anomalous_errors = model.get_reconstruction_error(test_anomalous).numpy()
    anomalous_detect_rate = (anomalous_errors > threshold).mean()
    print(f"Anomalous detection rate: {anomalous_detect_rate*100:.2f}%")
    
    # Save and load
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(suffix='.pth', delete=False)
    
    save_spoof_model(model, threshold, temp_file.name)
    loaded_model, loaded_threshold = load_spoof_model(temp_file.name)
    
    # Verify
    assert loaded_threshold == threshold
    loaded_errors = loaded_model.get_reconstruction_error(test_genuine).numpy()
    assert np.allclose(genuine_errors, loaded_errors)
    print("\nSpoof model save/load successful!")
    
    # Cleanup
    import os
    os.unlink(temp_file.name)
    
    print("\nAll spoof detector tests passed!")
