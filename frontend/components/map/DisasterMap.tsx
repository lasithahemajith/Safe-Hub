"use client";
import { useEffect, useRef } from "react";
import type { Incident } from "@/services/incidentService";

interface Props {
  incidents: Incident[];
  center?: [number, number];
  zoom?: number;
  onIncidentClick?: (incident: Incident) => void;
}

const SEVERITY_COLORS: Record<string, string> = {
  critical: "#ef4444",
  high: "#f97316",
  medium: "#eab308",
  low: "#22c55e",
};

export default function DisasterMap({ incidents, center = [-41.2865, 174.7762], zoom = 6, onIncidentClick }: Props) {
  const mapRef = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<unknown>(null);
  const markersRef = useRef<unknown[]>([]);

  useEffect(() => {
    if (typeof window === "undefined" || !mapRef.current) return;
    if (mapInstance.current) return;

    import("leaflet").then((L) => {
      const map = L.map(mapRef.current!, { center, zoom });
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
      }).addTo(map);
      mapInstance.current = map;
      renderMarkers(L, map);
    });

    return () => {
      if (mapInstance.current) {
        (mapInstance.current as { remove: () => void }).remove();
        mapInstance.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!mapInstance.current) return;
    import("leaflet").then((L) => {
      const map = mapInstance.current as { addLayer: (l: unknown) => void; removeLayer: (l: unknown) => void };
      markersRef.current.forEach((m) => map.removeLayer(m));
      markersRef.current = [];
      renderMarkers(L, mapInstance.current as Parameters<typeof renderMarkers>[1]);
    });
  }, [incidents]);

  function renderMarkers(L: typeof import("leaflet"), map: unknown) {
    const leafletMap = map as { addLayer: (l: unknown) => void };
    incidents.forEach((incident) => {
      const color = SEVERITY_COLORS[incident.severity] || "#6b7280";
      const icon = L.divIcon({
        html: `<div style="
          width:24px;height:24px;border-radius:50%;
          background:${color};border:3px solid white;
          box-shadow:0 2px 6px rgba(0,0,0,0.3);
        "></div>`,
        className: "",
        iconSize: [24, 24],
        iconAnchor: [12, 12],
      });
      const marker = L.marker([incident.latitude, incident.longitude], { icon })
        .bindPopup(`
          <div style="min-width:200px">
            <strong>${incident.title}</strong><br/>
            <em>${incident.disaster_type}</em> – ${incident.severity}<br/>
            <small>${incident.status}</small>
          </div>
        `);
      if (onIncidentClick) {
        marker.on("click", () => onIncidentClick(incident));
      }
      marker.addTo(leafletMap as Parameters<typeof marker.addTo>[0]);
      markersRef.current.push(marker);
    });
  }

  return (
    <div
      ref={mapRef}
      style={{ height: "100%", width: "100%", minHeight: "400px" }}
      className="rounded-xl overflow-hidden z-0"
    />
  );
}
