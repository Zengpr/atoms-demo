"use client";

import { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, Mail, Lock, User, Zap } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { useAuthStore } from "@/lib/store";

type Tab = "login" | "register";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, register } = useAuthStore();
  const initialTab = searchParams.get("tab") === "register" ? "register" : "login";
  const [tab, setTab] = useState<Tab>(initialTab);
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [guestLoading, setGuestLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGuestLogin = async () => {
    setGuestLoading(true);
    setError("");
    try {
      await useAuthStore.getState().guestLogin();
      router.push("/dashboard");
    } catch {
      setError("创建游客账号失败，请尝试手动注册。");
    } finally {
      setGuestLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (tab === "login") {
        await login(email, password);
      } else {
        await register(email, username, password);
      }
      router.push("/dashboard");
    } catch (err: unknown) {
      let message = "出错了，请重试。";
      if (err instanceof Error) {
        message = err.message;
      }
      if (message.includes("400") || message.includes("already")) {
        message = tab === "register"
          ? "邮箱或用户名已被使用，请换一个。"
          : "邮箱或密码不正确。";
      }
      if (message.includes("500") || message.includes("Server error") || message.includes("Failed to fetch")) {
        message = "无法连接服务器，请检查网络。";
      }
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-full items-center justify-center px-4 py-12">
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-atoms-accent/10 via-atoms-dark to-purple-900/10" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="w-full max-w-md"
      >
        <div className="mb-8 flex flex-col items-center">
          <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-atoms-accent/10 text-atoms-accent">
            <Sparkles className="h-7 w-7" />
          </div>
          <h1 className="text-2xl font-bold text-white">Atoms Demo</h1>
          <p className="mt-1 text-sm text-zinc-400">
            AI Agent 驱动的代码生成平台
          </p>
        </div>

        <div className="rounded-xl border border-atoms-border bg-atoms-card p-6 shadow-2xl shadow-atoms-accent/5">
          <div className="mb-6 flex rounded-lg bg-atoms-dark p-1">
            {(["login", "register"] as const).map((t) => (
              <button
                key={t}
                onClick={() => {
                  setTab(t);
                  setError("");
                }}
                className={`flex-1 rounded-md py-2 text-sm font-medium transition-all ${
                  tab === t
                    ? "bg-atoms-accent text-white shadow-lg"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {t === "login" ? "登录" : "注册"}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
              <Input
                type="email"
                placeholder="邮箱"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="pl-10"
                required
              />
            </div>

            <AnimatePresence>
              {tab === "register" && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
                    <Input
                      type="text"
                      placeholder="用户名"
                      value={username}
                      onChange={(e) => setUsername(e.target.value)}
                      className="pl-10"
                      required
                    />
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-zinc-500" />
              <Input
                type="password"
                placeholder="密码"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="pl-10"
                required
                minLength={6}
              />
            </div>

            {error && (
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="rounded-lg bg-red-500/10 px-3 py-2 text-sm text-red-400"
              >
                {error}
              </motion.p>
            )}

            <Button type="submit" loading={loading} className="w-full">
              {tab === "login" ? "登录" : "注册"}
            </Button>
          </form>

          <div className="relative my-5">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-atoms-border" /></div>
            <div className="relative flex justify-center text-xs"><span className="bg-atoms-card px-2 text-zinc-500">或</span></div>
          </div>

          <Button
            onClick={handleGuestLogin}
            loading={guestLoading}
            variant="outline"
            className="w-full flex items-center justify-center gap-2"
          >
            <Zap className="h-4 w-4" />
            游客体验 — 免注册
          </Button>

          <div className="mt-4 rounded-lg bg-white/3 border border-white/6 px-3 py-2.5 text-center">
            <p className="text-[11px] text-zinc-500 mb-1">演示测试账号（评审专用）</p>
            <p className="text-xs text-zinc-300 font-mono">demo@atoms-demo.app / demo2024</p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="flex min-h-full items-center justify-center"><Sparkles className="h-5 w-5 text-atoms-accent animate-spin" /></div>}>
      <LoginForm />
    </Suspense>
  );
}
