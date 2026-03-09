import api from "./api";
import { SeverityLevel, PaginatedResponse } from "./incidentService";

export interface Alert {
  id: string;
  title: string;
  message: string;
  region: string;
  severity: SeverityLevel;
  created_by: string;
  created_at: string;
}

export interface Shelter {
  id: string;
  name: string;
  capacity: number;
  available_space: number;
  latitude: number;
  longitude: number;
  contact_number: string;
  address: string;
  is_active: boolean;
  distance_km?: number;
}

export interface Resource {
  id: string;
  resource_type: string;
  status: string;
  latitude: number;
  longitude: number;
  assigned_incident?: string;
  description: string;
  contact: string;
}

export const alertService = {
  list: (params?: { page?: number; per_page?: number }) =>
    api
      .get<PaginatedResponse<Alert>>("/alerts", { params })
      .then((r) => r.data),

  create: (data: Omit<Alert, "id" | "created_by" | "created_at">) =>
    api.post<Alert>("/alerts", data).then((r) => r.data),
};

export const shelterService = {
  list: () => api.get<Shelter[]>("/shelters").then((r) => r.data),

  getNearby: (lat: number, lon: number, radiusKm = 20) =>
    api
      .get<Shelter[]>("/shelters/nearby", {
        params: { lat, lon, radius_km: radiusKm },
      })
      .then((r) => r.data),
};

export const resourceService = {
  list: () => api.get<Resource[]>("/resources").then((r) => r.data),

  update: (id: string, data: Partial<Resource>) =>
    api.patch<Resource>(`/resources/${id}`, data).then((r) => r.data),
};
