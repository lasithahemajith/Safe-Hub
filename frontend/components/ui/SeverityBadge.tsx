import { SeverityLevel } from "@/services/incidentService";

const COLOURS: Record<SeverityLevel, string> = {
  critical: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 border border-red-300",
  high: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200 border border-orange-300",
  medium: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 border border-yellow-300",
  low: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 border border-green-300",
};

export default function SeverityBadge({ severity }: { severity: SeverityLevel }) {
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-semibold uppercase ${COLOURS[severity]}`}>
      {severity}
    </span>
  );
}
