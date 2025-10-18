"""
DEAP EEG Preprocessing Module
Handles loading .bdf files, preprocessing (filtering, ICA, normalization), and saving processed trials.
"""

import os
import argparse
import logging
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import mne
from scipy import signal
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_bdf_to_trials(path: str, n_channels: int = 48) -> np.ndarray:
    """
    Load EEG data from .bdf file and return trials.
    
    Args:
        path: Path to .bdf file
        n_channels: Number of EEG channels to use (default 48 for DEAP)
    
    Returns:
        trials: np.ndarray of shape (n_trials, n_channels, n_samples)
    """
    try:
        # Load BDF file using MNE
        raw = mne.io.read_raw_bdf(path, preload=True, verbose=False)
        
        # Get EEG channels (first 48 channels in DEAP)
        eeg_channels = raw.ch_names[:n_channels]
        raw.pick_channels(eeg_channels)
        
        # Get data
        data = raw.get_data()  # Shape: (n_channels, n_samples)
        
        # DEAP has 40 trials, each 63 seconds at 512 Hz
        # 63 seconds * 512 Hz = 32256 samples per trial
        fs = int(raw.info['sfreq'])
        trial_duration = 63  # seconds
        samples_per_trial = trial_duration * fs
        
        n_trials = 40
        trials = []
        
        for trial_idx in range(n_trials):
            start_sample = trial_idx * samples_per_trial
            end_sample = start_sample + samples_per_trial
            
            if end_sample <= data.shape[1]:
                trial_data = data[:, start_sample:end_sample]
                trials.append(trial_data)
            else:
                logger.warning(f"Trial {trial_idx} exceeds data length, skipping")
        
        trials = np.array(trials)  # Shape: (n_trials, n_channels, n_samples)
        logger.info(f"Loaded {trials.shape[0]} trials with shape {trials.shape[1:]}")
        
        return trials
        
    except Exception as e:
        logger.error(f"Error loading BDF file {path}: {e}")
        raise


def preprocess_trials(
    trials: np.ndarray,
    fs_in: int = 512,
    fs_out: int = 128,
    do_ica: bool = True,
    bandpass_low: float = 1.0,
    bandpass_high: float = 50.0,
    notch_freq: Optional[float] = 50.0
) -> np.ndarray:
    """
    Preprocess EEG trials with filtering, downsampling, normalization, and optional ICA.
    
    Args:
        trials: Input trials (n_trials, n_channels, n_samples)
        fs_in: Input sampling frequency
        fs_out: Output sampling frequency
        do_ica: Whether to apply ICA for artifact removal
        bandpass_low: Low cutoff for bandpass filter
        bandpass_high: High cutoff for bandpass filter
        notch_freq: Notch filter frequency (50 or 60 Hz), None to skip
    
    Returns:
        processed_trials: Preprocessed trials (n_trials, n_channels, n_samples_out)
    """
    n_trials, n_channels, n_samples = trials.shape
    processed_trials = []
    
    logger.info(f"Preprocessing {n_trials} trials...")
    
    for trial_idx in tqdm(range(n_trials), desc="Preprocessing trials"):
        trial = trials[trial_idx]  # Shape: (n_channels, n_samples)
        
        # 1. Bandpass filter
        sos = signal.butter(4, [bandpass_low, bandpass_high], btype='band', fs=fs_in, output='sos')
        trial = signal.sosfiltfilt(sos, trial, axis=1)
        
        # 2. Notch filter (optional)
        if notch_freq is not None:
            b_notch, a_notch = signal.iirnotch(notch_freq, Q=30, fs=fs_in)
            trial = signal.filtfilt(b_notch, a_notch, trial, axis=1)
        
        # 3. Downsample
        if fs_in != fs_out:
            downsample_factor = fs_in // fs_out
            trial = signal.decimate(trial, downsample_factor, axis=1, zero_phase=True)
        
        # 4. Z-score normalization per channel
        trial = (trial - trial.mean(axis=1, keepdims=True)) / (trial.std(axis=1, keepdims=True) + 1e-8)
        
        # 5. Optional ICA (basic artifact removal)
        if do_ica:
            try:
                # Create MNE RawArray for ICA
                info = mne.create_info(ch_names=[f'CH{i}' for i in range(n_channels)],
                                     sfreq=fs_out, ch_types='eeg')
                raw_trial = mne.io.RawArray(trial, info, verbose=False)
                
                # Fit ICA
                ica = mne.preprocessing.ICA(n_components=min(15, n_channels-1), 
                                           random_state=42, max_iter=200, verbose=False)
                ica.fit(raw_trial)
                
                # Auto-detect and exclude EOG-like components (first 2 components often artifacts)
                ica.exclude = list(range(min(2, len(ica.exclude))))
                
                # Apply ICA
                raw_trial = ica.apply(raw_trial)
                trial = raw_trial.get_data()
                
            except Exception as e:
                logger.warning(f"ICA failed for trial {trial_idx}: {e}, skipping ICA")
        
        processed_trials.append(trial)
    
    processed_trials = np.array(processed_trials)
    logger.info(f"Preprocessing complete. Output shape: {processed_trials.shape}")
    
    return processed_trials


