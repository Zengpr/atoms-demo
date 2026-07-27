"use client";

import { motion } from "framer-motion";

interface TemplateCardProps {
  icon: string;
  name: string;
  description: string;
  onClick: () => void;
}

export function TemplateCard({
  icon,
  name,
  description,
  onClick,
}: TemplateCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.03 }}
      whileTap={{ scale: 0.97 }}
      onClick={onClick}
      className="group cursor-pointer rounded-xl border border-atoms-border bg-atoms-card p-5 transition-all hover:border-white/15 hover:shadow-lg hover:shadow-black/20 hover:bg-atoms-surface-hover"
    >
      <div className="mb-3 text-3xl group-hover:scale-110 transition-transform origin-left">{icon}</div>
      <h3 className="font-semibold text-zinc-100 mb-1 text-sm group-hover:text-white transition-colors">{name}</h3>
      <p className="text-xs text-zinc-500 leading-relaxed">{description}</p>
    </motion.div>
  );
}
