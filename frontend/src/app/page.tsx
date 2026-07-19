"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { AGENTS } from "@/lib/agents";
import { Cpu, Eye, Rocket, Sparkles } from "lucide-react";

const FEATURES = [
  {
    icon: Cpu,
    title: "Multi-Agent Workflow",
    description:
      "5 specialized AI agents collaborate to design, architect, and build your application from scratch.",
  },
  {
    icon: Eye,
    title: "Real-time Preview",
    description:
      "See your application come to life instantly as agents generate code, with live preview in the browser.",
  },
  {
    icon: Rocket,
    title: "One-Click Deploy",
    description:
      "From idea to production in minutes. Deploy your generated application with a single click.",
  },
];

export default function HomePage() {
  return (
    <div className="min-h-full bg-atoms-dark overflow-hidden">
      {/* Gradient background */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-b from-atoms-accent/8 via-transparent to-transparent" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-atoms-accent/5 rounded-full blur-3xl" />
      </div>

      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-4 border-b border-atoms-border/50">
        <div className="flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-atoms-accent" />
          <span className="text-lg font-bold text-white">Atoms Demo</span>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/login">
            <Button variant="ghost" size="sm">
              Sign In
            </Button>
          </Link>
          <Link href="/login?tab=register">
            <Button size="sm">Get Started</Button>
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative flex flex-col items-center justify-center px-6 pt-24 pb-20 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-atoms-border bg-atoms-card/60 px-4 py-1.5 text-sm text-zinc-400 backdrop-blur">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            Powered by Multi-Agent AI
          </div>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="max-w-4xl text-5xl font-bold leading-tight tracking-tight text-white sm:text-6xl lg:text-7xl"
        >
          Turn Ideas into Apps
          <br />
          <span className="bg-gradient-to-r from-atoms-accent to-purple-400 bg-clip-text text-transparent">
            with AI Agents
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-6 max-w-2xl text-lg text-zinc-400"
        >
          Our team of specialized AI agents collaborates to design, architect,
          and build full-stack applications from your ideas. Just describe what
          you want, and watch it come to life.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-8 flex gap-4"
        >
          <Link href="/login?tab=register">
            <Button size="lg">
              Get Started
              <Rocket className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/login">
            <Button variant="outline" size="lg">
              Sign In
            </Button>
          </Link>
        </motion.div>
      </section>

      {/* Agents */}
      <section className="px-6 py-20">
        <div className="mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="mb-12 text-center"
          >
            <h2 className="text-3xl font-bold text-white mb-3">
              Meet Your AI Team
            </h2>
            <p className="text-zinc-400">
              Each agent specializes in a different aspect of software
              development
            </p>
          </motion.div>

          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
            {AGENTS.map((agent, i) => (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
                className="group rounded-xl border border-atoms-border bg-atoms-card p-5 text-center transition-colors hover:border-atoms-accent/40"
              >
                <div className="mb-3 text-4xl">{agent.avatarEmoji}</div>
                <h3 className="font-semibold text-white">{agent.name}</h3>
                <p className="text-xs text-atoms-accent-hover mt-0.5">
                  {agent.role}
                </p>
                <p className="mt-2 text-xs text-zinc-500">
                  {agent.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="px-6 py-20 border-t border-atoms-border/30">
        <div className="mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="mb-12 text-center"
          >
            <h2 className="text-3xl font-bold text-white mb-3">
              How It Works
            </h2>
            <p className="text-zinc-400">
              From idea to deployed application in three simple steps
            </p>
          </motion.div>

          <div className="grid gap-6 md:grid-cols-3">
            {FEATURES.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="rounded-xl border border-atoms-border bg-atoms-card p-6 transition-colors hover:border-atoms-accent/30"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-atoms-accent/10 text-atoms-accent">
                  <feature.icon className="h-6 w-6" />
                </div>
                <h3 className="text-lg font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-sm text-zinc-400 leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mx-auto max-w-2xl text-center"
        >
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Build Something Amazing?
          </h2>
          <p className="text-zinc-400 mb-8">
            Join thousands of developers who are already building with AI agents
          </p>
          <Link href="/login?tab=register">
            <Button size="lg">
              Start Building Now
              <Sparkles className="h-4 w-4" />
            </Button>
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="border-t border-atoms-border/30 px-6 py-8">
        <div className="mx-auto max-w-6xl flex items-center justify-between text-sm text-zinc-500">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-atoms-accent" />
            <span>Atoms Demo</span>
          </div>
          <span>Built with Next.js + FastAPI</span>
        </div>
      </footer>
    </div>
  );
}
