import Head from "next/head";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dynamic from "next/dynamic";
import Navbar from "@/components/layout/Navbar";
import IncidentCard from "@/components/incidents/IncidentCard";
import { incidentService, Incident } from "@/services/incidentService";

const DisasterMap = dynamic(() => import("@/components/map/DisasterMap"), { ssr: false });

export default function MapPage() {
  const [selected, setSelected] = useState<Incident | null>(null);
  const { data, isLoading } = useQuery({
    queryKey: ["incidents"],
    queryFn: () => incidentService.list({ per_page: 100 }),
  });

  const incidents = data?.items || [];

  return (
    <>
      <Head>
        <title>Disaster Map – SafeNZ</title>
        <link
          rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          crossOrigin=""
        />
      </Head>
      <Navbar />
      <div className="flex h-[calc(100vh-64px)]">
        {/* Sidebar */}
        <aside className="w-80 overflow-y-auto bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 p-4 flex-shrink-0">
          <h2 className="text-lg font-bold mb-4">Active Incidents ({incidents.length})</h2>
          {isLoading ? (
            <p className="text-gray-500">Loading…</p>
          ) : incidents.length === 0 ? (
            <p className="text-gray-500">No active incidents</p>
          ) : (
            <div className="flex flex-col gap-3">
              {incidents.map((incident) => (
                <div
                  key={incident.id}
                  className={`cursor-pointer rounded-lg transition-all ${selected?.id === incident.id ? "ring-2 ring-blue-500" : ""}`}
                  onClick={() => setSelected(incident)}
                >
                  <IncidentCard incident={incident} />
                </div>
              ))}
            </div>
          )}
        </aside>

        {/* Map */}
        <div className="flex-1 relative">
          <DisasterMap
            incidents={incidents}
            onIncidentClick={setSelected}
          />
          {selected && (
            <div className="absolute bottom-4 left-4 right-4 md:right-auto md:w-80 card shadow-xl z-50">
              <div className="flex justify-between items-start">
                <h3 className="font-bold">{selected.title}</h3>
                <button onClick={() => setSelected(null)} className="text-gray-400 hover:text-gray-600 text-xl leading-none">×</button>
              </div>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{selected.description}</p>
              <div className="mt-2 flex gap-2 text-xs">
                <span className="capitalize font-medium">{selected.disaster_type}</span>
                <span>·</span>
                <span className="capitalize">{selected.severity}</span>
                <span>·</span>
                <span className="capitalize">{selected.status.replace("_", " ")}</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
