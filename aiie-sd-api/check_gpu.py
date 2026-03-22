import torch

print('=' * 50)
print('PyTorch GPU Check (Stable Diffusion API)')
print('=' * 50)
print(f'CUDA Available: {torch.cuda.is_available()}')
print(f'CUDA Device Count: {torch.cuda.device_count()}')

if torch.cuda.is_available():
    print(f'CUDA Device Name: {torch.cuda.get_device_name(0)}')
    print(f'CUDA Version: {torch.version.cuda}')
else:
    print('⚠️  Running on CPU - GPU not detected')
