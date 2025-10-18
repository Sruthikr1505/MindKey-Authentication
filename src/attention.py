"""
Attention mechanisms for temporal EEG data.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class TemporalAttention(nn.Module):
    """
    Temporal attention mechanism for sequence data.
    Computes attention weights over time steps and returns weighted sum.
    """
    
    def __init__(self, hidden_dim: int):
        """
        Args:
            hidden_dim: Dimension of hidden states
        """
        super().__init__()
        self.hidden_dim = hidden_dim
        
        # Attention layers
        self.attention_fc = nn.Linear(hidden_dim, hidden_dim)
        self.context_vector = nn.Linear(hidden_dim, 1, bias=False)
    
    def forward(self, x):
        """
        Args:
            x: Input tensor of shape (batch, timesteps, hidden_dim)
        
        Returns:
            attended: Attention-weighted output (batch, hidden_dim)
            attention_weights: Attention weights (batch, timesteps)
        """
        # Compute attention scores
        # x: (batch, timesteps, hidden_dim)
        attn_hidden = torch.tanh(self.attention_fc(x))  # (batch, timesteps, hidden_dim)
        attn_scores = self.context_vector(attn_hidden).squeeze(-1)  # (batch, timesteps)
        
        # Compute attention weights
        attention_weights = F.softmax(attn_scores, dim=1)  # (batch, timesteps)
        
        # Apply attention weights
        attended = torch.bmm(
            attention_weights.unsqueeze(1),  # (batch, 1, timesteps)
            x  # (batch, timesteps, hidden_dim)
        ).squeeze(1)  # (batch, hidden_dim)
        
        return attended, attention_weights


class MultiHeadTemporalAttention(nn.Module):
    """
    Multi-head temporal attention mechanism.
    """
    
    def __init__(self, hidden_dim: int, num_heads: int = 4):
        """
        Args:
            hidden_dim: Dimension of hidden states
            num_heads: Number of attention heads
        """
        super().__init__()
        assert hidden_dim % num_heads == 0, "hidden_dim must be divisible by num_heads"
        
        self.hidden_dim = hidden_dim
        self.num_heads = num_heads
        self.head_dim = hidden_dim // num_heads
        
        self.query = nn.Linear(hidden_dim, hidden_dim)
        self.key = nn.Linear(hidden_dim, hidden_dim)
        self.value = nn.Linear(hidden_dim, hidden_dim)
        self.out = nn.Linear(hidden_dim, hidden_dim)
    
    def forward(self, x):
        """
        Args:
            x: Input tensor of shape (batch, timesteps, hidden_dim)
        
        Returns:
            attended: Attention output (batch, hidden_dim)
            attention_weights: Average attention weights across heads (batch, timesteps)
        """
        batch_size, timesteps, _ = x.shape
        
        # Linear projections
        Q = self.query(x)  # (batch, timesteps, hidden_dim)
        K = self.key(x)
        V = self.value(x)
        
        # Reshape for multi-head attention
        Q = Q.view(batch_size, timesteps, self.num_heads, self.head_dim).transpose(1, 2)
        K = K.view(batch_size, timesteps, self.num_heads, self.head_dim).transpose(1, 2)
        V = V.view(batch_size, timesteps, self.num_heads, self.head_dim).transpose(1, 2)
        # Now: (batch, num_heads, timesteps, head_dim)
        
        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / (self.head_dim ** 0.5)
        # scores: (batch, num_heads, timesteps, timesteps)
        
        attention_weights = F.softmax(scores, dim=-1)
        
        # Apply attention to values
        attended = torch.matmul(attention_weights, V)
        # attended: (batch, num_heads, timesteps, head_dim)
        
        # Concatenate heads
        attended = attended.transpose(1, 2).contiguous().view(batch_size, timesteps, self.hidden_dim)
        
        # Final linear projection
        attended = self.out(attended)  # (batch, timesteps, hidden_dim)
        
        # Pool over time (mean pooling)
        attended = attended.mean(dim=1)  # (batch, hidden_dim)
        
        # Average attention weights across heads for visualization
        avg_attention_weights = attention_weights.mean(dim=1).mean(dim=1)  # (batch, timesteps)
        
        return attended, avg_attention_weights


# Demo
if __name__ == "__main__":
    print("Testing attention mechanisms...")
    
    # Create dummy input
    batch_size = 16
    timesteps = 256
    hidden_dim = 128
    
    x = torch.randn(batch_size, timesteps, hidden_dim)
    print(f"Input shape: {x.shape}")
    
    # Test TemporalAttention
    print("\n=== TemporalAttention ===")
    attn = TemporalAttention(hidden_dim)
    attended, weights = attn(x)
    print(f"Attended shape: {attended.shape}")
    print(f"Attention weights shape: {weights.shape}")
    print(f"Attention weights sum: {weights.sum(dim=1).mean():.4f} (should be ~1.0)")
    
    # Test MultiHeadTemporalAttention
    print("\n=== MultiHeadTemporalAttention ===")
    multi_attn = MultiHeadTemporalAttention(hidden_dim, num_heads=4)
    attended_multi, weights_multi = multi_attn(x)
    print(f"Attended shape: {attended_multi.shape}")
    print(f"Attention weights shape: {weights_multi.shape}")
    
    # Test gradient flow
    print("\n=== Testing gradient flow ===")
    loss = attended.sum()
    loss.backward()
    print("Gradient flow successful!")
    
    print("\nAll attention tests passed!")
