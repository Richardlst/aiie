import axiosInstance from './axios';
import {
    GenerationResponse,
    Text2ImgRequest,
    Img2ImgRequest,
    InpaintRequest,
    SegmentRequest,
    ExpandRequest,
    ColorizationRequest,
    FaceRefineRequest
} from "../../types/image";
const AGENT_API_URL = import.meta.env.VITE_AGENT_API_URL;

export const superResolutionApi = async (image_url: string): Promise<GenerationResponse> => {
    const response = await axiosInstance.post(`${AGENT_API_URL}/image/sr`, { image_url });
    const responseData = response.data as GenerationResponse;
    return responseData;
};

export const textToImageApi = async (data: Text2ImgRequest): Promise<GenerationResponse> => {
    const response = await axiosInstance.post(`${AGENT_API_URL}/image/txt2img`, data);
    const responseData = response.data as GenerationResponse;
    return responseData;
};

export const imageToImageApi = async (data: Img2ImgRequest): Promise<GenerationResponse> => {
    const response = await axiosInstance.post(`${AGENT_API_URL}/image/img2img`, data);
    const responseData = response.data as GenerationResponse;
    return responseData;
};

export const inpaintApi = async (data: InpaintRequest): Promise<GenerationResponse> => {
    const response = await axiosInstance.post(`${AGENT_API_URL}/image/inpaint`, data);
    const responseData = response.data as GenerationResponse;
    return responseData;
};

export const segmentApi = async (data: SegmentRequest): Promise<GenerationResponse> => {
    const response = await axiosInstance.post(`${AGENT_API_URL}/image/segment`, data);
    const responseData = response.data as GenerationResponse;
    return responseData;
};

export const expandApi = async (data: ExpandRequest): Promise<GenerationResponse> => {
    const response = await axiosInstance.post(`${AGENT_API_URL}/image/expand`, data, {
        timeout: 10 * 60 * 1000 // 10 minutes
    });
    const responseData = response.data as GenerationResponse;
    return responseData;
};

export const colorizationApi = async (data: ColorizationRequest): Promise<GenerationResponse> => {
    const response = await axiosInstance.post(`${AGENT_API_URL}/image/colorization`, data);
    const responseData = response.data as GenerationResponse;
    return responseData;
};

export const faceRefineApi = async (data: FaceRefineRequest): Promise<GenerationResponse> => {
    const response = await axiosInstance.post(`${AGENT_API_URL}/image/face-refine`, data);
    const responseData = response.data as GenerationResponse;
    return responseData;
};