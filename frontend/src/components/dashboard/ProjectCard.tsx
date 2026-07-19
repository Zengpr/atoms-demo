"use client";

import { format } from "date-fns";
import { motion } from "framer-motion";
import { Badge } from "@/components/ui/Badge";
import { cn } from "@/lib/utils";
import type { Project } from "@/lib/types";
import { useRouter } from "next/navigation";

interface ProjectCardProps {
  project: Project;
}

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
      className="group cursor-pointer rounded-xl border border-atoms-border bg-atoms-card p-4 transition-colors hover:border-atoms-accent/40"
    >
      <div className="mb-3 h-32 rounded-lg bg-atoms-dark/80 flex items-center justify-center overflow-hidden">
        {project.thumbnail ? (
          <img
            src={project.thumbnail}
            alt={project.name}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="text-4xl opacity-30">
            {project.mode === "engineer" ? "\u{1F4BB}" : project.mode === "team" ? "\u{1F465}" : project.mode === "race" ? "\u{26A1}" : "\u{1F50D}"}
          </div>
        )}
      </div>
      <div className="space-y-2">
        <h3 className="font-semibold text-zinc-100 truncate">
          {project.name}
        </h3>
        <p className="text-sm text-zinc-400 line-clamp-2">
          {project.description}
        </p>
        <div className="flex items-center gap-2">
          <Badge variant={statusVariant}>{project.status}</Badge>
          <Badge>{project.mode}</Badge>
        </div>
        <p className="text-xs text-zinc-500">
          {format(new Date(project.createdAt), "MMM d, yyyy")}
        </p>
      </div>
    </motion.div>
  );
}
