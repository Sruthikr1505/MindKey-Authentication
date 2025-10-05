"""
DEAP EEG Preprocessing Module
Loads .bdf or .mat files, applies bandpass filtering, downsampling, ICA artifact removal, and z-score normalization.
"""

import os
import logging
import argparse
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import mne
from scipy import signal
from scipy.io import loadmat
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_bdf_to_trials(path: str) -> np.ndarray:
    """
    Load EEG data from .bdf or .mat file.
    
    Args:
        path: Path to .bdf or .mat file
        
    Returns:
        trials: np.ndarray of shape (n_trials, n_channels, n_samples)
    """
    path = Path(path)
    
    if path.suffix == '.bdf':
        # Load BDF file using MNE
        raw = mne.io.read_raw_bdf(str(path), preload=True, verbose=False)
        # Get data: (n_channels, n_samples)
        data = raw.get_data()
        # For DEAP, typically 40 trials of 63 seconds each at 512 Hz
        # Split into 40 trials of equal length
        n_channels, total_samples = data.shape
        trial_length = total_samples // 40
        trials = []
        for i in range(40):
            start = i * trial_length
            end = start + trial_length
            trials.append(data[:, start:end])
        trials = np.array(trials)  # (40, n_channels, trial_length)
        
    elif path.suffix == '.mat':
        # Load .mat file (DEAP preprocessed format)
        mat = loadmat(str(path))
        # DEAP .mat structure: 'data' key contains (40, 32, 8064) for 40 trials, 32 channels, 63s @ 128Hz
        if 'data' in mat:
            trials = mat['data']  # (40, 32, n_samples)
        elif 'eeg' in mat:
            trials = mat['eeg']
        else:
            # Try to find the largest array
            arrays = {k: v for k, v in mat.items() if isinstance(v, np.ndarray) and v.ndim == 3}
            if arrays:
                key = max(arrays.keys(), key=lambda k: arrays[k].size)
                trials = arrays[key]
                logger.warning(f"Using key '{key}' from .mat file")
            else:
                raise ValueError(f"Could not find trial data in {path}")
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")
    
    logger.info(f"Loaded {trials.shape[0]} trials with {trials.shape[1]} channels and {trials.shape[2]} samples from {path.name}")
    return trials


def preprocess_trials(
    trials: np.ndarray,
    fs_in: int = 512,
    fs_out: int = 128,
    do_ica: bool = True,
    seed: int = 42
) -> np.ndarray:
    """
    Preprocess EEG trials: bandpass filter, downsample, ICA artifact removal, z-score normalization.
    
    Args:
        trials: (n_trials, n_channels, n_samples) array
        fs_in: Input sampling frequency
        fs_out: Output sampling frequency
        do_ica: Whether to apply ICA for artifact removal
        seed: Random seed for reproducibility
        
    Returns:
        processed_trials: (n_trials, n_channels, n_samples_out) array
    """
    np.random.seed(seed)
    n_trials, n_channels, n_samples = trials.shape
    processed = []
    
    # Design bandpass filter 1-50 Hz
    nyquist = fs_in / 2
    low = 1.0 / nyquist
    high = 50.0 / nyquist
    b, a = signal.butter(4, [low, high], btype='band')
    
    # Optional notch filter for powerline (50/60 Hz)
    notch_freq = 50.0  # Change to 60.0 for US
    Q = 30.0
    b_notch, a_notch = signal.iirnotch(notch_freq, Q, fs_in)
    
    for trial_idx in range(n_trials):
        trial = trials[trial_idx]  # (n_channels, n_samples)
        
        # 1. Bandpass filter
        trial_filt = signal.filtfilt(b, a, trial, axis=1)
        
        # 2. Notch filter
        trial_filt = signal.filtfilt(b_notch, a_notch, trial_filt, axis=1)
        
        # 3. Downsample
        if fs_in != fs_out:
            downsample_factor = fs_in // fs_out
            trial_filt = signal.decimate(trial_filt, downsample_factor, axis=1, zero_phase=True)
        
        # 4. ICA for artifact removal (optional, can be slow)
        if do_ica:
            try:
                # Create MNE RawArray for ICA
                ch_names = [f'EEG{i:03d}' for i in range(n_channels)]
                ch_types = ['eeg'] * n_channels
                info = mne.create_info(ch_names=ch_names, sfreq=fs_out, ch_types=ch_types)
                raw = mne.io.RawArray(trial_filt, info, verbose=False)
                
                # Fit ICA
                ica = mne.preprocessing.ICA(n_components=min(15, n_channels), random_state=seed, max_iter=200, verbose=False)
                ica.fit(raw)
                
                # Automatically detect and exclude EOG components (heuristic)
                # In production, you'd use EOG channels or manual inspection
                eog_indices, eog_scores = ica.find_bads_eog(raw, threshold=3.0, verbose=False)
                ica.exclude = eog_indices[:2]  # Exclude top 2 EOG components
                
                # Apply ICA
                raw_clean = ica.apply(raw.copy(), verbose=False)
                trial_filt = raw_clean.get_data()
            except Exception as e:
                logger.warning(f"ICA failed for trial {trial_idx}: {e}. Skipping ICA.")
        
        # 5. Z-score normalization per channel
        trial_norm = (trial_filt - trial_filt.mean(axis=1, keepdims=True)) / (trial_filt.std(axis=1, keepdims=True) + 1e-8)
        
        processed.append(trial_norm)
    
    processed = np.array(processed)
    logger.info(f"Preprocessed {n_trials} trials: {trials.shape} -> {processed.shape}")
    return processed


