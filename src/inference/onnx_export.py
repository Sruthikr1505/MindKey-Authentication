"""
ONNX export utilities for model deployment.
"""

import os
import argparse
import logging
import numpy as np
import torch
import onnx
import onnxruntime as ort

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model import BiLSTMEncoder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def export_to_onnx(
    checkpoint_path: str,
    output_path: str,
    n_channels: int = 48,
    timesteps: int = 256,
    device: str = 'cpu'
):
    """
    Export PyTorch model to ONNX format.
    
    Args:
        checkpoint_path: Path to PyTorch checkpoint
        output_path: Path to save ONNX model
        n_channels: Number of EEG channels
        timesteps: Number of timesteps
        device: Device to load model on
    """
    logger.info("Loading PyTorch model...")
    
    # Load model
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
    
    # Create dummy input
    dummy_input = torch.randn(1, n_channels, timesteps).to(device)
    
    logger.info(f"Exporting to ONNX: {output_path}")
    
    # Export to ONNX
    torch.onnx.export(
        model,
        dummy_input,
        output_path,
        export_params=True,
        opset_version=12,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['embedding'],
        dynamic_axes={
            'input': {0: 'batch_size'},
            'embedding': {0: 'batch_size'}
        }
    )
    
    logger.info("ONNX export complete")


def verify_onnx_model(
    onnx_path: str,
    checkpoint_path: str,
    n_channels: int = 48,
    timesteps: int = 256,
    device: str = 'cpu'
):
    """
    Verify ONNX model against PyTorch model.
    
    Args:
        onnx_path: Path to ONNX model
        checkpoint_path: Path to PyTorch checkpoint
        n_channels: Number of EEG channels
        timesteps: Number of timesteps
        device: Device to load model on
    """
    logger.info("Verifying ONNX model...")
    
    # Load PyTorch model
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
    
    # Create test input
    test_input = torch.randn(1, n_channels, timesteps).to(device)
    
    # PyTorch inference
    with torch.no_grad():
        pytorch_output = model(test_input).cpu().numpy()
    
    # ONNX inference
    ort_session = ort.InferenceSession(onnx_path)
    onnx_input = {ort_session.get_inputs()[0].name: test_input.cpu().numpy()}
    onnx_output = ort_session.run(None, onnx_input)[0]
    
    # Compare outputs
    diff = np.abs(pytorch_output - onnx_output).max()
    logger.info(f"Max difference between PyTorch and ONNX: {diff:.8f}")
    
    if diff < 1e-5:
        logger.info("✓ ONNX model verification successful!")
    else:
        logger.warning(f"⚠ Large difference detected: {diff}")
    
    return diff < 1e-5


def main():
    parser = argparse.ArgumentParser(description="Export model to ONNX")
    parser.add_argument('--checkpoint', type=str, default='checkpoints/best.ckpt',
                       help='Path to PyTorch checkpoint')
    parser.add_argument('--output', type=str, default='models/encoder.onnx',
                       help='Path to save ONNX model')
    parser.add_argument('--n_channels', type=int, default=48,
                       help='Number of EEG channels')
    parser.add_argument('--timesteps', type=int, default=256,
                       help='Number of timesteps')
    parser.add_argument('--device', type=str, default='cpu',
                       choices=['cpu', 'cuda'],
                       help='Device to use')
    parser.add_argument('--verify', action='store_true',
                       help='Verify ONNX model after export')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    # Export to ONNX
    export_to_onnx(
        checkpoint_path=args.checkpoint,
        output_path=args.output,
        n_channels=args.n_channels,
        timesteps=args.timesteps,
        device=args.device
    )
    
    # Verify if requested
    if args.verify:
        verify_onnx_model(
            onnx_path=args.output,
            checkpoint_path=args.checkpoint,
            n_channels=args.n_channels,
            timesteps=args.timesteps,
            device=args.device
        )


if __name__ == "__main__":
    main()
