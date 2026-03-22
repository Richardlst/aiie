export enum ResultType {
    SR = "SR", // Super Resolution
    T2I = "T2I", // Text to Image
    I2I = "I2I", // Image to Image
    INP = "INP", // Inpaint
    EXP = "EXP", // Expand
    SEG = "SEG", // Segment
    COL = "COL", // Colorization
    FR = "FR",  // Face Refine
}

export interface ResultResponse {
    url: string;
    type: ResultType;
    id: string;
    created_at: string;
    updated_at: string;
}

export interface ResultPagingRequest {
    page?: number;
    page_size?: number;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
    search?: string;
    filter?: Record<string, any>;
}

export interface ResultPagingResponse {
    data: ResultResponse[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
}