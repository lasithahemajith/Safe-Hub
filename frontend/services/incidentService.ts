import api from "./api";

export type DisasterType = "earthquake" | "flood" | "landslide" | "storm" | "fire" | "other";
export type SeverityLevel = "low" | "medium" | "high" | "critical";
export type IncidentStatus = "reported" | "confirmed" | "in_progress" | "resolved" | "closed";

export interface Incident {
  id: string;
  title: string;
  description: string;
  disaster_type: DisasterType;
  severity: SeverityLevel;
  latitude: number;
  longitude: number;
  status: IncidentStatus;
  reported_by: string;
  image_urls: string[];
  ai_damage_level?: string;
  ai_confidence?: number;
  vote_count: number;
  created_at: string;
  updated_at: string;
}

export interface CreateIncidentData {
  title: string;
  description: string;
  disaster_type: DisasterType;
  severity: SeverityLevel;
  latitude: number;
  longitude: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

export const incidentService = {
  list: (params?: {
    page?: number;
    per_page?: number;
    disaster_type?: string;
    severity?: string;
    status?: string;
  }) =>
    api
      .get<PaginatedResponse<Incident>>("/incidents", { params })
      .then((r) => r.data),

  get: (id: string) =>
    api.get<Incident>(`/incidents/${id}`).then((r) => r.data),

  create: (data: CreateIncidentData) =>
    api.post<Incident>("/incidents", data).then((r) => r.data),

  update: (id: string, data: Partial<Incident>) =>
    api.put<Incident>(`/incidents/${id}`, data).then((r) => r.data),

  getNearby: (lat: number, lon: number, radiusKm = 10) =>
    api
      .get<Incident[]>("/incidents/nearby", {
        params: { lat, lon, radius_km: radiusKm },
      })
      .then((r) => r.data),

  uploadImages: (id: string, files: File[]) => {
    const formData = new FormData();
    files.forEach((f) => formData.append("files", f));
    return api
      .post(`/incidents/${id}/images`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      })
      .then((r) => r.data);
  },

  vote: (id: string) =>
    api.post(`/incidents/${id}/vote`).then((r) => r.data),

  addComment: (id: string, content: string) =>
    api.post(`/incidents/${id}/comments`, { content }).then((r) => r.data),

  getComments: (id: string) =>
    api.get(`/incidents/${id}/comments`).then((r) => r.data),
};
