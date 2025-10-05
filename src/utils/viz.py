"""
Visualization Utilities
Plot waveforms, heatmaps, ROC curves, and DET curves.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Optional
from sklearn.metrics import roc_curve, auc


def plot_eeg_waveform(
    trial: np.ndarray,
    fs: int = 128,
    channels_to_plot: Optional[list] = None,
    save_path: Optional[str] = None
):
    """
    Plot EEG waveform for selected channels.
    
    Args:
        trial: (n_channels, n_samples) array
        fs: Sampling frequency
        channels_to_plot: List of channel indices to plot (default: first 4)
        save_path: Path to save figure
    """
    if channels_to_plot is None:
        channels_to_plot = list(range(min(4, trial.shape[0])))
    
    n_channels = len(channels_to_plot)
    time = np.arange(trial.shape[1]) / fs
    
    fig, axes = plt.subplots(n_channels, 1, figsize=(12, 2 * n_channels), sharex=True)
    if n_channels == 1:
        axes = [axes]
    
    for i, ch_idx in enumerate(channels_to_plot):
        axes[i].plot(time, trial[ch_idx], linewidth=0.5)
        axes[i].set_ylabel(f'Ch {ch_idx}')
        axes[i].grid(True, alpha=0.3)
    
    axes[-1].set_xlabel('Time (s)')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_attention_heatmap(
    trial: np.ndarray,
    attention_weights: np.ndarray,
    fs: int = 128,
    save_path: Optional[str] = None
):
    """
    Plot heatmap of attention weights over time and channels.
    
    Args:
        trial: (n_channels, n_samples) array
        attention_weights: (n_samples,) or (n_channels, n_samples) attention weights
        fs: Sampling frequency
        save_path: Path to save figure
    """
    n_channels, n_samples = trial.shape
    time = np.arange(n_samples) / fs
    
    # If 1D attention, broadcast to all channels
    if attention_weights.ndim == 1:
        attention_weights = np.tile(attention_weights, (n_channels, 1))
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1])
    
    # Heatmap
    im = ax1.imshow(
        attention_weights,
        aspect='auto',
        cmap='hot',
        interpolation='nearest',
        extent=[time[0], time[-1], n_channels, 0]
    )
    ax1.set_ylabel('Channel')
    ax1.set_title('Attention Heatmap')
    plt.colorbar(im, ax=ax1, label='Attention Weight')
    
    # Average attention over channels
    avg_attention = attention_weights.mean(axis=0)
    ax2.plot(time, avg_attention, linewidth=1.5)
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Avg Attention')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_roc_curve(
    genuine_scores: np.ndarray,
    impostor_scores: np.ndarray,
    save_path: Optional[str] = None
):
    """
    Plot ROC curve for authentication system.
    
    Args:
        genuine_scores: Genuine similarity scores
        impostor_scores: Impostor similarity scores
        save_path: Path to save figure
    """
    # Create labels
    y_true = np.concatenate([
        np.ones(len(genuine_scores)),
        np.zeros(len(impostor_scores))
    ])
    y_scores = np.concatenate([genuine_scores, impostor_scores])
    
    # Compute ROC
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)
    
    # Plot
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, linewidth=2, label=f'ROC (AUC = {roc_auc:.3f})')
    plt.plot([0, 1], [0, 1], 'k--', linewidth=1, label='Random')
    plt.xlabel('False Positive Rate (FAR)')
    plt.ylabel('True Positive Rate (1 - FRR)')
    plt.title('ROC Curve')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_det_curve(
    genuine_scores: np.ndarray,
    impostor_scores: np.ndarray,
    save_path: Optional[str] = None
):
    """
    Plot DET (Detection Error Tradeoff) curve.
    
    Args:
        genuine_scores: Genuine similarity scores
        impostor_scores: Impostor similarity scores
        save_path: Path to save figure
    """
    # Create labels
    y_true = np.concatenate([
        np.ones(len(genuine_scores)),
        np.zeros(len(impostor_scores))
    ])
    y_scores = np.concatenate([genuine_scores, impostor_scores])
    
    # Compute ROC
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    frr = 1 - tpr
    
    # Plot on log scale
    plt.figure(figsize=(8, 6))
    plt.plot(fpr * 100, frr * 100, linewidth=2)
    plt.xlabel('False Accept Rate (%)')
    plt.ylabel('False Reject Rate (%)')
    plt.title('DET Curve')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid(True, which='both', alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def plot_score_distribution(
    genuine_scores: np.ndarray,
    impostor_scores: np.ndarray,
    save_path: Optional[str] = None
):
    """
    Plot distribution of genuine vs impostor scores.
    
    Args:
        genuine_scores: Genuine similarity scores
        impostor_scores: Impostor similarity scores
        save_path: Path to save figure
    """
    plt.figure(figsize=(10, 6))
    
    plt.hist(impostor_scores, bins=50, alpha=0.6, label='Impostor', color='red', density=True)
    plt.hist(genuine_scores, bins=50, alpha=0.6, label='Genuine', color='green', density=True)
    
    plt.xlabel('Similarity Score')
    plt.ylabel('Density')
    plt.title('Score Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


if __name__ == "__main__":
    # Demo
    print("Testing visualization utilities...")
    
    import tempfile
    
    # Create dummy data
    trial = np.random.randn(32, 256)
    attention = np.random.rand(256)
    attention = attention / attention.sum()
    
    genuine_scores = np.random.beta(8, 2, 1000)
    impostor_scores = np.random.beta(2, 8, 1000)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test waveform plot
        plot_eeg_waveform(trial, fs=128, save_path=f"{tmpdir}/waveform.png")
        print("Waveform plot saved")
        
        # Test heatmap
        plot_attention_heatmap(trial, attention, fs=128, save_path=f"{tmpdir}/heatmap.png")
        print("Heatmap saved")
        
        # Test ROC
        plot_roc_curve(genuine_scores, impostor_scores, save_path=f"{tmpdir}/roc.png")
        print("ROC curve saved")
        
        # Test DET
        plot_det_curve(genuine_scores, impostor_scores, save_path=f"{tmpdir}/det.png")
        print("DET curve saved")
        
        # Test score distribution
        plot_score_distribution(genuine_scores, impostor_scores, save_path=f"{tmpdir}/dist.png")
        print("Score distribution saved")
    
    print("Visualization tests passed!")
