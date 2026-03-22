import { AddMessageRequest } from "../../types/message";
import axiosInstance from "./axios";

export const getMessagesByConversationIdApi = async (conversationId: string) => {
    const response = await axiosInstance.get(`/message/${conversationId}`);
    return response;
};

export const addMessageApi = async (request: AddMessageRequest) => {
    const response = await axiosInstance.post(`/message`, request);
    return response;
};