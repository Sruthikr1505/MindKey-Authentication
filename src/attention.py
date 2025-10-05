"""
Temporal Attention Module
Implements attention mechanism for temporal pooling of Bi-LSTM outputs.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class TemporalAttention(nn.Module):
    """
    Temporal attention mechanism for sequence pooling.
    
    Computes attention weights over time steps and returns weighted sum.
    """
    
    def __init__(self, hidden_dim: int):
        """
        Args:
            hidden_dim: Hidden dimension of input sequence
        """
        super().__init__()
        self.hidden_dim = hidden_dim
        
        # Attention layers
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 1)
        )
    
    def forward(self, x: torch.Tensor) -> tuple:
        """
        Args:
            x: (batch, seq_len, hidden_dim) tensor
            
        Returns:
            context: (batch, hidden_dim) weighted pooled representation
            weights: (batch, seq_len) attention weights
        """
        # Compute attention scores: (batch, seq_len, 1)
        scores = self.attention(x)
        
        # Normalize to get attention weights: (batch, seq_len, 1)
        weights = F.softmax(scores, dim=1)
        
        # Weighted sum: (batch, hidden_dim)
        context = torch.sum(weights * x, dim=1)
        
        # Return context and weights (squeeze last dim of weights)
        return context, weights.squeeze(-1)


if __name__ == "__main__":
    # Demo
    print("Testing TemporalAttention...")
    
    batch_size = 16
    seq_len = 256
    hidden_dim = 128
    
    # Create dummy input
    x = torch.randn(batch_size, seq_len, hidden_dim)
    
    # Create attention module
    attention = TemporalAttention(hidden_dim)
    
    # Forward pass
    context, weights = attention(x)
    
    print(f"Input shape: {x.shape}")
    print(f"Context shape: {context.shape}")
    print(f"Weights shape: {weights.shape}")
    print(f"Weights sum (should be ~1.0): {weights.sum(dim=1).mean().item():.4f}")
    
    # Check gradients
    loss = context.sum()
    loss.backward()
    
    print("Attention module tests passed!")
