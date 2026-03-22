import axiosInstance from './axios';

export const loginApi = async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await axiosInstance.post('/auth/login', formData, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    });

    return response;
};

export const registerApi = async (email: string, password: string) => {
    const response = await axiosInstance.post('/auth/register', { email, password });
    return response;
};

export const verifyEmailApi = async (token: string) => {
    const response = await axiosInstance.post('/auth/verify-email', { token });
    return response;
};

export const sendVerificationEmailApi = async (email: string) => {
    const response = await axiosInstance.post('/auth/resend-email', { email });
    return response;
};

export const forgotPasswordApi = async (email: string) => {
    const response = await axiosInstance.post('/auth/forgot-password', { email });
    return response;
};

export const resetPasswordApi = async (token: string, newPassword: string) => {
    const response = await axiosInstance.post('/auth/reset-password', {
        token,
        password: newPassword
    });
    return response;
};
