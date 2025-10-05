"""
DEAP Dataset Module
Loads preprocessed EEG trials, creates sliding windows, applies augmentations, and provides DataLoaders.
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split

from augmentations import augment_window


class DEAPDataset(Dataset):
    """
    DEAP EEG Dataset with sliding windows.
    
    For each subject, first 30 trials are used for training, last 10 for testing.
    """
    
    def __init__(
        self,
        processed_dir: str,
        subject_list: List[int],
        split: str = 'train',
        window_size_seconds: float = 2.0,
        step_seconds: float = 1.0,
        fs: int = 128,
        augment: bool = True,
        seed: int = 42
    ):
        """
        Args:
            processed_dir: Directory containing preprocessed .npy files
            subject_list: List of subject IDs (1-10)
            split: 'train', 'val', or 'test'
            window_size_seconds: Window size in seconds
            step_seconds: Step size for sliding window in seconds
            fs: Sampling frequency
            augment: Whether to apply augmentations (only for train split)
            seed: Random seed
        """
        self.processed_dir = Path(processed_dir)
        self.subject_list = subject_list
        self.split = split
        self.window_size = int(window_size_seconds * fs)
        self.step_size = int(step_seconds * fs)
        self.fs = fs
        self.augment = augment and (split == 'train')
        self.seed = seed
        
        np.random.seed(seed)
        
        # Load and create windows
        self.windows = []
        self.labels = []
        
        for subject_id in subject_list:
            # Determine trial range based on split
            if split == 'train':
                trial_range = range(0, 24)  # First 24 trials for training (60%)
            elif split == 'val':
                trial_range = range(24, 30)  # Next 6 trials for validation (15%)
            else:  # test
                trial_range = range(30, 40)  # Last 10 trials for testing (25%)
            
            for trial_idx in trial_range:
                trial_path = self.processed_dir / f"s{subject_id:02d}_trial{trial_idx:02d}.npy"
                
                if not trial_path.exists():
                    continue
                
                # Load trial: (n_channels, n_samples)
                trial = np.load(str(trial_path))
                
                # Create sliding windows
                n_channels, n_samples = trial.shape
                for start in range(0, n_samples - self.window_size + 1, self.step_size):
                    end = start + self.window_size
                    window = trial[:, start:end]
                    self.windows.append(window)
                    self.labels.append(subject_id - 1)  # 0-indexed labels
        
        self.windows = np.array(self.windows, dtype=np.float32)
        self.labels = np.array(self.labels, dtype=np.int64)
        
        print(f"Loaded {len(self.windows)} windows for {split} split from {len(subject_list)} subjects")
    
    def __len__(self):
        return len(self.windows)
    
    def __getitem__(self, idx):
        window = self.windows[idx]
        label = self.labels[idx]
        
        # Apply augmentations for training
        if self.augment:
            window = augment_window(window, fs=self.fs, seed=None)  # Random augmentation
        
        # Convert to tensor
        window = torch.from_numpy(window).float()
        label = torch.tensor(label, dtype=torch.long)
        
        return window, label


def make_dataloaders(
    processed_dir: str,
    subject_ids: List[int],
    batch_size: int = 64,
    num_workers: int = 4,
    window_size_seconds: float = 2.0,
    step_seconds: float = 1.0,
    fs: int = 128,
    seed: int = 42
) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Create train, validation, and test DataLoaders.
    
    Args:
        processed_dir: Directory with preprocessed .npy files
        subject_ids: List of subject IDs
        batch_size: Batch size
        num_workers: Number of workers for DataLoader
        window_size_seconds: Window size in seconds
        step_seconds: Step size in seconds
        fs: Sampling frequency
        seed: Random seed
        
    Returns:
        train_loader, val_loader, test_loader
    """
    # Create datasets
    train_dataset = DEAPDataset(
        processed_dir=processed_dir,
        subject_list=subject_ids,
        split='train',
        window_size_seconds=window_size_seconds,
        step_seconds=step_seconds,
        fs=fs,
        augment=True,
        seed=seed
    )
    
    val_dataset = DEAPDataset(
        processed_dir=processed_dir,
        subject_list=subject_ids,
        split='val',
        window_size_seconds=window_size_seconds,
        step_seconds=step_seconds,
        fs=fs,
        augment=False,
        seed=seed
    )
    
    test_dataset = DEAPDataset(
        processed_dir=processed_dir,
        subject_list=subject_ids,
        split='test',
        window_size_seconds=window_size_seconds,
        step_seconds=step_seconds,
        fs=fs,
        augment=False,
        seed=seed
    )
    
    # Create DataLoaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
        drop_last=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )
    
    return train_loader, val_loader, test_loader


if __name__ == "__main__":
    # Demo
    print("Testing DEAPDataset...")
    
    # Create dummy processed files for testing
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy data
        for subject_id in [1, 2]:
            for trial_idx in range(40):
                trial = np.random.randn(32, 16384)  # 32 channels, 128 seconds @ 128 Hz
                trial_path = Path(tmpdir) / f"s{subject_id:02d}_trial{trial_idx:02d}.npy"
                np.save(str(trial_path), trial)
        
        # Test dataset
        dataset = DEAPDataset(
            processed_dir=tmpdir,
            subject_list=[1, 2],
            split='train',
            window_size_seconds=2.0,
            step_seconds=1.0,
            fs=128,
            augment=True,
            seed=42
        )
        
        print(f"Dataset size: {len(dataset)}")
        window, label = dataset[0]
        print(f"Window shape: {window.shape}, Label: {label}")
        
        # Test DataLoader
        train_loader, val_loader, test_loader = make_dataloaders(
            processed_dir=tmpdir,
            subject_ids=[1, 2],
            batch_size=32,
            num_workers=0,
            seed=42
        )
        
        print(f"Train batches: {len(train_loader)}")
        print(f"Val batches: {len(val_loader)}")
        print(f"Test batches: {len(test_loader)}")
        
        # Test batch
        for batch_x, batch_y in train_loader:
            print(f"Batch X shape: {batch_x.shape}, Batch Y shape: {batch_y.shape}")
            break
    
    print("Dataset tests passed!")
