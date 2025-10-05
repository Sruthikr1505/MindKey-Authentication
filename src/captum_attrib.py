"""
Captum Explainability Module
Generate attribution heatmaps and identify important channels/time windows.
"""

import os
import json
from pathlib import Path
import numpy as np
import torch
from captum.attr import IntegratedGradients, GradientShap, Saliency
import matplotlib.pyplot as plt

from model import BiLSTMEncoder
from utils.viz import plot_attention_heatmap


def explain_trial(
    checkpoint_path: str,
    trial_path: str,
    config: dict,
    methods: list = ['integrated_gradients', 'grad_shap'],
    output_dir: str = 'outputs/explanations',
    device: str = 'cpu'
) -> dict:
    """
    Generate explanations for a single trial using Captum.
    
    Args:
        checkpoint_path: Path to model checkpoint
        trial_path: Path to trial .npy file
        config: Model configuration dict
        methods: List of attribution methods to use
        output_dir: Directory to save outputs
        device: Device to use
        
    Returns:
        result: Dict with paths to heatmap and top channels/windows
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load model
    model = BiLSTMEncoder(
        n_channels=config['n_channels'],
        hidden_size=config['hidden_size'],
        embedding_size=config['embedding_size'],
        num_layers=config['num_layers'],
        use_attention=config.get('use_attention', True),
        num_classes=config['num_classes']
    )
    
    model.load_state_dict(torch.load(checkpoint_path, map_location=device))
    model.eval()
    model.to(device)
    
    # Load trial
    trial = np.load(trial_path)  # (n_channels, n_samples)
    trial_tensor = torch.from_numpy(trial).float().unsqueeze(0).to(device)  # (1, n_channels, n_samples)
    
    # Compute baseline (zeros)
    baseline = torch.zeros_like(trial_tensor)
    
    # Compute attributions
    attributions = {}
    
    if 'integrated_gradients' in methods:
        ig = IntegratedGradients(model)
        attr_ig = ig.attribute(trial_tensor, baseline, target=None)
        attributions['integrated_gradients'] = attr_ig.squeeze(0).cpu().detach().numpy()
    
    if 'grad_shap' in methods:
        gs = GradientShap(model)
        attr_gs = gs.attribute(trial_tensor, baseline, target=None)
        attributions['grad_shap'] = attr_gs.squeeze(0).cpu().detach().numpy()
    
    if 'saliency' in methods:
        sal = Saliency(model)
        attr_sal = sal.attribute(trial_tensor, target=None)
        attributions['saliency'] = attr_sal.squeeze(0).cpu().detach().numpy()
    
    # Aggregate attributions (use first method)
    method_name = methods[0]
    attr = attributions[method_name]  # (n_channels, n_samples)
    
    # Compute importance scores
    channel_importance = np.abs(attr).mean(axis=1)  # (n_channels,)
    temporal_importance = np.abs(attr).mean(axis=0)  # (n_samples,)
    
    # Top channels
    top_channel_indices = np.argsort(channel_importance)[::-1][:5]
    top_channels = [
        {'channel': int(idx), 'importance': float(channel_importance[idx])}
        for idx in top_channel_indices
    ]
    
    # Top time windows (divide into 10 windows)
    n_samples = attr.shape[1]
    window_size = n_samples // 10
    window_importance = []
    for i in range(10):
        start = i * window_size
        end = start + window_size if i < 9 else n_samples
        importance = np.abs(attr[:, start:end]).mean()
        window_importance.append({'window': i, 'start': start, 'end': end, 'importance': float(importance)})
    
    window_importance = sorted(window_importance, key=lambda x: x['importance'], reverse=True)[:5]
    
    # Generate heatmap
    trial_name = Path(trial_path).stem
    heatmap_path = output_dir / f'{trial_name}_{method_name}_heatmap.png'
    
    # Normalize attributions for visualization
    attr_norm = np.abs(attr)
    attr_norm = (attr_norm - attr_norm.min()) / (attr_norm.max() - attr_norm.min() + 1e-8)
    
    plot_attention_heatmap(
        trial=trial,
        attention_weights=attr_norm,
        fs=128,
        save_path=str(heatmap_path)
    )
    
    # Save JSON
    json_path = output_dir / f'{trial_name}_{method_name}_explanation.json'
    explanation = {
        'trial': trial_name,
        'method': method_name,
        'top_channels': top_channels,
        'top_windows': window_importance,
        'heatmap_path': str(heatmap_path)
    }
    
    with open(json_path, 'w') as f:
        json.dump(explanation, f, indent=2)
    
    print(f"Explanation saved to {json_path}")
    print(f"Heatmap saved to {heatmap_path}")
    
    return explanation


if __name__ == "__main__":
    # Demo
    print("Testing Captum attribution...")
    
    import tempfile
    
    # Create dummy trial
    trial = np.random.randn(32, 256)
    
    # Create dummy config
    config = {
        'n_channels': 32,
        'hidden_size': 128,
        'embedding_size': 128,
        'num_layers': 2,
        'use_attention': True,
        'num_classes': 10
    }
    
    # Create dummy model
    model = BiLSTMEncoder(**config)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save trial
        trial_path = f"{tmpdir}/test_trial.npy"
        np.save(trial_path, trial)
        
        # Save model
        checkpoint_path = f"{tmpdir}/model.pth"
        torch.save(model.state_dict(), checkpoint_path)
        
        # Generate explanation
        explanation = explain_trial(
            checkpoint_path=checkpoint_path,
            trial_path=trial_path,
            config=config,
            methods=['integrated_gradients'],
            output_dir=f"{tmpdir}/explanations",
            device='cpu'
        )
        
        print(f"Top channels: {explanation['top_channels']}")
        print(f"Top windows: {explanation['top_windows']}")
    
    print("Captum attribution tests passed!")
