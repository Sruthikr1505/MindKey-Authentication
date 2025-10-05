"""
TorchServe Handler
Custom handler for serving BiLSTM encoder with TorchServe.
"""

import json
import logging
import numpy as np
import torch
from ts.torch_handler.base_handler import BaseHandler

logger = logging.getLogger(__name__)


class EEGAuthHandler(BaseHandler):
    """
    Custom TorchServe handler for EEG authentication.
    
    Expects preprocessed numpy arrays as input.
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
        model_pt_path = f"{model_dir}/{serialized_file}"
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load config
        config_path = f"{model_dir}/config.json"
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Import model (assumes model.py is in model archive)
        from model import BiLSTMEncoder
        
        self.model = BiLSTMEncoder(
            n_channels=self.config['n_channels'],
            hidden_size=self.config['hidden_size'],
            embedding_size=self.config['embedding_size'],
            num_layers=self.config['num_layers'],
            use_attention=self.config.get('use_attention', True),
            num_classes=self.config['num_classes']
        )
        
        self.model.load_state_dict(torch.load(model_pt_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        
        self.initialized = True
        logger.info("EEG Auth Handler initialized")
    
    def preprocess(self, data):
        """
        Preprocess input data.
        
        Args:
            data: List of input data (numpy arrays or JSON)
            
        Returns:
            Preprocessed tensor
        """
        preprocessed = []
        
        for row in data:
            # Expect numpy array or JSON with 'data' key
            if isinstance(row, dict):
                # JSON input
                if 'body' in row:
                    body = row['body']
                    if isinstance(body, (bytes, bytearray)):
                        body = json.loads(body.decode('utf-8'))
                    trial = np.array(body['data'])
                else:
                    trial = np.array(row['data'])
            else:
                # Direct numpy array
                trial = np.array(row)
            
            preprocessed.append(trial)
        
        # Stack into batch
        batch = np.stack(preprocessed, axis=0)
        tensor = torch.from_numpy(batch).float().to(self.device)
        
        return tensor
    
    def inference(self, data):
        """
        Run inference.
        
        Args:
            data: Preprocessed tensor
            
        Returns:
            Model output
        """
        with torch.no_grad():
            embeddings = self.model(data)
        
        return embeddings
    
    def postprocess(self, inference_output):
        """
        Postprocess inference output.
        
        Args:
            inference_output: Model output tensor
            
        Returns:
            List of predictions
        """
        embeddings = inference_output.cpu().numpy()
        
        # Return as list of embeddings
        return [emb.tolist() for emb in embeddings]


# For standalone testing
if __name__ == "__main__":
    print("TorchServe handler stub created.")
    print("To use with TorchServe:")
    print("1. Create model archive with: torch-model-archiver")
    print("2. Include: encoder.pth, config.json, model.py, attention.py, torchserve_handler.py")
    print("3. Start TorchServe with the .mar file")
