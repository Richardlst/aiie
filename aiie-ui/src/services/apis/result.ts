import axiosInstance from "./axios";
import { ResultPagingRequest, ResultPagingResponse } from "../../types/result";

export const getResultsPagingApi = async (params: ResultPagingRequest): Promise<ResultPagingResponse> => {
    const response = await axiosInstance.get("/result/paging", { params });
    return response.data as ResultPagingResponse;
};