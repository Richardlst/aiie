import axiosInstance from './axios';
import { UpdateUserRequest, User } from '../../types/user';

export const getUserApi = async (): Promise<{ data: User; status: number }> => {
    const response = await axiosInstance.get('/user');
    return response;
};

export const updateUserApi = async (userData: UpdateUserRequest): Promise<{ data: User; status: number }> => {
    const response = await axiosInstance.put('/user', userData);
    return response;
};