def save_processed(
    subject_id: int,
    input_dir: str,
    output_dir: str,
    fast: bool = False,
    fs_in: int = 512,
    fs_out: int = 128,
    do_ica: bool = False,  # ICA is slow, disabled by default for demo
    seed: int = 42
):
    """
    Load, preprocess, and save trials for a single subject.
    
    Args:
        subject_id: Subject ID (1-10)
        input_dir: Directory containing raw .bdf files
        output_dir: Directory to save processed .npy files
        fast: If True, process only first 3 trials
        fs_in: Input sampling frequency
        fs_out: Output sampling frequency
        do_ica: Whether to apply ICA
        seed: Random seed
    """
    input_path = Path(input_dir) / f"s{subject_id:02d}.bdf"
    if not input_path.exists():
        # Try .mat extension
        input_path = Path(input_dir) / f"s{subject_id:02d}.mat"
        if not input_path.exists():
            logger.error(f"File not found: {input_path}")
            return
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Load trials
    trials = load_bdf_to_trials(str(input_path))
    
    # Fast mode: only first 3 trials
    if fast:
        trials = trials[:3]
        logger.info(f"Fast mode: processing only {len(trials)} trials")
    
    # Preprocess
    processed = preprocess_trials(trials, fs_in=fs_in, fs_out=fs_out, do_ica=do_ica, seed=seed)
    
    # Save each trial separately
    for trial_idx, trial_data in enumerate(processed):
        trial_path = output_path / f"s{subject_id:02d}_trial{trial_idx:02d}.npy"
        np.save(str(trial_path), trial_data)
    
    logger.info(f"Saved {len(processed)} trials for subject {subject_id:02d} to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Preprocess DEAP EEG data')
    parser.add_argument('--input_dir', type=str, default='data/raw', help='Input directory with .bdf files')
    parser.add_argument('--output_dir', type=str, default='data/processed', help='Output directory for .npy files')
    parser.add_argument('--subjects', type=int, nargs='+', default=list(range(1, 11)), help='Subject IDs to process')
    parser.add_argument('--fast', action='store_true', help='Fast mode: process only 3 trials per subject')
    parser.add_argument('--fs_in', type=int, default=512, help='Input sampling frequency')
    parser.add_argument('--fs_out', type=int, default=128, help='Output sampling frequency')
    parser.add_argument('--ica', action='store_true', help='Apply ICA for artifact removal (slow)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    
    args = parser.parse_args()
    
    logger.info(f"Starting preprocessing for subjects: {args.subjects}")
    logger.info(f"Fast mode: {args.fast}, ICA: {args.ica}")
    
    for subject_id in tqdm(args.subjects, desc='Processing subjects'):
        save_processed(
            subject_id=subject_id,
            input_dir=args.input_dir,
            output_dir=args.output_dir,
            fast=args.fast,
            fs_in=args.fs_in,
            fs_out=args.fs_out,
            do_ica=args.ica,
            seed=args.seed
        )
    
    logger.info("Preprocessing complete!")


if __name__ == "__main__":
    main()
