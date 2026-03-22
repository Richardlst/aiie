import os
import sys
from pathlib import Path
import numpy as np
import tensorlayerx as tlx
from PIL import Image
import gc

# Add the parent directory to the path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.srgan import SRGAN_g
from app.logger import setup_logger

logger = setup_logger("BatchProcessor")

# Setup TensorLayerX
os.environ["TL_BACKEND"] = "tensorflow"
tlx.set_device("GPU")


def load_model():
    """Load the pre-trained SRGAN model"""
    G = SRGAN_g()
    G.init_build(tlx.nn.Input(shape=(1, 96, 96, 3)))

    model_path = os.path.join("models/g.npz")
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")

    G.load_weights(model_path, format="npz_dict")
    G.set_eval()
    logger.info("Model loaded successfully")
    return G


def process_batch_image(G, lr_img, patch_size=384, overlap=32):
    """Process image using batch processing with patches"""
    h, w = lr_img.shape[:2]

    n_h = (h + patch_size - 1) // patch_size
    n_w = (w + patch_size - 1) // patch_size

    print(f"Splitting image {(h, w)} into {n_h}x{n_w} patches")

    scale = 4
    output = np.zeros((h * scale, w * scale, 3), dtype=np.float32)
    weight = np.zeros_like(output)

    for i in range(n_h):
        for j in range(n_w):
            top = i * patch_size
            left = j * patch_size
            bottom = min(top + patch_size + overlap, h)
            right = min(left + patch_size + overlap, w)

            patch = lr_img[top:bottom, left:right]

            # Prepare tensor for NHWC format with improved normalization
            # Convert to float32 first to avoid precision loss
            patch_tensor = patch.astype(np.float32)
            # Normalize to [-1, 1] range more precisely
            patch_tensor = (patch_tensor / 127.5) - 1.0
            patch_tensor = patch_tensor[np.newaxis, ...]
            patch_tensor = tlx.ops.convert_to_tensor(patch_tensor)

            try:
                sr_patch = G(patch_tensor)
                sr_patch = tlx.ops.convert_to_numpy(sr_patch)

                # Convert from [-1, 1] to [0, 1] range more precisely
                sr_patch = (sr_patch + 1.0) / 2.0
                # Clip to ensure values are in valid range
                sr_patch = np.clip(sr_patch, 0.0, 1.0)
                sr_patch = sr_patch[0]

                top_sr = top * scale
                left_sr = left * scale
                bottom_sr = bottom * scale
                right_sr = right * scale

                mask = np.ones_like(sr_patch)
                if overlap > 0:
                    mask = create_blending_mask(sr_patch.shape[:2])

                output[top_sr:bottom_sr, left_sr:right_sr] += sr_patch * mask
                weight[top_sr:bottom_sr, left_sr:right_sr] += mask

                print(f"Processed patch ({i}, {j})")

            except Exception as e:
                print(f"Error processing patch ({i}, {j}): {str(e)}")
                continue

    # Final conversion with better precision
    output = np.divide(output, weight, where=weight != 0)
    # Ensure output is in [0, 1] range before scaling
    output = np.clip(output, 0.0, 1.0)
    # Convert to uint8 with proper rounding
    output = np.round(output * 255.0).astype(np.uint8)

    return output


def create_blending_mask(shape):
    """Create mask for blending patches"""
    h, w = shape
    mask = np.ones((h, w), dtype=np.float32)

    # Create gradient at edges
    gradient_size = 32
    for i in range(gradient_size):
        alpha = i / gradient_size
        mask[i, :] *= alpha
        mask[-i - 1, :] *= alpha
        mask[:, i] *= alpha
        mask[:, -i - 1] *= alpha

    return mask[..., np.newaxis]


def load_image(image_path):
    """Load image from file path"""
    try:
        pil_image = Image.open(image_path)

        # Convert RGBA to RGB if needed
        if pil_image.mode == "RGBA":
            pil_image = pil_image.convert("RGB")

        # Convert PIL Image to numpy array
        valid_img = np.asarray(pil_image)
        return valid_img
    except Exception as e:
        logger.error(f"Error loading image {image_path}: {str(e)}")
        return None


def save_image(image_array, output_path):
    """Save numpy array as image"""
    try:
        # Image is already in RGB format from PIL processing, no conversion needed
        # Create PIL Image and save
        output_image = Image.fromarray(image_array)
        output_image.save(output_path)
        logger.info(f"Saved processed image to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error saving image {output_path}: {str(e)}")
        return False


def get_supported_image_extensions():
    """Get list of supported image extensions"""
    return {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}


def process_folder(G, input_folder, output_folder, patch_size=384, overlap=32):
    """Process all images in input folder and save to output folder"""

    # Create output folder if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)

    # Get all image files from input folder
    input_path = Path(input_folder)
    supported_extensions = get_supported_image_extensions()

    image_files = []
    for ext in supported_extensions:
        image_files.extend(list(input_path.glob(f"*{ext}")))
        image_files.extend(list(input_path.glob(f"*{ext.upper()}")))

    if not image_files:
        logger.warning(f"No supported image files found in {input_folder}")
        return

    logger.info(f"Found {len(image_files)} image files to process")

    # Process each image
    processed_count = 0
    for i, image_file in enumerate(image_files):
        logger.info(f"Processing {i + 1}/{len(image_files)}: {image_file.name}")

        # Load image
        lr_img = load_image(image_file)
        if lr_img is None:
            continue

        print(f"Input image shape: {lr_img.shape}")

        try:
            # Process image
            sr_img = process_batch_image(
                G, lr_img, patch_size=patch_size, overlap=overlap
            )
            print(f"Output image shape: {sr_img.shape}")

            # Create output filename
            output_filename = f"sr_{image_file.stem}{image_file.suffix}"
            output_path = Path(output_folder) / output_filename

            # Save processed image
            if save_image(sr_img, output_path):
                processed_count += 1

            # Cleanup memory
            del lr_img, sr_img
            gc.collect()

        except Exception as e:
            logger.error(f"Error processing {image_file.name}: {str(e)}")
            continue

    logger.info(
        f"Processing completed. Successfully processed {processed_count}/{len(image_files)} images"
    )


def main():
    patch_size = 512
    overlap = patch_size // 16  # Use integer division instead of float division

    # Load model
    G = load_model()

    # Process all images in the folder
    input_folder = "input/TTDV_Lan/all"
    output_folder = "output/TTDV_Lan/all"
    process_folder(G, input_folder, output_folder, patch_size, overlap)

    input_folder = "input/vkist306/dark"
    output_folder = "output/vkist306/dark"
    process_folder(G, input_folder, output_folder, patch_size, overlap)


if __name__ == "__main__":
    main()
