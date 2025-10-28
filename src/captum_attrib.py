"""
Explainability using Captum for EEG authentication.
"""

import os
import argparse
import json
import logging
from pathlib import Path
import numpy as np
import torch
from captum.attr import IntegratedGradients, GradientShap, Saliency

from model import BiLSTMEncoder
from utils.viz import plot_attention_heatmap

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def explain_trial(
    checkpoint_path: str,
    trial_path: str,
    methods: list = ['integrated_gradients', 'grad_shap'],
    n_channels: int = 48,
    device: str = 'cpu',
    output_dir: str = 'outputs/explanations'
):
    """
    Generate explanations for a single trial using Captum.
    
    Args:
        checkpoint_path: Path to model checkpoint
        trial_path: Path to trial .npy file
        methods: List of attribution methods to use
        n_channels: Number of EEG channels
        device: Device to run on
        output_dir: Output directory for explanations
    
    Returns:
        results: Dictionary containing explanation results
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Load model
    logger.info("Loading model...")
    model = BiLSTMEncoder(
        n_channels=n_channels,
        hidden_size=128,
        num_layers=2,
        embedding_size=128,
        use_attention=True,
        num_classes=10
    )
    
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint)
    model.eval()
    model.to(device)
    
    # Load trial
    logger.info(f"Loading trial from {trial_path}...")
    trial_data = np.load(trial_path)  # Shape: (n_channels, n_samples)
    
    # Convert to tensor
    trial_tensor = torch.FloatTensor(trial_data).unsqueeze(0).to(device)  # (1, n_channels, n_samples)
    
    # Get model prediction
    with torch.no_grad():
        embedding = model(trial_tensor)
    
    logger.info(f"Trial embedding shape: {embedding.shape}")
    
    # Create wrapper for attribution
    def model_forward(x):
        return model(x)
    
    results = {
        'trial_path': trial_path,
        'methods': {},
        'top_channels': [],
        'top_time_windows': []
    }
    
    # Compute attributions for each method
    for method in methods:
        logger.info(f"Computing {method} attributions...")
        
        if method == 'integrated_gradients':
            attributor = IntegratedGradients(model_forward)
            baseline = torch.zeros_like(trial_tensor)
            attributions = attributor.attribute(trial_tensor, baseline, target=None)
        
        elif method == 'grad_shap':
            attributor = GradientShap(model_forward)
            baseline = torch.randn(10, *trial_tensor.shape[1:]).to(device) * 0.1
            attributions = attributor.attribute(trial_tensor, baseline, target=None)
        
        elif method == 'saliency':
            attributor = Saliency(model_forward)
            attributions = attributor.attribute(trial_tensor, target=None)
        
        else:
            logger.warning(f"Unknown method: {method}, skipping")
            continue
        
        # Convert to numpy
        attr_np = attributions.squeeze(0).cpu().detach().numpy()  # (n_channels, n_samples)
        
        # Compute importance per channel (sum of absolute attributions)
        channel_importance = np.abs(attr_np).sum(axis=1)
        
        # Compute importance per time window (divide into 10 windows)
        n_samples = attr_np.shape[1]
        window_size = n_samples // 10
        time_importance = []
        for i in range(10):
            start = i * window_size
            end = min((i + 1) * window_size, n_samples)
            window_attr = np.abs(attr_np[:, start:end]).sum()
            time_importance.append(window_attr)
        time_importance = np.array(time_importance)
        
        # Get top channels
        top_channel_indices = np.argsort(channel_importance)[-5:][::-1]
        top_channels = [
            {'channel': int(idx), 'importance': float(channel_importance[idx])}
            for idx in top_channel_indices
        ]
        
        # Get top time windows
        top_time_indices = np.argsort(time_importance)[-3:][::-1]
        top_time_windows = [
            {'window': int(idx), 'start_sample': int(idx * window_size), 
             'end_sample': int(min((idx + 1) * window_size, n_samples)),
             'importance': float(time_importance[idx])}
            for idx in top_time_indices
        ]
        
        results['methods'][method] = {
            'top_channels': top_channels,
            'top_time_windows': top_time_windows
        }
        
        # Save heatmap
        heatmap_path = os.path.join(output_dir, f'{method}_heatmap.png')
        plot_attention_heatmap(
            np.abs(attr_np),
            fs=128,
            title=f'{method.replace("_", " ").title()} Attribution',
            save_path=heatmap_path
        )
        
        results['methods'][method]['heatmap_path'] = heatmap_path
    
    # Aggregate top channels across methods
    all_channels = {}
    for method_results in results['methods'].values():
        for ch_info in method_results['top_channels']:
            ch = ch_info['channel']
            if ch not in all_channels:
                all_channels[ch] = 0
            all_channels[ch] += ch_info['importance']
    
    # Sort and get top 5
    sorted_channels = sorted(all_channels.items(), key=lambda x: x[1], reverse=True)[:5]
    results['top_channels'] = [
        {'channel': ch, 'aggregated_importance': float(imp)}
        for ch, imp in sorted_channels
    ]
    
    # Save results
    results_path = os.path.join(output_dir, 'explanation_results.json')
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Saved explanation results to {results_path}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Generate explanations for EEG trial")
    parser.add_argument('--checkpoint', type=str, default='checkpoints/best.ckpt',
                       help='Path to model checkpoint')
    parser.add_argument('--trial', type=str, required=True,
                       help='Path to trial .npy file')
    parser.add_argument('--methods', type=str, nargs='+',
                       default=['integrated_gradients', 'grad_shap'],
                       choices=['integrated_gradients', 'grad_shap', 'saliency'],
                       help='Attribution methods to use')
    parser.add_argument('--n_channels', type=int, default=48,
                       help='Number of EEG channels')
    parser.add_argument('--device', type=str, default='cpu',
                       choices=['cpu', 'cuda'],
                       help='Device to run on')
    parser.add_argument('--output_dir', type=str, default='outputs/explanations',
                       help='Output directory')
    
    args = parser.parse_args()
    
    # Generate explanations
    results = explain_trial(
        checkpoint_path=args.checkpoint,cd 
        trial_path=args.trial,
        methods=args.methods,
        n_channels=args.n_channels,
        device=args.device,
        output_dir=args.output_dir
    )
    
    # Print summary
    print("\n" + "="*50)
    print("EXPLANATION RESULTS")
    print("="*50)
    print(f"Trial: {args.trial}")
    print(f"\nTop 5 Important Channels (aggregated):")
    for ch_info in results['top_channels']:
        print(f"  Channel {ch_info['channel']}: {ch_info['aggregated_importance']:.2f}")
    
    print(f"\nMethod-specific results:")
    for method, method_results in results['methods'].items():
        print(f"\n{method.replace('_', ' ').title()}:")
        print(f"  Top channels: {[ch['channel'] for ch in method_results['top_channels'][:3]]}")
        print(f"  Heatmap saved to: {method_results['heatmap_path']}")
    
    print("="*50 + "\n")


if __name__ == "__main__":
    main()
