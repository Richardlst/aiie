export interface GenerationResponse {
    image_url: string;
}

// Available AI Models for image generation
export type SDModel =
    | 'runwayml/stable-diffusion-v1-5'
    | 'dreamlike-art/dreamlike-photoreal-2.0'
    | 'nitrosocke/mo-di-diffusion'
    | 'nitrosocke/Ghibli-Diffusion'
    | 'stablediffusionapi/disney-pixal-cartoon';

// Model specifically for image expansion
export type ExpandModel = 'runwayml/stable-diffusion-inpainting';



// Text to Image request interface
export interface Text2ImgRequest {
    // Detailed description of the image you want to generate
    prompt: string;
    // Model to use for image generation
    model?: SDModel;
    // Elements to avoid in the generated image
    negative_prompt?: string;
    // Number of denoising steps (1-100)
    num_inference_steps?: number;
    // How strictly to follow the prompt (1-20)
    guidance_scale?: number;
    // Width in pixels (128-1024)
    width?: number;
    // Height in pixels (128-1024)
    height?: number;
}

// Image to Image request interface
export interface Img2ImgRequest {
    // Detailed description of how you want the source image to be transformed
    prompt: string;
    // URL of the source image you want to transform
    image_url: string;
    // Model to use for image transformation
    model?: SDModel;
    // Elements to avoid in the transformed image
    negative_prompt?: string;
    // Number of denoising steps (1-100)
    num_inference_steps?: number;
    // How closely the result follows your prompt (1-20)
    guidance_scale?: number;
    // How much to transform the original image (0-1)
    strength?: number;
    // Lower threshold for edge detection (0-255)
    canny_low_threshold?: number;
    // Upper threshold for edge detection (0-255)
    canny_high_threshold?: number;
    // Strength of edge guidance (0-1)
    controlnet_conditioning_scale?: number;
}

// Inpainting request interface
export interface InpaintRequest {
    // Detailed description of what content should be generated in masked areas
    prompt: string;
    // URL of the source image that requires inpainting
    image_url: string;
    // URL of the mask image defining areas to inpaint
    mask_url: string;
    // Optional reference image URL for IP-Adapter (omit = use source as self-reference)
    reference_image_url?: string;
    // Elements to avoid in the inpainted areas
    negative_prompt?: string;
    // Number of denoising steps (1-100)
    num_inference_steps?: number;
    // Controls how closely the inpainted result follows your prompt (1-20)
    guidance_scale?: number;
    // How much to change the masked area (0-1)
    strength?: number;
    // Mask edge softness (Gaussian blur radius)
    mask_blur_radius?: number;
    // IP-Adapter influence weight (0-1)
    ip_adapter_scale?: number;
}

// Image expansion request interface
export interface ExpandRequest {
    // Description of how the expanded areas should look
    prompt: string;
    // URL of the source image you want to expand
    image_url: string;
    // Number of pixels to expand the image upward
    expand_top: number;
    // Number of pixels to expand the image downward
    expand_bottom: number;
    // Number of pixels to expand the image to the left
    expand_left: number;
    // Number of pixels to expand the image to the right
    expand_right: number;
    // Model to use for expansion
    model?: ExpandModel;
    // Elements to avoid in the expanded areas
    negative_prompt?: string;
    // Number of denoising steps (1-100)
    num_inference_steps?: number;
    // Controls how closely the expanded areas match the original (1-20)
    guidance_scale?: number;
}

// Image segmentation request interface
export interface SegmentRequest {
    // URL of the image you want to segment
    image_url: string;
    // Text prompts specifying what objects to segment
    prompts: string;
}

// Image colorization request interface
export interface ColorizationRequest {
    // URL of the black and white or grayscale image to colorize
    image_url: string;
    // Optional prompt to guide colorization style
    prompt?: string;
    // Controls how vibrant the colors will be (0.1-1.0)
    color_intensity?: number;
    // Number of denoising steps (10-100)
    num_inference_steps?: number;
    // How closely to follow the prompt (1-20)
    guidance_scale?: number;
}

// Face refinement request interface
export interface FaceRefineRequest {
    // URL of the image with faces to refine
    image_url: string;
    // Super-resolution upscale factor (1-4)
    upscale?: number;
    // If true, only restore the center/largest face
    only_center_face?: boolean;
    // Balance between restored detail (1.0) and original identity (0.0)
    weight?: number;
}