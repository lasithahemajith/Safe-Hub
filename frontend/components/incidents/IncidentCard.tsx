import { Incident } from "@/services/incidentService";
import SeverityBadge from "@/components/ui/SeverityBadge";
import { formatDistanceToNow } from "date-fns";
import Link from "next/link";
import { MapPin, ThumbsUp, MessageCircle } from "lucide-react";

interface Props {
  incident: Incident;
}

const DISASTER_EMOJI: Record<string, string> = {
  earthquake: "🌍",
  flood: "🌊",
  landslide: "🏔️",
  storm: "⛈️",
  fire: "🔥",
  other: "⚠️",
};

export default function IncidentCard({ incident }: Props) {
  return (
    <Link href={`/incidents/${incident.id}`}>
      <div className="card hover:shadow-lg transition-shadow cursor-pointer border border-gray-200 dark:border-gray-700">
        <div className="flex items-start justify-between mb-2">
          <span className="text-2xl">{DISASTER_EMOJI[incident.disaster_type] || "⚠️"}</span>
          <SeverityBadge severity={incident.severity} />
        </div>
        <h3 className="font-semibold text-gray-900 dark:text-white mb-1 line-clamp-2">{incident.title}</h3>
        <p className="text-gray-600 dark:text-gray-400 text-sm line-clamp-2 mb-3">{incident.description}</p>
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <span className="flex items-center gap-1">
            <MapPin className="w-3 h-3" />
            {incident.latitude.toFixed(4)}, {incident.longitude.toFixed(4)}
          </span>
          <span>{formatDistanceToNow(new Date(incident.created_at), { addSuffix: true })}</span>
        </div>
        <div className="flex items-center gap-3 mt-2 text-xs text-gray-400">
          <span className="flex items-center gap-1">
            <ThumbsUp className="w-3 h-3" /> {incident.vote_count}
          </span>
          <span className="capitalize px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded-full">
            {incident.status.replace("_", " ")}
          </span>
        </div>
      </div>
    </Link>
  );
}
