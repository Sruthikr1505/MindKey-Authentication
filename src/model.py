"""
BiLSTM Encoder model with optional attention for EEG authentication.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import pytorch_lightning as pl
from typing import Optional, Dict, Any

from attention import TemporalAttention


class BiLSTMEncoder(pl.LightningModule):
    """
    Bidirectional LSTM encoder for EEG signals with optional temporal attention.
    """
    
    def __init__(
        self,
        n_channels: int = 32,
        hidden_size: int = 128,
        num_layers: int = 2,
        embedding_size: int = 128,
        use_attention: bool = True,
        num_classes: Optional[int] = None,
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-4,
        dropout: float = 0.3
    ):
        """
        Args:
            n_channels: Number of EEG channels
            hidden_size: LSTM hidden size
            num_layers: Number of LSTM layers
            embedding_size: Size of output embedding
            use_attention: Whether to use temporal attention
            num_classes: Number of classes for warmup classification (optional)
            learning_rate: Learning rate
            weight_decay: Weight decay
            dropout: Dropout probability
        """
        super().__init__()
        self.save_hyperparameters()
        
        self.n_channels = n_channels
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.embedding_size = embedding_size
        self.use_attention = use_attention
        self.num_classes = num_classes
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        
        # Input projection
        self.input_proj = nn.Linear(n_channels, hidden_size)
        
        # Bidirectional LSTM
        self.lstm = nn.LSTM(
            input_size=hidden_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Attention (optional)
        if use_attention:
            self.attention = TemporalAttention(hidden_size * 2)  # *2 for bidirectional
        
        # Embedding projection
        self.embedding_proj = nn.Sequential(
            nn.Linear(hidden_size * 2, hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size, embedding_size)
        )
        
        # Classification head for warmup (optional)
        if num_classes is not None:
            self.classifier = nn.Linear(embedding_size, num_classes)
        else:
            self.classifier = None
        
        # Training mode flag
        self.warmup_mode = False
        self.metric_loss_fn = None
    
    def forward(self, x, return_attention: bool = False):
        """
        Forward pass.
        
        Args:
            x: Input tensor (batch, n_channels, timesteps)
            return_attention: Whether to return attention weights
        
        Returns:
            embedding: L2-normalized embedding (batch, embedding_size)
            attention_weights: Attention weights if return_attention=True (batch, timesteps)
        """
        batch_size, n_channels, timesteps = x.shape
        
        # Permute to (batch, timesteps, n_channels)
        x = x.permute(0, 2, 1)
        
        # Input projection
        x = self.input_proj(x)  # (batch, timesteps, hidden_size)
        
        # BiLSTM
        lstm_out, _ = self.lstm(x)  # (batch, timesteps, hidden_size * 2)
        
        # Attention or mean pooling
        attention_weights = None
        if self.use_attention:
            pooled, attention_weights = self.attention(lstm_out)
        else:
            pooled = lstm_out.mean(dim=1)  # (batch, hidden_size * 2)
        
        # Embedding projection
        embedding = self.embedding_proj(pooled)  # (batch, embedding_size)
        
        # L2 normalization
        embedding = F.normalize(embedding, p=2, dim=1)
        
        if return_attention:
            return embedding, attention_weights
        return embedding
    
    def training_step(self, batch, batch_idx):
        """Training step supporting both warmup and metric learning."""
        x, labels = batch
        
        # Get embeddings
        embeddings = self(x)
        
        # Warmup mode: classification loss
        if self.warmup_mode and self.classifier is not None:
            logits = self.classifier(embeddings)
            loss = F.cross_entropy(logits, labels)
            
            # Compute accuracy
            preds = logits.argmax(dim=1)
            acc = (preds == labels).float().mean()
            
            self.log('train_loss', loss, prog_bar=True)
            self.log('train_acc', acc, prog_bar=True)
            
            return loss
        
        # Metric learning mode
        elif self.metric_loss_fn is not None:
            loss = self.metric_loss_fn(embeddings, labels)
            self.log('train_metric_loss', loss, prog_bar=True)
            return loss
        
        else:
            raise ValueError("Either warmup_mode or metric_loss_fn must be set")
    
    def validation_step(self, batch, batch_idx):
        """Validation step."""
        x, labels = batch
        embeddings = self(x)
        
        if self.warmup_mode and self.classifier is not None:
            logits = self.classifier(embeddings)
            loss = F.cross_entropy(logits, labels)
            preds = logits.argmax(dim=1)
            acc = (preds == labels).float().mean()
            
            self.log('val_loss', loss, prog_bar=True)
            self.log('val_acc', acc, prog_bar=True)
        
        return embeddings, labels
    
    def configure_optimizers(self):
        """Configure optimizer and scheduler."""
        optimizer = torch.optim.AdamW(
            self.parameters(),
            lr=self.learning_rate,
            weight_decay=self.weight_decay
        )
        
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer,
            mode='min',
            factor=0.5,
            patience=5
        )
        
        return {
            'optimizer': optimizer,
            'lr_scheduler': {
                'scheduler': scheduler,
                'monitor': 'val_loss' if self.warmup_mode else 'train_metric_loss'
            }
        }
    
    def set_warmup_mode(self, warmup: bool):
        """Set warmup mode."""
        self.warmup_mode = warmup
    
    def set_metric_loss(self, loss_fn):
        """Set metric learning loss function."""
        self.metric_loss_fn = loss_fn


# Demo
if __name__ == "__main__":
    print("Testing BiLSTMEncoder...")
    
    # Create model
    model = BiLSTMEncoder(
        n_channels=48,
        hidden_size=128,
        num_layers=2,
        embedding_size=128,
        use_attention=True,
        num_classes=10
    )
    
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Create dummy input
    batch_size = 16
    n_channels = 48
    timesteps = 256
    
    x = torch.randn(batch_size, n_channels, timesteps)
    print(f"\nInput shape: {x.shape}")
    
    # Forward pass
    embedding = model(x)
    print(f"Embedding shape: {embedding.shape}")
    print(f"Embedding norm: {embedding.norm(dim=1).mean():.4f} (should be ~1.0)")
    
    # Forward pass with attention
    embedding, attn_weights = model(x, return_attention=True)
    print(f"\nWith attention:")
    print(f"Embedding shape: {embedding.shape}")
    print(f"Attention weights shape: {attn_weights.shape}")
    
    # Test classification head
    if model.classifier is not None:
        logits = model.classifier(embedding)
        print(f"\nClassification logits shape: {logits.shape}")
    
    # Test gradient flow
    loss = embedding.sum()
    loss.backward()
    print("\nGradient flow successful!")
    
    # Test without attention
    print("\n=== Testing without attention ===")
    model_no_attn = BiLSTMEncoder(
        n_channels=48,
        hidden_size=128,
        num_layers=2,
        embedding_size=128,
        use_attention=False,
        num_classes=10
    )
    
    embedding_no_attn = model_no_attn(x)
    print(f"Embedding shape (no attention): {embedding_no_attn.shape}")
    
    print("\nAll model tests passed!")
