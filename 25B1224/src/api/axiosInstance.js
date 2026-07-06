import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const axiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api`,
});

axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem("accessToken");

  const publicRoutes = [
    "/doctors/",
    "/departments/",
    "/auth/login/",
    "/auth/register/",
    "/auth/refresh/",
  ];

  const isPublicRoute = publicRoutes.some((route) =>
    config.url?.startsWith(route)
  );

  if (token && !isPublicRoute) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export default axiosInstance;