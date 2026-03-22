
export interface FileResponse {
    filename: string;
    url: string;
}

export interface UploadImage {
    filename: string;
    url: string;
}

export interface UploadResponse {
    data: UploadImage;
}

export interface UploadMultipleResponse {
    data: UploadImage[];
}
