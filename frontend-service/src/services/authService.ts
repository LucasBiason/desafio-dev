import api from './api';

interface LoginCredentials {
  username: string;
  password: string;
}

export const authService = {
  async login(credentials: LoginCredentials) {
    const response = await api.post('/api/user/auth/v1/login/', credentials);
    // Backend returns: { encoded_token, valid_until, user }
    return {
      access_token: response.data.encoded_token,
      user: response.data.user,
    };
  },

  async validate() {
    const response = await api.post('/api/user/auth/v1/validate/');
    return response.data;
  },
};
