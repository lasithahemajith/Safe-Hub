import api from "./api";

export interface RegisterData {
  name: string;
  email: string;
  phone?: string;
  password: string;
  role?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  phone?: string;
  role: "citizen" | "responder" | "admin";
  verified: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export const authService = {
  register: (data: RegisterData) =>
    api.post<User>("/auth/register", data).then((r) => r.data),

  login: async (data: LoginData): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>("/auth/login", data);
    const { access_token, refresh_token } = response.data;
    if (typeof window !== "undefined") {
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("refresh_token", refresh_token);
    }
    return response.data;
  },

  logout: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
  },

  getMe: () => api.get<User>("/auth/me").then((r) => r.data),

  requestPasswordReset: (email: string) =>
    api.post("/auth/reset-password/request", { email }),

  resetPassword: (token: string, new_password: string) =>
    api.post("/auth/reset-password", { token, new_password }),
};
