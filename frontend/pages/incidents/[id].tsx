import Head from "next/head";
import { useRouter } from "next/router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Navbar from "@/components/layout/Navbar";
import SeverityBadge from "@/components/ui/SeverityBadge";
import { incidentService } from "@/services/incidentService";
import { useAuthStore } from "@/store/authStore";
import { formatDistanceToNow } from "date-fns";
import toast from "react-hot-toast";
import { ThumbsUp, MapPin } from "lucide-react";

export default function IncidentDetail() {
  const router = useRouter();
  const { id } = router.query as { id: string };
  const { user } = useAuthStore();
  const qc = useQueryClient();

  const { data: incident, isLoading } = useQuery({
    queryKey: ["incident", id],
    queryFn: () => incidentService.get(id),
    enabled: !!id,
  });

  const { data: comments } = useQuery({
    queryKey: ["comments", id],
    queryFn: () => incidentService.getComments(id),
    enabled: !!id,
  });

  const voteMutation = useMutation({
    mutationFn: () => incidentService.vote(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["incident", id] });
      toast.success("Vote recorded!");
    },
    onError: () => toast.error("Already voted or error"),
  });

  if (isLoading) return (
    <>
      <Navbar />
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    </>
  );

  if (!incident) return (
    <>
      <Navbar />
      <div className="text-center py-20 text-gray-500">Incident not found</div>
    </>
  );

  return (
    <>
      <Head><title>{incident.title} – SafeNZ</title></Head>
      <Navbar />
      <div className="min-h-[calc(100vh-64px)] bg-gray-50 dark:bg-gray-900 py-8 px-4">
        <div className="max-w-3xl mx-auto">
          <div className="card mb-4">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h1 className="text-2xl font-bold mb-1">{incident.title}</h1>
                <div className="flex items-center gap-2 flex-wrap">
                  <SeverityBadge severity={incident.severity} />
                  <span className="text-sm capitalize text-gray-600 dark:text-gray-400">
                    {incident.disaster_type}
                  </span>
                  <span className="text-sm text-gray-500">
                    {formatDistanceToNow(new Date(incident.created_at), { addSuffix: true })}
                  </span>
                </div>
              </div>
              <span className="capitalize px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm">
                {incident.status.replace("_", " ")}
              </span>
            </div>

            <p className="text-gray-700 dark:text-gray-300 mb-4">{incident.description}</p>

            <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
              <MapPin className="w-4 h-4" />
              <span>{incident.latitude.toFixed(5)}, {incident.longitude.toFixed(5)}</span>
            </div>

            {incident.ai_damage_level && (
              <div className="bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-700 rounded-lg p-3 mb-4">
                <p className="text-sm font-medium text-purple-800 dark:text-purple-300">
                  🤖 AI Damage Analysis: <span className="font-bold capitalize">{incident.ai_damage_level}</span>
                  {incident.ai_confidence && (
                    <span className="ml-2 text-xs">({Math.round(incident.ai_confidence * 100)}% confidence)</span>
                  )}
                </p>
              </div>
            )}

            {incident.image_urls.length > 0 && (
              <div className="grid grid-cols-2 gap-2 mb-4">
                {incident.image_urls.map((url, i) => (
                  <img key={i} src={url} alt={`Incident ${i + 1}`} className="rounded-lg object-cover h-40 w-full" />
                ))}
              </div>
            )}

            {user && (
              <button
                onClick={() => voteMutation.mutate()}
                disabled={voteMutation.isPending}
                className="flex items-center gap-2 btn-secondary"
              >
                <ThumbsUp className="w-4 h-4" />
                Confirm ({incident.vote_count})
              </button>
            )}
          </div>

          {/* Comments */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Community Reports ({(comments as unknown[])?.length || 0})</h2>
            {Array.isArray(comments) && comments.map((c: { id: string; content: string; created_at: string }) => (
              <div key={c.id} className="border-b border-gray-200 dark:border-gray-700 pb-3 mb-3 last:border-0">
                <p className="text-sm">{c.content}</p>
                <p className="text-xs text-gray-400 mt-1">
                  {formatDistanceToNow(new Date(c.created_at), { addSuffix: true })}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
