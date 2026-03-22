import { UploadMultipleResponse, UploadResponse } from '../../types/storage';
import axiosInstance from './axios';
import type { UploadFile } from "antd/es/upload/interface";

const STO_URL = import.meta.env.VITE_AGENT_API_URL;

export const saveImage = async (image: UploadFile) => {
    const formData = new FormData();
    formData.append('file', image.originFileObj as Blob);

    const response = await axiosInstance.post(`${STO_URL}/upload`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    const responseData = response.data as UploadResponse;

    return responseData;
}

export const saveMultipleImage = async (images: UploadFile[]) => {
    const formData = new FormData();
    images.forEach((image) => {
        formData.append('files', image.originFileObj as Blob);
    });

    const response = await axiosInstance.post(`${STO_URL}/upload/multiple`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    const responseData = response.data as UploadMultipleResponse;
    return responseData;
}

export const deleteImage = async (filename: string) => {
    const response = await axiosInstance.delete(`${STO_URL}/delete/${filename}`);
    return response;
}; 