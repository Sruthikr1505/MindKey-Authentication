# Exploration Notebooks

This directory is for Jupyter notebooks to explore the data and models.

## Suggested Notebooks

### 1. Data Exploration (`data_exploration.ipynb`)

```python
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Load preprocessed trial
trial = np.load('data/processed/s01_trial00.npy')
print(f"Trial shape: {trial.shape}")  # (32, n_samples)

# Plot channels
fig, axes = plt.subplots(4, 1, figsize=(12, 8))
for i in range(4):
    axes[i].plot(trial[i])
    axes[i].set_ylabel(f'Ch {i}')
plt.show()
```

### 2. Model Inference (`model_inference.ipynb`)

```python
import torch
from src.model import BiLSTMEncoder
import json

# Load config
with open('models/config.json') as f:
    config = json.load(f)

# Load model
model = BiLSTMEncoder(**config)
model.load_state_dict(torch.load('models/encoder.pth', map_location='cpu'))
model.eval()

# Inference
trial = np.load('data/processed/s01_trial00.npy')
trial_tensor = torch.from_numpy(trial).float().unsqueeze(0)
embedding = model(trial_tensor)
print(f"Embedding: {embedding.shape}")
```

### 3. Evaluation Analysis (`eval_analysis.ipynb`)

```python
import json
import matplotlib.pyplot as plt

# Load results
with open('outputs/eval_results.json') as f:
    results = json.load(f)

print(f"EER: {results['eer']:.4f}")
print(f"EER Threshold: {results['eer_threshold']:.4f}")

# Plot FAR vs FRR
plt.figure(figsize=(10, 6))
plt.plot(results['thresholds'], results['far'], label='FAR')
plt.plot(results['thresholds'], results['frr'], label='FRR')
plt.xlabel('Threshold')
plt.ylabel('Error Rate')
plt.legend()
plt.grid(True)
plt.show()
```

## Creating Notebooks

Use Jupyter Lab or Jupyter Notebook:

```bash
pip install jupyterlab
jupyter lab
```

Then create notebooks in this directory.
