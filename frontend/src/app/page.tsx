"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/Button";
import { AGENTS } from "@/lib/agents";
import { Cpu, Eye, Rocket, Sparkles, ArrowRight } from "lucide-react";

const FEATURES = [
  {
    icon: Cpu,
    title: "多Agent协作工作流",
    description: "8位专业AI Agent协同工作，从研究、规划、设计到实现，全流程自动化。",
  },
  {
    icon: Eye,
    title: "实时预览与迭代",
    description: "Agent生成代码的同时实时预览效果，支持即时修改和迭代优化。",
  },
  {
    icon: Rocket,
    title: "一键部署上线",
    description: "从想法到可销售产品只需几分钟，一键部署到线上，即刻开始获取用户。",
  },
];

export default function HomePage() {
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
          <Link href="/login">
            <Button variant="ghost" size="sm">登录</Button>
          </Link>
          <Link href="/login?tab=register">
            <Button size="sm">开始使用</Button>
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
            可销售的产品
          </span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-6 max-w-2xl text-lg text-zinc-400 leading-relaxed"
        >
          AI 员工用于验证想法、构建产品并获取客户。几分钟内完成。无需编码。
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-8 flex gap-4"
        >
          <Link href="/login?tab=register">
            <Button size="lg">
              免费开始
              <Rocket className="h-4 w-4" />
            </Button>
          </Link>
          <Link href="/login">
            <Button variant="outline" size="lg">登录</Button>
          </Link>
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
              你的 AI Team
            </h2>
            <p className="text-zinc-400">
              一个完整的 AI 团队，帮助你以更低成本更快发布
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
              调研、设计、编程、增长，尽在一处
            </h2>
            <p className="text-zinc-400">
              几分钟即可上线，不用等几周
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
            描述你的想法，AI 团队帮你从零到一
          </p>
          <Link href="/login?tab=register">
            <Button size="lg">
              立即开始
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </motion.div>
      </section>

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
