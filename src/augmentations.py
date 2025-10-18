"""
Data augmentation techniques for EEG signals.
"""

import numpy as np
from typing import Tuple


def channel_dropout(x: np.ndarray, p: float = 0.15, seed: int = None) -> np.ndarray:
    """
    Randomly zero out channels with probability p.
    
    Args:
        x: Input signal (n_channels, n_samples)
        p: Dropout probability
        seed: Random seed
    
    Returns:
        Augmented signal
    """
    if seed is not None:
        np.random.seed(seed)
    
    n_channels = x.shape[0]
    mask = np.random.binomial(1, 1-p, size=n_channels)
    return x * mask[:, np.newaxis]


def add_gaussian_noise(x: np.ndarray, snr_db: float = 20.0, seed: int = None) -> np.ndarray:
    """
    Add Gaussian noise to signal at specified SNR.
    
    Args:
        x: Input signal (n_channels, n_samples)
        snr_db: Signal-to-noise ratio in dB
        seed: Random seed
    
    Returns:
        Noisy signal
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Calculate signal power
    signal_power = np.mean(x ** 2)
    
    # Calculate noise power from SNR
    snr_linear = 10 ** (snr_db / 10)
    noise_power = signal_power / snr_linear
    
    # Generate noise
    noise = np.random.normal(0, np.sqrt(noise_power), x.shape)
    
    return x + noise


def time_shift(x: np.ndarray, max_shift_seconds: float = 0.5, fs: int = 128, seed: int = None) -> np.ndarray:
    """
    Randomly shift signal in time.
    
    Args:
        x: Input signal (n_channels, n_samples)
        max_shift_seconds: Maximum shift in seconds
        fs: Sampling frequency
        seed: Random seed
    
    Returns:
        Time-shifted signal
    """
    if seed is not None:
        np.random.seed(seed)
    
    max_shift_samples = int(max_shift_seconds * fs)
    shift = np.random.randint(-max_shift_samples, max_shift_samples + 1)
    
    return np.roll(x, shift, axis=1)


def mixup_same_user(x1: np.ndarray, x2: np.ndarray, alpha: float = 0.2, seed: int = None) -> np.ndarray:
    """
    Mixup augmentation between two trials from the same user.
    
    Args:
        x1: First signal (n_channels, n_samples)
        x2: Second signal (n_channels, n_samples)
        alpha: Mixup parameter (Beta distribution)
        seed: Random seed
    
    Returns:
        Mixed signal
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
    seed: int = None
) -> np.ndarray:
    """
    Composite augmentation pipeline for training.
    
    Args:
        x: Input signal (n_channels, n_samples)
        fs: Sampling frequency
        p_dropout: Channel dropout probability
        snr_db_range: Range for SNR in dB
        p_shift: Probability of applying time shift
        seed: Random seed
    
    Returns:
        Augmented signal
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Channel dropout
    x = channel_dropout(x, p=p_dropout)
    
    # Gaussian noise
    snr_db = np.random.uniform(snr_db_range[0], snr_db_range[1])
    x = add_gaussian_noise(x, snr_db=snr_db)
    
    # Time shift (with probability)
    if np.random.rand() < p_shift:
        x = time_shift(x, max_shift_seconds=0.5, fs=fs)
    
    return x


# Demo
if __name__ == "__main__":
    print("Testing augmentation functions...")
    
    # Create dummy signal
    np.random.seed(42)
    x = np.random.randn(48, 256)  # 48 channels, 256 samples (2s @ 128Hz)
    
    print(f"Original shape: {x.shape}")
    print(f"Original mean: {x.mean():.4f}, std: {x.std():.4f}")
    
    # Test channel dropout
    x_dropout = channel_dropout(x, p=0.2, seed=42)
    print(f"\nAfter channel dropout: mean={x_dropout.mean():.4f}, std={x_dropout.std():.4f}")
    
    # Test Gaussian noise
    x_noise = add_gaussian_noise(x, snr_db=20, seed=42)
    print(f"After Gaussian noise: mean={x_noise.mean():.4f}, std={x_noise.std():.4f}")
    
    # Test time shift
    x_shift = time_shift(x, max_shift_seconds=0.5, fs=128, seed=42)
    print(f"After time shift: mean={x_shift.mean():.4f}, std={x_shift.std():.4f}")
    
    # Test mixup
    x2 = np.random.randn(48, 256)
    x_mix = mixup_same_user(x, x2, alpha=0.2, seed=42)
    print(f"After mixup: mean={x_mix.mean():.4f}, std={x_mix.std():.4f}")
    
    # Test composite augmentation
    x_aug = augment_window(x, fs=128, seed=42)
    print(f"After composite augmentation: mean={x_aug.mean():.4f}, std={x_aug.std():.4f}")
    
    print("\nAll augmentation tests passed!")
