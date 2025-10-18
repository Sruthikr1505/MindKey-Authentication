"""
Visualization utilities for EEG data and evaluation metrics.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List
from pathlib import Path


def plot_eeg_waveform(
    data: np.ndarray,
    fs: int = 128,
    channels_to_plot: Optional[List[int]] = None,
    title: str = "EEG Waveform",
    save_path: Optional[str] = None
):
    """
    Plot EEG waveform for selected channels.
    
    Args:
        data: EEG data (n_channels, n_samples)
        fs: Sampling frequency
        channels_to_plot: List of channel indices to plot (default: first 8)
        title: Plot title
        save_path: Path to save figure
    """
    if channels_to_plot is None:
        channels_to_plot = list(range(min(8, data.shape[0])))
    
    n_channels = len(channels_to_plot)
    time = np.arange(data.shape[1]) / fs
    
    fig, axes = plt.subplots(n_channels, 1, figsize=(12, 2*n_channels), sharex=True)
    if n_channels == 1:
        axes = [axes]
    
    for i, ch_idx in enumerate(channels_to_plot):
        axes[i].plot(time, data[ch_idx], linewidth=0.5)
        axes[i].set_ylabel(f'Ch {ch_idx}')
        axes[i].grid(True, alpha=0.3)
    
    axes[-1].set_xlabel('Time (s)')
    fig.suptitle(title)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved waveform plot to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_attention_heatmap(
    attention_weights: np.ndarray,
    fs: int = 128,
    title: str = "Attention Heatmap",
    save_path: Optional[str] = None
):
    """
    Plot attention weights as heatmap.
    
    Args:
        attention_weights: Attention weights (batch, timesteps) or (timesteps,)
        fs: Sampling frequency
        title: Plot title
        save_path: Path to save figure
    """
    if attention_weights.ndim == 1:
        attention_weights = attention_weights[np.newaxis, :]
    
    time = np.arange(attention_weights.shape[1]) / fs
    
    plt.figure(figsize=(12, 4))
    plt.imshow(attention_weights, aspect='auto', cmap='hot', interpolation='nearest')
    plt.colorbar(label='Attention Weight')
    plt.xlabel('Time (s)')
    plt.ylabel('Sample')
    
    # Set x-axis ticks to time
    n_ticks = 10
    tick_indices = np.linspace(0, len(time)-1, n_ticks, dtype=int)
    plt.xticks(tick_indices, [f'{time[i]:.1f}' for i in tick_indices])
    
    plt.title(title)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved attention heatmap to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_roc_curve(
    far: np.ndarray,
    tar: np.ndarray,
    eer: Optional[float] = None,
    title: str = "ROC Curve",
    save_path: Optional[str] = None
):
    """
    Plot ROC curve (FAR vs TAR).
    
    Args:
        far: False Accept Rate
        tar: True Accept Rate
        eer: Equal Error Rate (optional, for annotation)
        title: Plot title
        save_path: Path to save figure
    """
    plt.figure(figsize=(8, 8))
    plt.plot(far, tar, linewidth=2, label='ROC Curve')
    plt.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random')
    
    if eer is not None:
        plt.plot(eer, 1-eer, 'ro', markersize=8, label=f'EER = {eer*100:.2f}%')
    
    plt.xlabel('False Accept Rate (FAR)')
    plt.ylabel('True Accept Rate (TAR)')
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved ROC curve to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_det_curve(
    far: np.ndarray,
    frr: np.ndarray,
    eer: Optional[float] = None,
    title: str = "DET Curve",
    save_path: Optional[str] = None
):
    """
    Plot DET curve (FAR vs FRR in log scale).
    
    Args:
        far: False Accept Rate
        frr: False Reject Rate
        eer: Equal Error Rate (optional, for annotation)
        title: Plot title
        save_path: Path to save figure
    """
    plt.figure(figsize=(8, 8))
    plt.plot(far * 100, frr * 100, linewidth=2, label='DET Curve')
    plt.plot([0.01, 100], [0.01, 100], 'k--', linewidth=1, label='EER Line')
    
    if eer is not None:
        plt.plot(eer * 100, eer * 100, 'ro', markersize=8, label=f'EER = {eer*100:.2f}%')
    
    plt.xlabel('False Accept Rate (%)')
    plt.ylabel('False Reject Rate (%)')
    plt.title(title)
    plt.xscale('log')
    plt.yscale('log')
    plt.grid(True, which='both', alpha=0.3)
    plt.legend()
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved DET curve to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_score_distribution(
    genuine_scores: np.ndarray,
    impostor_scores: np.ndarray,
    threshold: Optional[float] = None,
    title: str = "Score Distribution",
    save_path: Optional[str] = None
):
    """
    Plot distribution of genuine and impostor scores.
    
    Args:
        genuine_scores: Genuine similarity scores
        impostor_scores: Impostor similarity scores
        threshold: Decision threshold (optional)
        title: Plot title
        save_path: Path to save figure
    """
    plt.figure(figsize=(10, 6))
    
    plt.hist(genuine_scores, bins=50, alpha=0.6, label='Genuine', color='green', density=True)
    plt.hist(impostor_scores, bins=50, alpha=0.6, label='Impostor', color='red', density=True)
    
    if threshold is not None:
        plt.axvline(threshold, color='black', linestyle='--', linewidth=2, 
                   label=f'Threshold = {threshold:.3f}')
    
    plt.xlabel('Similarity Score')
    plt.ylabel('Density')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved score distribution to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_confusion_matrix(
    cm: np.ndarray,
    class_names: Optional[List[str]] = None,
    title: str = "Confusion Matrix",
    save_path: Optional[str] = None
):
    """
    Plot confusion matrix.
    
    Args:
        cm: Confusion matrix
        class_names: List of class names
        title: Plot title
        save_path: Path to save figure
    """
    plt.figure(figsize=(10, 8))
    
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names)
    
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title(title)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved confusion matrix to {save_path}")
    else:
        plt.show()
    
    plt.close()


# Demo
if __name__ == "__main__":
    print("Testing visualization functions...")
    
    # Create dummy data
    np.random.seed(42)
    
    # EEG waveform
    eeg_data = np.random.randn(48, 512)
    plot_eeg_waveform(eeg_data, fs=128, channels_to_plot=[0, 1, 2, 3], 
                     title="Demo EEG Waveform")
    
    # Attention heatmap
    attention = np.random.rand(256)
    attention = attention / attention.sum()
    plot_attention_heatmap(attention, fs=128, title="Demo Attention Heatmap")
    
    # ROC curve
    far = np.linspace(0, 1, 100)
    tar = 1 - np.sqrt(far)  # Dummy curve
    plot_roc_curve(far, tar, eer=0.05, title="Demo ROC Curve")
    
    # DET curve
    frr = np.linspace(0.001, 0.5, 100)
    far_det = frr ** 1.2  # Dummy curve
    plot_det_curve(far_det, frr, eer=0.05, title="Demo DET Curve")
    
    # Score distribution
    genuine = np.random.normal(0.8, 0.1, 1000)
    impostor = np.random.normal(0.4, 0.15, 1000)
    plot_score_distribution(genuine, impostor, threshold=0.6, title="Demo Score Distribution")
    
    print("\nAll visualization tests passed!")
