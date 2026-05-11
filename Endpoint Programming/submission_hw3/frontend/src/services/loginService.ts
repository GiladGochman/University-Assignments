import api from '../axiosConfig';
export interface LoginData { username:string; password:string }
export const loginRequest = (creds:LoginData) => api.post('/login', creds);