def save_processed(
    subject_id: int,
    input_dir: str,
    output_dir: str,
    fast_mode: bool = False,
    n_channels: int = 48
):
    """
    Load, preprocess, and save trials for a single subject.
    
    Args:
        subject_id: Subject ID (1-10)
        input_dir: Directory containing raw .bdf files
        output_dir: Directory to save processed .npy files
        fast_mode: If True, process only first 3 trials for quick testing
        n_channels: Number of EEG channels
    """
    # Find BDF file
    bdf_path = os.path.join(input_dir, f"s{subject_id:02d}.bdf")
    
    if not os.path.exists(bdf_path):
        logger.error(f"BDF file not found: {bdf_path}")
        return
    
    logger.info(f"Processing subject {subject_id:02d}...")
    
    # Load trials
    trials = load_bdf_to_trials(bdf_path, n_channels=n_channels)
    
    # Fast mode: only first 3 trials
    if fast_mode:
        trials = trials[:3]
        logger.info(f"Fast mode: processing only {len(trials)} trials")
    
    # Preprocess
    processed = preprocess_trials(trials, fs_in=512, fs_out=128, do_ica=True)
    
    # Save each trial
    os.makedirs(output_dir, exist_ok=True)
    
    for trial_idx, trial_data in enumerate(processed):
        output_path = os.path.join(output_dir, f"s{subject_id:02d}_trial{trial_idx:02d}.npy")
        np.save(output_path, trial_data)
    
    logger.info(f"Saved {len(processed)} trials for subject {subject_id:02d}")


def main():
    parser = argparse.ArgumentParser(description="Preprocess DEAP EEG data")
    parser.add_argument('--input_dir', type=str, default='data/raw',
                       help='Directory containing raw .bdf files')
    parser.add_argument('--output_dir', type=str, default='data/processed',
                       help='Directory to save processed .npy files')
    parser.add_argument('--subjects', type=int, nargs='+', default=list(range(1, 11)),
                       help='Subject IDs to process (default: 1-10)')
    parser.add_argument('--fast', action='store_true',
                       help='Fast mode: process only first 3 trials per subject')
    parser.add_argument('--n_channels', type=int, default=48,
                       help='Number of EEG channels to use')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    # Set random seeds
    np.random.seed(args.seed)
    
    # Process each subject
    for subject_id in args.subjects:
        try:
            save_processed(
                subject_id=subject_id,
                input_dir=args.input_dir,
                output_dir=args.output_dir,
                fast_mode=args.fast,
                n_channels=args.n_channels
            )
        except Exception as e:
            logger.error(f"Failed to process subject {subject_id}: {e}")
    
    logger.info("Preprocessing complete!")


if __name__ == "__main__":
    # Demo: load and preprocess a single trial
    import sys
    
    if len(sys.argv) == 1:
        print("Demo mode: Testing preprocessing functions")
        
        # Create dummy trial data
        dummy_trial = np.random.randn(1, 48, 32256)  # 1 trial, 48 channels, 63s @ 512Hz
        print(f"Input shape: {dummy_trial.shape}")
        
        # Preprocess
        processed = preprocess_trials(dummy_trial, fs_in=512, fs_out=128, do_ica=False)
        print(f"Output shape: {processed.shape}")
        print(f"Output mean: {processed.mean():.4f}, std: {processed.std():.4f}")
        
        print("\nTo run preprocessing on real data:")
        print("python src/preprocessing.py --input_dir data/raw --output_dir data/processed --subjects 1 2 3 --fast")
    else:
        main()
