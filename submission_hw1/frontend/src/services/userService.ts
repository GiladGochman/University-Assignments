import api from '../axiosConfig';
export interface CreateUserData { name:string; email:string; username:string; password:string }
export const createUser = (data:CreateUserData) => api.post('/users', data);