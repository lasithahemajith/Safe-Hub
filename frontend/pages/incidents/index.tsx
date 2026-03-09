import Head from "next/head";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Navbar from "@/components/layout/Navbar";
import IncidentCard from "@/components/incidents/IncidentCard";
import { incidentService } from "@/services/incidentService";
import Link from "next/link";
import { Plus } from "lucide-react";

export default function IncidentsPage() {
  const [page, setPage] = useState(1);
  const [filterType, setFilterType] = useState("");
  const [filterSeverity, setFilterSeverity] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["incidents", page, filterType, filterSeverity],
    queryFn: () =>
      incidentService.list({
        page,
        per_page: 12,
        disaster_type: filterType || undefined,
        severity: filterSeverity || undefined,
      }),
  });

  const incidents = data?.items || [];
  const pages = data?.pages || 1;

  return (
    <>
      <Head><title>Incidents – SafeNZ</title></Head>
      <Navbar />
      <div className="min-h-[calc(100vh-64px)] bg-gray-50 dark:bg-gray-900 py-8 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold">Disaster Incidents</h1>
            <Link href="/incidents/report" className="btn-primary flex items-center gap-2">
              <Plus className="w-4 h-4" /> Report Incident
            </Link>
          </div>

          {/* Filters */}
          <div className="flex gap-3 mb-6 flex-wrap">
            <select
              value={filterType}
              onChange={(e) => { setFilterType(e.target.value); setPage(1); }}
              className="input-field w-auto"
            >
              <option value="">All types</option>
              <option value="earthquake">🌍 Earthquake</option>
              <option value="flood">🌊 Flood</option>
              <option value="landslide">🏔️ Landslide</option>
              <option value="storm">⛈️ Storm</option>
              <option value="fire">🔥 Fire</option>
            </select>
            <select
              value={filterSeverity}
              onChange={(e) => { setFilterSeverity(e.target.value); setPage(1); }}
              className="input-field w-auto"
            >
              <option value="">All severities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>

          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="card animate-pulse h-40 bg-gray-200 dark:bg-gray-700" />
              ))}
            </div>
          ) : incidents.length === 0 ? (
            <div className="text-center py-20 text-gray-500">
              <p className="text-xl mb-2">No incidents found</p>
              <p className="text-sm">Be the first to report a disaster incident</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {incidents.map((incident) => (
                <IncidentCard key={incident.id} incident={incident} />
              ))}
            </div>
          )}

          {/* Pagination */}
          {pages > 1 && (
            <div className="flex justify-center gap-2 mt-8">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="btn-secondary"
              >
                Previous
              </button>
              <span className="py-2 px-4 text-sm text-gray-600 dark:text-gray-400">
                Page {page} of {pages}
              </span>
              <button
                onClick={() => setPage(Math.min(pages, page + 1))}
                disabled={page === pages}
                className="btn-secondary"
              >
                Next
              </button>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
