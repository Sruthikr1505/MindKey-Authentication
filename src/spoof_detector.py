"""
Spoof Detection via Embedding Autoencoder
Train autoencoder on genuine embeddings and detect spoofs via reconstruction error.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from pathlib import Path
from tqdm import tqdm


class EmbeddingAutoencoder(nn.Module):
    """
    Simple autoencoder for embedding reconstruction.
    
    Architecture: embedding_dim -> hidden -> latent -> hidden -> embedding_dim
    """
    
    def __init__(self, embedding_dim: int = 128, hidden_dim: int = 64, latent_dim: int = 32):
        super().__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(embedding_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, latent_dim),
            nn.ReLU()
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, embedding_dim)
        )
    
    def forward(self, x):
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed
    
    def reconstruction_error(self, x):
        """Compute MSE reconstruction error"""
        with torch.no_grad():
            reconstructed = self(x)
            error = F.mse_loss(reconstructed, x, reduction='none').mean(dim=1)
        return error


def train_autoencoder(
    embeddings: np.ndarray,
    embedding_dim: int = 128,
    hidden_dim: int = 64,
    latent_dim: int = 32,
    epochs: int = 50,
    batch_size: int = 64,
    lr: float = 1e-3,
    device: str = 'cpu',
    seed: int = 42
) -> EmbeddingAutoencoder:
    """
    Train autoencoder on genuine embeddings.
    
    Args:
        embeddings: (n_samples, embedding_dim) array of genuine embeddings
        embedding_dim: Embedding dimension
        hidden_dim: Hidden layer dimension
        latent_dim: Latent dimension
        epochs: Number of training epochs
        batch_size: Batch size
        lr: Learning rate
        device: Device to train on
        seed: Random seed
        
    Returns:
        model: Trained autoencoder
    """
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    # Create dataset
    embeddings_tensor = torch.from_numpy(embeddings).float()
    dataset = TensorDataset(embeddings_tensor)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # Create model
    model = EmbeddingAutoencoder(embedding_dim, hidden_dim, latent_dim).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    
    # Training loop
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for batch in dataloader:
            x = batch[0].to(device)
            
            # Forward pass
            reconstructed = model(x)
            loss = F.mse_loss(reconstructed, x)
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(dataloader)
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.6f}")
    
    model.eval()
    return model


def compute_reconstruction_errors(
    model: EmbeddingAutoencoder,
    embeddings: np.ndarray,
    device: str = 'cpu'
) -> np.ndarray:
    """
    Compute reconstruction errors for embeddings.
    
    Args:
        model: Trained autoencoder
        embeddings: (n_samples, embedding_dim) array
        device: Device
        
    Returns:
        errors: (n_samples,) reconstruction errors
    """
    model.eval()
    embeddings_tensor = torch.from_numpy(embeddings).float().to(device)
    
    with torch.no_grad():
        errors = model.reconstruction_error(embeddings_tensor)
    
    return errors.cpu().numpy()


def choose_spoof_threshold(
    errors: np.ndarray,
    percentile: float = 99.0
) -> float:
    """
    Choose spoof detection threshold based on percentile of genuine errors.
    
    Args:
        errors: Reconstruction errors on genuine validation set
        percentile: Percentile to use as threshold
        
    Returns:
        threshold: Spoof detection threshold
    """
    threshold = np.percentile(errors, percentile)
    return threshold


def save_spoof_model(model: EmbeddingAutoencoder, path: str):
    """Save spoof detector model"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), path)
    print(f"Saved spoof detector to {path}")


def load_spoof_model(
    path: str,
    embedding_dim: int = 128,
    hidden_dim: int = 64,
    latent_dim: int = 32,
    device: str = 'cpu'
) -> EmbeddingAutoencoder:
    """Load spoof detector model"""
    model = EmbeddingAutoencoder(embedding_dim, hidden_dim, latent_dim).to(device)
    model.load_state_dict(torch.load(path, map_location=device))
    model.eval()
    print(f"Loaded spoof detector from {path}")
    return model


if __name__ == "__main__":
    # Demo
    print("Testing spoof detector...")
    
    import tempfile
    
    # Create dummy embeddings
    np.random.seed(42)
    n_samples = 1000
    embedding_dim = 128
    
    # Genuine embeddings (clustered)
    genuine_embeddings = np.random.randn(n_samples, embedding_dim) * 0.5
    
    # Train autoencoder
    model = train_autoencoder(
        genuine_embeddings,
        embedding_dim=embedding_dim,
        epochs=20,
        batch_size=64,
        device='cpu',
        seed=42
    )
    
    # Compute errors on genuine
    genuine_errors = compute_reconstruction_errors(model, genuine_embeddings, device='cpu')
    print(f"Genuine errors: mean={genuine_errors.mean():.6f}, std={genuine_errors.std():.6f}")
    
    # Choose threshold
    threshold = choose_spoof_threshold(genuine_errors, percentile=99.0)
    print(f"Spoof threshold (99th percentile): {threshold:.6f}")
    
    # Test on spoof (random embeddings)
    spoof_embeddings = np.random.randn(100, embedding_dim) * 2.0
    spoof_errors = compute_reconstruction_errors(model, spoof_embeddings, device='cpu')
    print(f"Spoof errors: mean={spoof_errors.mean():.6f}, std={spoof_errors.std():.6f}")
    
    # Detection rate
    spoof_detected = (spoof_errors > threshold).mean()
    print(f"Spoof detection rate: {spoof_detected:.2%}")
    
    # Test save/load
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = f"{tmpdir}/spoof_model.pth"
        save_spoof_model(model, model_path)
        loaded_model = load_spoof_model(model_path, embedding_dim=embedding_dim, device='cpu')
        
        # Verify
        loaded_errors = compute_reconstruction_errors(loaded_model, genuine_embeddings, device='cpu')
        assert np.allclose(genuine_errors, loaded_errors)
    
    print("Spoof detector tests passed!")
