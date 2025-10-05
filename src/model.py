"""
BiLSTM Encoder Model
PyTorch Lightning module for EEG authentication with optional temporal attention.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import pytorch_lightning as pl
from typing import Optional, Dict, Any

from attention import TemporalAttention


class BiLSTMEncoder(pl.LightningModule):
    """
    Bi-directional LSTM encoder for EEG embeddings.
    
    Architecture:
    - Input: (batch, channels, timesteps)
    - Linear projection per timestep
    - Bi-LSTM (2 layers)
    - Optional temporal attention
    - FC layer to embedding
    - L2 normalization
    """
    
    def __init__(
        self,
        n_channels: int = 32,
        hidden_size: int = 128,
        embedding_size: int = 128,
        num_layers: int = 2,
        use_attention: bool = True,
        num_classes: Optional[int] = None,
        lr: float = 1e-3,
        weight_decay: float = 1e-4
    ):
        """
        Args:
            n_channels: Number of EEG channels
            hidden_size: LSTM hidden size
            embedding_size: Final embedding dimension
            num_layers: Number of LSTM layers
            use_attention: Whether to use temporal attention
            num_classes: Number of classes for warmup classification (optional)
            lr: Learning rate
            weight_decay: Weight decay for optimizer
        """
        super().__init__()
        self.save_hyperparameters()
        
        self.n_channels = n_channels
        self.hidden_size = hidden_size
        self.embedding_size = embedding_size
        self.num_layers = num_layers
        self.use_attention = use_attention
        self.num_classes = num_classes
        self.lr = lr
        self.weight_decay = weight_decay
        
        # Linear projection per timestep
        self.input_proj = nn.Linear(n_channels, hidden_size)
        
        # Bi-LSTM
        self.lstm = nn.LSTM(
            input_size=hidden_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=0.3 if num_layers > 1 else 0.0
        )
        
        # Attention or pooling
        if use_attention:
            self.attention = TemporalAttention(hidden_size * 2)  # *2 for bidirectional
        else:
            self.attention = None
        
        # Embedding layer
        self.embedding_fc = nn.Sequential(
            nn.Linear(hidden_size * 2, embedding_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(embedding_size, embedding_size)
        )
        
        # Optional classification head for warmup
        if num_classes is not None:
            self.classifier = nn.Linear(embedding_size, num_classes)
        else:
            self.classifier = None
        
        # Training mode flag
        self.training_mode = 'warmup'  # 'warmup' or 'metric'
        self.metric_loss_fn = None
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass to compute embeddings.
        
        Args:
            x: (batch, channels, timesteps) tensor
            
        Returns:
            embeddings: (batch, embedding_size) L2-normalized embeddings
        """
        batch_size, n_channels, timesteps = x.shape
        
        # Permute to (batch, timesteps, channels)
        x = x.permute(0, 2, 1)
        
        # Project: (batch, timesteps, hidden_size)
        x = self.input_proj(x)
        
        # Bi-LSTM: (batch, timesteps, hidden_size * 2)
        lstm_out, _ = self.lstm(x)
        
        # Pooling
        if self.use_attention:
            # Attention pooling: (batch, hidden_size * 2)
            pooled, _ = self.attention(lstm_out)
        else:
            # Mean pooling: (batch, hidden_size * 2)
            pooled = lstm_out.mean(dim=1)
        
        # Embedding: (batch, embedding_size)
        embedding = self.embedding_fc(pooled)
        
        # L2 normalization
        embedding = F.normalize(embedding, p=2, dim=1)
        
        return embedding
    
    def training_step(self, batch, batch_idx):
        x, y = batch
        embeddings = self(x)
        
        if self.training_mode == 'warmup':
            # Classification loss
            if self.classifier is None:
                raise ValueError("Classifier head not initialized for warmup training")
            logits = self.classifier(embeddings)
            loss = F.cross_entropy(logits, y)
            
            # Accuracy
            preds = logits.argmax(dim=1)
            acc = (preds == y).float().mean()
            
            self.log('train_loss', loss, prog_bar=True)
            self.log('train_acc', acc, prog_bar=True)
            
        elif self.training_mode == 'metric':
            # Metric learning loss (set externally)
            if self.metric_loss_fn is None:
                raise ValueError("Metric loss function not set")
            loss = self.metric_loss_fn(embeddings, y)
            self.log('train_metric_loss', loss, prog_bar=True)
        
        else:
            raise ValueError(f"Unknown training mode: {self.training_mode}")
        
        return loss
    
    def validation_step(self, batch, batch_idx):
        x, y = batch
        embeddings = self(x)
        
        if self.training_mode == 'warmup':
            logits = self.classifier(embeddings)
            loss = F.cross_entropy(logits, y)
            preds = logits.argmax(dim=1)
            acc = (preds == y).float().mean()
            
            self.log('val_loss', loss, prog_bar=True)
            self.log('val_acc', acc, prog_bar=True)
        
        return embeddings, y
    
    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(
            self.parameters(),
            lr=self.lr,
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
                'monitor': 'val_loss' if self.training_mode == 'warmup' else 'train_metric_loss'
            }
        }
    
    def set_training_mode(self, mode: str):
        """Set training mode: 'warmup' or 'metric'"""
        self.training_mode = mode
    
    def set_metric_loss(self, loss_fn):
        """Set metric learning loss function"""
        self.metric_loss_fn = loss_fn


if __name__ == "__main__":
    # Demo
    print("Testing BiLSTMEncoder...")
    
    batch_size = 16
    n_channels = 32
    timesteps = 256
    num_classes = 10
    
    # Create dummy input
    x = torch.randn(batch_size, n_channels, timesteps)
    y = torch.randint(0, num_classes, (batch_size,))
    
    # Test with attention
    model_attn = BiLSTMEncoder(
        n_channels=n_channels,
        hidden_size=128,
        embedding_size=128,
        num_layers=2,
        use_attention=True,
        num_classes=num_classes
    )
    
    embeddings = model_attn(x)
    print(f"Input shape: {x.shape}")
    print(f"Embeddings shape (with attention): {embeddings.shape}")
    print(f"Embeddings norm: {embeddings.norm(dim=1).mean().item():.4f} (should be ~1.0)")
    
    # Test without attention
    model_no_attn = BiLSTMEncoder(
        n_channels=n_channels,
        hidden_size=128,
        embedding_size=128,
        num_layers=2,
        use_attention=False,
        num_classes=num_classes
    )
    
    embeddings_no_attn = model_no_attn(x)
    print(f"Embeddings shape (no attention): {embeddings_no_attn.shape}")
    
    # Test classification head
    logits = model_attn.classifier(embeddings)
    print(f"Logits shape: {logits.shape}")
    
    # Test backward
    loss = F.cross_entropy(logits, y)
    loss.backward()
    print(f"Loss: {loss.item():.4f}")
    
    print("BiLSTMEncoder tests passed!")
