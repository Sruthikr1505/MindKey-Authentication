"""
PyTorch Dataset and DataLoader utilities for DEAP EEG data.
"""

import os
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from typing import List, Tuple, Dict
import logging

from augmentations import augment_window

logger = logging.getLogger(__name__)


class DEAPDataset(Dataset):
    """
    Dataset for DEAP EEG trials with windowing and augmentation.
    """
    
    def __init__(
        self,
        processed_dir: str,
        subject_list: List[int],
        split: str = 'train',
        window_size_seconds: float = 2.0,
        step_seconds: float = 1.0,
        fs: int = 128,
        apply_augmentation: bool = True,
        seed: int = 42
    ):
        """
        Args:
            processed_dir: Directory containing processed .npy files
            subject_list: List of subject IDs to include
            split: 'train', 'val', or 'test'
            window_size_seconds: Window size in seconds
            step_seconds: Step size for sliding window
            fs: Sampling frequency
            apply_augmentation: Whether to apply augmentation (only for train split)
            seed: Random seed
        """
        self.processed_dir = processed_dir
        self.subject_list = subject_list
        self.split = split
        self.window_size = int(window_size_seconds * fs)
        self.step_size = int(step_seconds * fs)
        self.fs = fs
        self.apply_augmentation = apply_augmentation and (split == 'train')
        self.seed = seed
        
        # Load data
        self.windows = []
        self.labels = []
        
        self._load_data()
        
        logger.info(f"Loaded {len(self.windows)} windows for {split} split")
    
    def _load_data(self):
        """Load and window all trials for specified subjects and split."""
        np.random.seed(self.seed)
        
        for subject_id in self.subject_list:
            # Find all trial files for this subject
            trial_files = []
            for f in os.listdir(self.processed_dir):
                if f.startswith(f"s{subject_id:02d}_trial") and f.endswith(".npy"):
                    trial_files.append(f)
            
            trial_files.sort()
            
            # Split trials: first 30 for train/val, last 10 for test
            if self.split in ['train', 'val']:
                trial_files = trial_files[:30]
                
                # Further split train/val: 80/20
                n_train = int(0.8 * len(trial_files))
                if self.split == 'train':
                    trial_files = trial_files[:n_train]
                else:  # val
                    trial_files = trial_files[n_train:]
            else:  # test
                trial_files = trial_files[30:40]
            
            # Load trials and create windows
            for trial_file in trial_files:
                trial_path = os.path.join(self.processed_dir, trial_file)
                trial_data = np.load(trial_path)  # Shape: (n_channels, n_samples)
                
                # Create sliding windows
                n_samples = trial_data.shape[1]
                for start_idx in range(0, n_samples - self.window_size + 1, self.step_size):
                    window = trial_data[:, start_idx:start_idx + self.window_size]
                    self.windows.append(window)
                    self.labels.append(subject_id - 1)  # 0-indexed labels
    
    def __len__(self):
        return len(self.windows)
    
    def __getitem__(self, idx):
        window = self.windows[idx].copy()
        label = self.labels[idx]
        
        # Apply augmentation for training
        if self.apply_augmentation:
            window = augment_window(window, fs=self.fs, seed=None)
        
        # Convert to torch tensors
        window = torch.FloatTensor(window)  # Shape: (n_channels, n_samples)
        label = torch.LongTensor([label])[0]
        
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
    Create train, validation, and test dataloaders.
    
    Args:
        processed_dir: Directory containing processed .npy files
        subject_ids: List of subject IDs
        batch_size: Batch size
        num_workers: Number of workers for data loading
        window_size_seconds: Window size in seconds
        step_seconds: Step size in seconds
        fs: Sampling frequency
        seed: Random seed
    
    Returns:
        train_loader, val_loader, test_loader
    """
    # Set random seeds
    torch.manual_seed(seed)
    np.random.seed(seed)
    
    # Create datasets
    train_dataset = DEAPDataset(
        processed_dir=processed_dir,
        subject_list=subject_ids,
        split='train',
        window_size_seconds=window_size_seconds,
        step_seconds=step_seconds,
        fs=fs,
        apply_augmentation=True,
        seed=seed
    )
    
    val_dataset = DEAPDataset(
        processed_dir=processed_dir,
        subject_list=subject_ids,
        split='val',
        window_size_seconds=window_size_seconds,
        step_seconds=step_seconds,
        fs=fs,
        apply_augmentation=False,
        seed=seed
    )
    
    test_dataset = DEAPDataset(
        processed_dir=processed_dir,
        subject_list=subject_ids,
        split='test',
        window_size_seconds=window_size_seconds,
        step_seconds=step_seconds,
        fs=fs,
        apply_augmentation=False,
        seed=seed
    )
    
    # Create dataloaders
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


# Demo
if __name__ == "__main__":
    print("Testing DEAPDataset...")
    
    # Create dummy processed files for testing
    import tempfile
    import shutil
    
    temp_dir = tempfile.mkdtemp()
    print(f"Creating dummy data in {temp_dir}")
    
    # Create dummy processed files
    for subject_id in [1, 2]:
        for trial_id in range(40):
            dummy_data = np.random.randn(48, 8064)  # 48 channels, 63s @ 128Hz
            filename = f"s{subject_id:02d}_trial{trial_id:02d}.npy"
            np.save(os.path.join(temp_dir, filename), dummy_data)
    
    # Create dataset
    dataset = DEAPDataset(
        processed_dir=temp_dir,
        subject_list=[1, 2],
        split='train',
        window_size_seconds=2.0,
        step_seconds=1.0,
        fs=128
    )
    
    print(f"Dataset size: {len(dataset)}")
    
    # Test __getitem__
    window, label = dataset[0]
    print(f"Window shape: {window.shape}")
    print(f"Label: {label}")
    
    # Test dataloader
    train_loader, val_loader, test_loader = make_dataloaders(
        processed_dir=temp_dir,
        subject_ids=[1, 2],
        batch_size=32,
        num_workers=0,
        seed=42
    )
    
    print(f"\nTrain batches: {len(train_loader)}")
    print(f"Val batches: {len(val_loader)}")
    print(f"Test batches: {len(test_loader)}")
    
    # Test batch
    for batch_windows, batch_labels in train_loader:
        print(f"\nBatch windows shape: {batch_windows.shape}")
        print(f"Batch labels shape: {batch_labels.shape}")
        break
    
    # Cleanup
    shutil.rmtree(temp_dir)
    print("\nDataset tests passed!")
