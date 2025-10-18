"""
TorchServe handler for EEG authentication model.
"""

import os
import json
import logging
import numpy as np
import torch
from ts.torch_handler.base_handler import BaseHandler

logger = logging.getLogger(__name__)


class EEGAuthHandler(BaseHandler):
    """
    Custom TorchServe handler for EEG authentication.
    """
    
    def __init__(self):
        super().__init__()
        self.initialized = False
    
    def initialize(self, context):
        """
        Initialize handler.
        
        Args:
            context: TorchServe context
        """
        self.manifest = context.manifest
        properties = context.system_properties
        model_dir = properties.get("model_dir")
        
        # Load model
        serialized_file = self.manifest['model']['serializedFile']
        model_pt_path = os.path.join(model_dir, serialized_file)
        
        if not os.path.isfile(model_pt_path):
            raise RuntimeError(f"Missing model file: {model_pt_path}")
        
        # Import model class
        import sys
        sys.path.append(model_dir)
        from model import BiLSTMEncoder
        
        # Create model
        self.model = BiLSTMEncoder(
            n_channels=48,
            hidden_size=128,
            num_layers=2,
            embedding_size=128,
            use_attention=True,
            num_classes=10
        )
        
        # Load checkpoint
        checkpoint = torch.load(model_pt_path, map_location=self.device)
        self.model.load_state_dict(checkpoint)
        self.model.to(self.device)
        self.model.eval()
        
        logger.info("Model loaded successfully")
        self.initialized = True
    
    def preprocess(self, data):
        """
        Preprocess input data.
        
        Args:
            data: List of input data (numpy arrays as bytes)
        
        Returns:
            Preprocessed tensor
        """
        preprocessed_data = []
        
        for row in data:
            # Assume input is numpy array sent as bytes
            input_data = row.get("data") or row.get("body")
            
            if isinstance(input_data, (bytes, bytearray)):
                # Deserialize numpy array
                input_array = np.frombuffer(input_data, dtype=np.float32)
                # Reshape to (n_channels, timesteps)
                input_array = input_array.reshape(48, -1)
            else:
                # Assume already numpy array
                input_array = np.array(input_data)
            
            # Convert to tensor
            input_tensor = torch.FloatTensor(input_array)
            preprocessed_data.append(input_tensor)
        
        # Stack into batch
        batch = torch.stack(preprocessed_data)
        
        return batch
    
    def inference(self, data):
        """
        Run inference.
        
        Args:
            data: Preprocessed input tensor
        
        Returns:
            Model output (embeddings)
        """
        with torch.no_grad():
            embeddings = self.model(data.to(self.device))
        
        return embeddings
    
    def postprocess(self, inference_output):
        """
        Postprocess inference output.
        
        Args:
            inference_output: Model output tensor
        
        Returns:
            List of response dictionaries
        """
        # Convert to numpy
        embeddings = inference_output.cpu().numpy()
        
        # Create response
        responses = []
        for embedding in embeddings:
            response = {
                "embedding": embedding.tolist(),
                "embedding_dim": len(embedding)
            }
            responses.append(response)
        
        return responses


# For testing
if __name__ == "__main__":
    print("TorchServe handler stub created.")
    print("To use with TorchServe:")
    print("1. Package model with torch-model-archiver")
    print("2. Deploy to TorchServe")
    print("3. Send requests to inference endpoint")
