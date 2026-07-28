"use client";

import { format } from "date-fns";
import { motion } from "framer-motion";
import { Badge } from "@/components/ui/Badge";
import type { Project } from "@/lib/types";
import { useRouter } from "next/navigation";

interface ProjectCardProps {
  project: Project;
}

const MODE_LABELS: Record<string, string> = {
  engineer: "Engineer",
  team: "Team",
  race: "Race",
  research: "Research",
  review: "Review",
};

const STATUS_LABELS: Record<string, string> = {
  completed: "Completed",
  building: "Building",
  draft: "Draft",
};

export function ProjectCard({ project }: ProjectCardProps) {
  const router = useRouter();

  const statusVariant =
    project.status === "completed"
      ? "success"
      : project.status === "building"
        ? "warning"
        : "default";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={() => router.push(`/workspace/${project.id}`)}
      className="group cursor-pointer rounded-xl border border-atoms-border bg-atoms-card p-4 transition-all hover:border-white/15 hover:shadow-lg hover:shadow-black/20"
    >
      <div className="mb-3 h-28 rounded-lg bg-atoms-dark/80 flex items-center justify-center overflow-hidden relative">
        {project.thumbnail ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={project.thumbnail}
            alt={project.name}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="text-3xl opacity-20 group-hover:opacity-30 transition-opacity">
            {project.mode === "engineer" ? "\u{1F4BB}" : project.mode === "team" ? "\u{1F465}" : project.mode === "race" ? "\u{26A1}" : "\u{1F50D}"}
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-atoms-card/80 to-transparent" />
      </div>
      <div className="space-y-1.5">
        <h3 className="font-medium text-zinc-100 truncate text-sm group-hover:text-white transition-colors">
          {project.name}
        </h3>
        {project.description && (
          <p className="text-xs text-zinc-500 line-clamp-2 leading-relaxed">
            {project.description}
          </p>
        )}
        <div className="flex items-center gap-2 pt-1">
          <Badge variant={statusVariant}>{STATUS_LABELS[project.status] ?? project.status}</Badge>
          <Badge>{MODE_LABELS[project.mode] ?? project.mode}</Badge>
        </div>
        <p className="text-[11px] text-zinc-600">
          {format(new Date(project.createdAt), "yyyy/MM/dd")}
        </p>
      </div>
    </motion.div>
  );
}
