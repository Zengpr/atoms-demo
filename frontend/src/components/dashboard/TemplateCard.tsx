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
      className="group cursor-pointer rounded-xl border border-atoms-border bg-atoms-card p-5 transition-all hover:border-atoms-accent/40 hover:shadow-lg hover:shadow-atoms-accent/5"
    >
      <div className="mb-3 text-3xl">{icon}</div>
      <h3 className="font-semibold text-zinc-100 mb-1">{name}</h3>
      <p className="text-sm text-zinc-400">{description}</p>
    </motion.div>
  );
}
