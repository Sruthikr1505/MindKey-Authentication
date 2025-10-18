"""
View the contents of explanation .npy files
"""
import numpy as np
import sys

if len(sys.argv) < 2:
    print("Usage: python view_explanation.py <path_to_npy_file>")
    sys.exit(1)

file_path = sys.argv[1]

# Load the numpy array
data = np.load(file_path)

print("=" * 60)
print("EEG EXPLANATION DATA")
print("=" * 60)
print(f"\nFile: {file_path}")
print(f"\nShape: {data.shape}")
print(f"Data type: {data.dtype}")
print(f"Min value: {data.min():.6f}")
print(f"Max value: {data.max():.6f}")
print(f"Mean value: {data.mean():.6f}")
print(f"Std deviation: {data.std():.6f}")

if len(data.shape) == 2:
    print(f"\nChannels: {data.shape[0]}")
    print(f"Time points: {data.shape[1]}")
    print(f"\nFirst 5 time points of first 3 channels:")
    print(data[:3, :5])
else:
    print(f"\nFirst 10 values:")
    print(data.flatten()[:10])

print("\n" + "=" * 60)
