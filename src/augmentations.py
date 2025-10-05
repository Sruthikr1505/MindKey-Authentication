"""
EEG Data Augmentation Module
Provides augmentation techniques for EEG signals: channel dropout, noise injection, time shift, mixup.
"""

import numpy as np
from typing import Tuple


def channel_dropout(x: np.ndarray, p: float = 0.15, seed: int = None) -> np.ndarray:
    """
    Randomly zero out channels with probability p.
    
    Args:
        x: (n_channels, n_samples) array
        p: Dropout probability
        seed: Random seed
        
    Returns:
        Augmented array
    """
    if seed is not None:
        np.random.seed(seed)
    
    n_channels = x.shape[0]
    mask = np.random.rand(n_channels) > p
    x_aug = x.copy()
    x_aug[~mask] = 0
    return x_aug


def add_gaussian_noise(x: np.ndarray, snr_db: float = 20.0, seed: int = None) -> np.ndarray:
    """
    Add Gaussian noise to signal with specified SNR.
    
    Args:
        x: (n_channels, n_samples) array
        snr_db: Signal-to-noise ratio in dB
        seed: Random seed
        
    Returns:
        Noisy array
    """
    if seed is not None:
        np.random.seed(seed)
    
    signal_power = np.mean(x ** 2)
    snr_linear = 10 ** (snr_db / 10)
    noise_power = signal_power / snr_linear
    noise = np.random.normal(0, np.sqrt(noise_power), x.shape)
    return x + noise


def time_shift(x: np.ndarray, max_shift_seconds: float, fs: int = 128, seed: int = None) -> np.ndarray:
    """
    Randomly shift signal in time (circular shift).
    
    Args:
        x: (n_channels, n_samples) array
        max_shift_seconds: Maximum shift in seconds
        fs: Sampling frequency
        seed: Random seed
        
    Returns:
        Shifted array
    """
    if seed is not None:
        np.random.seed(seed)
    
    max_shift_samples = int(max_shift_seconds * fs)
    shift = np.random.randint(-max_shift_samples, max_shift_samples + 1)
    return np.roll(x, shift, axis=1)


def mixup_same_user(x1: np.ndarray, x2: np.ndarray, alpha: float = 0.2, seed: int = None) -> np.ndarray:
    """
    Mixup augmentation: linear interpolation between two samples from same user.
    
    Args:
        x1: (n_channels, n_samples) array
        x2: (n_channels, n_samples) array
        alpha: Beta distribution parameter
        seed: Random seed
        
    Returns:
        Mixed array
    """
    if seed is not None:
        np.random.seed(seed)
    
    lam = np.random.beta(alpha, alpha)
    return lam * x1 + (1 - lam) * x2


def augment_window(
    x: np.ndarray,
    fs: int = 128,
    p_dropout: float = 0.15,
    snr_db_range: Tuple[float, float] = (12, 28),
    p_shift: float = 0.5,
    max_shift: float = 0.2,
    seed: int = None
) -> np.ndarray:
    """
    Composite augmentation pipeline for training.
    
    Args:
        x: (n_channels, n_samples) array
        fs: Sampling frequency
        p_dropout: Channel dropout probability
        snr_db_range: Range for SNR in dB
        p_shift: Probability of applying time shift
        max_shift: Maximum time shift in seconds
        seed: Random seed
        
    Returns:
        Augmented array
    """
    if seed is not None:
        np.random.seed(seed)
    
    x_aug = x.copy()
    
    # Channel dropout
    if np.random.rand() < 0.5:
        x_aug = channel_dropout(x_aug, p=p_dropout)
    
    # Gaussian noise
    if np.random.rand() < 0.7:
        snr_db = np.random.uniform(*snr_db_range)
        x_aug = add_gaussian_noise(x_aug, snr_db=snr_db)
    
    # Time shift
    if np.random.rand() < p_shift:
        x_aug = time_shift(x_aug, max_shift_seconds=max_shift, fs=fs)
    
    return x_aug


if __name__ == "__main__":
    # Demo
    print("Testing augmentations...")
    
    # Create dummy EEG signal
    n_channels, n_samples = 32, 256
    x = np.random.randn(n_channels, n_samples)
    
    # Test each augmentation
    x_dropout = channel_dropout(x, p=0.2, seed=42)
    print(f"Channel dropout: {(x_dropout == 0).sum()} zeros added")
    
    x_noise = add_gaussian_noise(x, snr_db=15.0, seed=42)
    print(f"Noise injection: SNR change = {10 * np.log10(np.mean(x**2) / np.mean((x - x_noise)**2)):.2f} dB")
    
    x_shift = time_shift(x, max_shift_seconds=0.1, fs=128, seed=42)
    print(f"Time shift: correlation = {np.corrcoef(x.flatten(), x_shift.flatten())[0, 1]:.3f}")
    
    x2 = np.random.randn(n_channels, n_samples)
    x_mix = mixup_same_user(x, x2, alpha=0.2, seed=42)
    print(f"Mixup: output shape = {x_mix.shape}")
    
    x_aug = augment_window(x, seed=42)
    print(f"Composite augmentation: output shape = {x_aug.shape}")
    
    print("All augmentations passed!")
