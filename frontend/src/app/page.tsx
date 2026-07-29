"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/Button";
import { AGENTS } from "@/lib/agents";
import { Cpu, Eye, Rocket, Sparkles, ArrowRight, Zap, Loader2 } from "lucide-react";

const FEATURES = [
  {
    icon: Cpu,
    title: "多 Agent 协作",
    description: "8个专业AI Agent自动协作——从调研、规划到设计和实现，全流程自动化。",
  },
  {
    icon: Eye,
    title: "实时预览 & 迭代",
    description: "Agent生成代码的同时实时预览。随时修改任何细节，快速迭代。",
  },
  {
    icon: Rocket,
    title: "分钟级交付",
    description: "从想法到可交付产品只需几分钟。一键部署，立即上线。",
  },
];

export default function HomePage() {
  const [guestLoading, setGuestLoading] = useState(false);

  const handleGuestLogin = async () => {
    if (guestLoading) return;
    setGuestLoading(true);
    try {
      const { guestLogin } = await import("@/lib/store").then(m => m.useAuthStore.getState());
      await guestLogin();
      window.location.href = "/dashboard";
    } catch {
      setGuestLoading(false);
    }
  };

  return (
    <div className="min-h-full bg-atoms-dark overflow-hidden">
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-b from-atoms-accent/8 via-transparent to-transparent" />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] bg-atoms-accent/5 rounded-full blur-3xl" />
      </div>

      <nav className="flex items-center justify-between px-6 py-4 border-b border-atoms-border/50">
        <div className="flex items-center gap-2">
          <Sparkles className="h-6 w-6 text-atoms-accent" />
          <span className="text-lg font-bold text-white">Atoms Demo</span>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleGuestLogin}
            disabled={guestLoading}
            className="flex items-center gap-1.5 rounded-lg border border-atoms-border bg-atoms-card px-3 py-1.5 text-sm text-zinc-300 hover:bg-white/5 transition-colors disabled:opacity-50"
          >
            {guestLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Zap className="h-3.5 w-3.5 text-amber-400" />}
            {guestLoading ? "登录中..." : "游客体验"}
          </button>
          <Link href="/login">
            <Button variant="ghost" size="sm">登录</Button>
          </Link>
          <Link href="/login?tab=register">
            <Button size="sm">注册</Button>
          </Link>
        </div>
      </nav>

      <section className="relative flex flex-col items-center justify-center px-6 pt-24 pb-20 text-center">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-atoms-border bg-atoms-card/60 px-4 py-1.5 text-sm text-zinc-400 backdrop-blur">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            AI Agent 驱动的代码生成平台
          </div>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="max-w-4xl text-5xl font-bold leading-tight tracking-tight text-white sm:text-6xl lg:text-7xl"
        >
          把想法变成
          <br />
          <span className="bg-gradient-to-r from-atoms-accent to-purple-400 bg-clip-text text-transparent">
            可交付的产品
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-6 max-w-2xl text-lg text-zinc-400 leading-relaxed"
        >
          AI团队帮你验证想法、构建产品、获取用户。几分钟搞定，无需编码。
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-8 flex flex-col items-center gap-3"
        >
          <div className="flex gap-4">
            <button
              onClick={handleGuestLogin}
              disabled={guestLoading}
              className="flex items-center gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 px-6 py-3 text-sm font-semibold text-amber-300 hover:bg-amber-500/20 transition-all disabled:opacity-50"
            >
              {guestLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
              {guestLoading ? "登录中..." : "游客体验 — 免注册"}
            </button>
            <Link href="/login?tab=register">
              <Button size="lg">
                免费开始
                <Rocket className="h-4 w-4" />
              </Button>
            </Link>
          </div>
          <p className="text-xs text-zinc-600">演示账号: demo@atoms-demo.app / demo2024</p>
        </motion.div>
      </section>

      <section className="px-6 py-20">
        <div className="mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="mb-12 text-center"
          >
            <h2 className="text-3xl font-bold text-white mb-3">
              你的 AI 团队
            </h2>
            <p className="text-zinc-400">
              8个专业AI Agent帮你更快、更低成本地交付产品
            </p>
          </motion.div>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-4">
            {AGENTS.map((agent, i) => (
              <motion.div
                key={agent.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.06 }}
                className="agent-card-atoms group rounded-xl border border-atoms-border bg-atoms-card p-5 text-center"
                style={{ "--hover-color": `${agent.color}40` } as React.CSSProperties}
              >
                <div className="flex justify-center mb-3">
                  <Image
                    src={agent.avatarUrl}
                    alt={agent.name}
                    width={64}
                    height={64}
                    className="agent-avatar-img"
                    style={{ borderColor: `${agent.color}30`, borderWidth: 2 }}
                    unoptimized
                  />
                </div>
                <h3 className="font-semibold text-white text-sm">{agent.name}</h3>
                <span
                  className="inline-block text-[10px] px-2 py-0.5 rounded-full mt-0.5 mb-2 font-medium"
                  style={{ backgroundColor: `${agent.color}15`, color: agent.color }}
                >
                  {agent.role}
                </span>
                <p className="text-xs text-zinc-500 leading-relaxed">{agent.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section className="px-6 py-20 border-t border-atoms-border/30">
        <div className="mx-auto max-w-6xl">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="mb-12 text-center"
          >
            <h2 className="text-3xl font-bold text-white mb-3">
              调研、设计、构建、增长 — 一站搞定
            </h2>
            <p className="text-zinc-400">
              几分钟交付，而不是几周
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
                className="glass-card p-6 hover:border-white/10 transition-colors"
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

      <section className="px-6 py-20">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mx-auto max-w-2xl text-center"
        >
          <h2 className="text-3xl font-bold text-white mb-4">
            准备好构建你的产品了吗？
          </h2>
          <p className="text-zinc-400 mb-8">
            描述你的想法，AI团队从零到一帮你构建
          </p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={handleGuestLogin}
              disabled={guestLoading}
              className="flex items-center gap-2 rounded-xl border border-amber-500/30 bg-amber-500/10 px-6 py-3 text-sm font-semibold text-amber-300 hover:bg-amber-500/20 transition-all disabled:opacity-50"
            >
              {guestLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Zap className="h-4 w-4" />}
              游客体验
            </button>
            <Link href="/login?tab=register">
              <Button size="lg">
                免费开始
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        </motion.div>
      </section>

      <footer className="border-t border-atoms-border/30 px-6 py-8">
        <div className="mx-auto max-w-6xl flex items-center justify-between text-sm text-zinc-500">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-atoms-accent" />
            <span>Atoms Demo</span>
          </div>
          <span>基于 Next.js + FastAPI 构建</span>
        </div>
      </footer>
    </div>
  );
}
