import axiosInstance from './axios';

export const getConversationsApi = async () => {
    const response = await axiosInstance.get('/conversation');
    return response;
};

export const createConversationApi = async () => {
    const response = await axiosInstance.post('/conversation');
    return response;
};