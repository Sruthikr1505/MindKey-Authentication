"""
ONNX Export Module
Export BiLSTM encoder to ONNX format for deployment.
"""

import json
from pathlib import Path
import numpy as np
import torch
import onnx
import onnxruntime as ort

import sys
sys.path.append(str(Path(__file__).parent.parent))

from model import BiLSTMEncoder


def export_to_onnx(
    checkpoint_path: str,
    config_path: str,
    output_path: str,
    opset_version: int = 12
):
    """
    Export BiLSTM encoder to ONNX format.
    
    Args:
        checkpoint_path: Path to model checkpoint
        config_path: Path to config JSON
        output_path: Path to save ONNX model
        opset_version: ONNX opset version
    """
    # Load config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Create model
    model = BiLSTMEncoder(
        n_channels=config['n_channels'],
        hidden_size=config['hidden_size'],
        embedding_size=config['embedding_size'],
        num_layers=config['num_layers'],
        use_attention=config.get('use_attention', True),
        num_classes=config['num_classes']
    )
    
    # Load weights
    model.load_state_dict(torch.load(checkpoint_path, map_location='cpu'))
    model.eval()
    
    # Create dummy input
    dummy_input = torch.randn(1, config['n_channels'], 256)  # (batch, channels, timesteps)
    
    # Export to ONNX
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=opset_version,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['embedding'],
        dynamic_axes={
            'input': {0: 'batch_size', 2: 'timesteps'},
            'embedding': {0: 'batch_size'}
        }
    )
    
    print(f"Model exported to {output_path}")
    
    # Verify ONNX model
    onnx_model = onnx.load(output_path)
    onnx.checker.check_model(onnx_model)
    print("ONNX model verified successfully")


def verify_onnx_model(
    onnx_path: str,
    checkpoint_path: str,
    config_path: str
):
    """
    Verify ONNX model output matches PyTorch model.
    
    Args:
        onnx_path: Path to ONNX model
        checkpoint_path: Path to PyTorch checkpoint
        config_path: Path to config JSON
    """
    # Load config
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Load PyTorch model
    pytorch_model = BiLSTMEncoder(
        n_channels=config['n_channels'],
        hidden_size=config['hidden_size'],
        embedding_size=config['embedding_size'],
        num_layers=config['num_layers'],
        use_attention=config.get('use_attention', True),
        num_classes=config['num_classes']
    )
    pytorch_model.load_state_dict(torch.load(checkpoint_path, map_location='cpu'))
    pytorch_model.eval()
    
    # Create test input
    test_input = np.random.randn(1, config['n_channels'], 256).astype(np.float32)
    
    # PyTorch inference
    with torch.no_grad():
        pytorch_output = pytorch_model(torch.from_numpy(test_input)).numpy()
    
    # ONNX inference
    ort_session = ort.InferenceSession(onnx_path)
    onnx_output = ort_session.run(None, {'input': test_input})[0]
    
    # Compare outputs
    diff = np.abs(pytorch_output - onnx_output).max()
    print(f"Max difference between PyTorch and ONNX: {diff:.8f}")
    
    if diff < 1e-5:
        print("✓ ONNX model verification passed!")
    else:
        print("✗ ONNX model verification failed - outputs differ significantly")
    
    return diff < 1e-5


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Export BiLSTM encoder to ONNX')
    parser.add_argument('--checkpoint', type=str, default='models/encoder.pth', help='Path to checkpoint')
    parser.add_argument('--config', type=str, default='models/config.json', help='Path to config')
    parser.add_argument('--output', type=str, default='models/encoder.onnx', help='Output ONNX path')
    parser.add_argument('--verify', action='store_true', help='Verify ONNX model')
    
    args = parser.parse_args()
    
    # Export
    export_to_onnx(
        checkpoint_path=args.checkpoint,
        config_path=args.config,
        output_path=args.output
    )
    
    # Verify
    if args.verify:
        verify_onnx_model(
            onnx_path=args.output,
            checkpoint_path=args.checkpoint,
            config_path=args.config
        )
