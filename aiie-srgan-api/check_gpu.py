try:
    import tensorlayerx as tlx
    print('=' * 50)
    print('TensorLayerX GPU Check (SRGAN API)')
    print('=' * 50)
    print(f'Backend: {tlx.BACKEND}')
    
    if tlx.BACKEND == 'tensorflow':
        import tensorflow as tf
        gpus = tf.config.list_physical_devices('GPU')
        print(f'TensorFlow GPU Available: {len(gpus) > 0}')
        print(f'TensorFlow GPUs: {gpus}')
        if len(gpus) == 0:
            print('⚠️  Running on CPU - GPU not detected')
    elif tlx.BACKEND == 'torch':
        import torch
        print(f'PyTorch CUDA Available: {torch.cuda.is_available()}')
        if torch.cuda.is_available():
            print(f'PyTorch CUDA Device: {torch.cuda.get_device_name(0)}')
        else:
            print('⚠️  Running on CPU - GPU not detected')
except Exception as e:
    print(f'Error checking GPU: {e}')
