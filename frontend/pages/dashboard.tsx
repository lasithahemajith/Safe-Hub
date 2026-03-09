import Head from "next/head";
import { useQuery } from "@tanstack/react-query";
import Navbar from "@/components/layout/Navbar";
import { useAuthStore } from "@/store/authStore";
import { incidentService } from "@/services/incidentService";
import { alertService, resourceService } from "@/services/dataService";
import { useRouter } from "next/router";
import { useEffect } from "react";
import IncidentCard from "@/components/incidents/IncidentCard";
import { AlertTriangle, Bell, Wrench, TrendingUp } from "lucide-react";

export default function Dashboard() {
  const { user, isAuthenticated } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) router.push("/login");
  }, [isAuthenticated, router]);

  const { data: incidentsData } = useQuery({
    queryKey: ["incidents-recent"],
    queryFn: () => incidentService.list({ per_page: 6 }),
    enabled: isAuthenticated,
  });

  const { data: alertsData } = useQuery({
    queryKey: ["alerts-recent"],
    queryFn: () => alertService.list({ per_page: 5 }),
    enabled: isAuthenticated,
  });

  const { data: resources } = useQuery({
    queryKey: ["resources"],
    queryFn: () => resourceService.list(),
    enabled: isAuthenticated,
  });

  const incidents = incidentsData?.items || [];
  const alerts = alertsData?.items || [];

  return (
    <>
      <Head><title>Dashboard – SafeNZ</title></Head>
      <Navbar />
      <div className="min-h-[calc(100vh-64px)] bg-gray-50 dark:bg-gray-900 py-8 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <h1 className="text-2xl font-bold">Dashboard</h1>
            <p className="text-gray-600 dark:text-gray-400">Welcome, {user?.name} · {user?.role}</p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {[
              {
                label: "Total Incidents",
                value: incidentsData?.total || 0,
                icon: <AlertTriangle className="w-6 h-6 text-red-500" />,
                bg: "bg-red-50 dark:bg-red-900/20",
              },
              {
                label: "Active Alerts",
                value: alertsData?.total || 0,
                icon: <Bell className="w-6 h-6 text-orange-500" />,
                bg: "bg-orange-50 dark:bg-orange-900/20",
              },
              {
                label: "Resources",
                value: resources?.length || 0,
                icon: <Wrench className="w-6 h-6 text-blue-500" />,
                bg: "bg-blue-50 dark:bg-blue-900/20",
              },
              {
                label: "Resolved",
                value: incidents.filter((i) => i.status === "resolved").length,
                icon: <TrendingUp className="w-6 h-6 text-green-500" />,
                bg: "bg-green-50 dark:bg-green-900/20",
              },
            ].map((stat) => (
              <div key={stat.label} className={`card ${stat.bg}`}>
                <div className="flex items-center gap-3">
                  {stat.icon}
                  <div>
                    <p className="text-2xl font-bold">{stat.value}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Recent Incidents & Alerts */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <h2 className="text-lg font-semibold mb-4">Recent Incidents</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {incidents.map((incident) => (
                  <IncidentCard key={incident.id} incident={incident} />
                ))}
              </div>
            </div>
            <div>
              <h2 className="text-lg font-semibold mb-4">Recent Alerts</h2>
              <div className="flex flex-col gap-3">
                {(alerts as Array<{
                  id: string;
                  title: string;
                  severity: string;
                  region: string;
                  created_at: string;
                }>).map((alert) => (
                  <div key={alert.id} className="card border-l-4 border-red-400">
                    <p className="font-medium text-sm">{alert.title}</p>
                    <p className="text-xs text-gray-500 mt-1">{alert.region} · {alert.severity}</p>
                  </div>
                ))}
                {alerts.length === 0 && (
                  <p className="text-gray-500 text-sm">No alerts</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
