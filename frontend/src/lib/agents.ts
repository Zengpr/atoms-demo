import type { AgentInfo } from "./types";

const CDN = "https://public-frontend-cos.metadl.com/nuxt-mgx/prod/assets";

export const AGENTS: AgentInfo[] = [
  {
    name: "Mike",
    role: "Team Leader",
    description: "Runs the plan end to end, coordinates agents, and requests your approval so you move fast while staying in the loop.",
    avatarEmoji: "\u{1F468}\u{200D}\u{1F4BC}",
    avatarUrl: `${CDN}/Mike-TeamLeader-Avatar.Cz3pEmZL.webp`,
    color: "#6366F1",
  },
  {
    name: "Emma",
    role: "Product Manager",
    description: "Turns your idea into a clear spec and scope, so the build stays simple and usable.",
    avatarEmoji: "\u{1F469}\u{200D}\u{1F4BB}",
    avatarUrl: `${CDN}/Emma-ProductManager-Avatar.SF7T1yd6.webp`,
    color: "#EC4899",
  },
  {
    name: "Bob",
    role: "Architect",
    description: "Designs the system blueprint, choosing the right structure so your app is scalable and reliable.",
    avatarEmoji: "\u{1F3D7}\u{FE0F}",
    avatarUrl: `${CDN}/Bob-Architect-Avatar.BuXFqV4r.webp`,
    color: "#F59E0B",
  },
  {
    name: "Alex",
    role: "Engineer",
    description: "Builds a production-ready full-stack app by wiring the frontend, backend, integrations, and deployment.",
    avatarEmoji: "\u{1F4BB}",
    avatarUrl: `${CDN}/Alex-Engineer-Avatar.CEF2q3cr.png`,
    color: "#10B981",
  },
  {
    name: "Iris",
    role: "Deep Researcher",
    description: "Finds real demand and niches through Deep Research, then turns signals into focused opportunities.",
    avatarEmoji: "\u{1F50D}",
    avatarUrl: `${CDN}/Iris-DeepResearcher-Avatar.Ct5iZcVH.webp`,
    color: "#8B5CF6",
  },
  {
    name: "Sarah",
    role: "SEO Specialist",
    description: "Launches SEO pages fast and automates optimizations to drive organic traffic quickly at lower cost.",
    avatarEmoji: "\u{1F680}",
    avatarUrl: `${CDN}/Sarah-SEOSpecialist-Avatar.C57ySW-t.webp`,
    color: "#06B6D4",
  },
  {
    name: "Adrian",
    role: "Ads Specialist",
    description: "Runs Google Ads automatically. Manages campaign creation, tracking, and optimization so you scale growth with less effort.",
    avatarEmoji: "\u{1F4E2}",
    avatarUrl: `${CDN}/Adrian-AdsAgent-Avatar.D1HVIhCr.png`,
    color: "#EF4444",
  },
  {
    name: "David",
    role: "Data Analyst",
    description: "Analyzes massive data to spot growth opportunities and surface clear insights for smarter decisions.",
    avatarEmoji: "\u{1F4CA}",
    avatarUrl: `${CDN}/David-DataAnalyst-Avatar.k44i8aOu.webp`,
    color: "#F97316",
  },
];

export const WORKFLOW_STEPS = [
  { key: "research", label: "Research", agent: "Iris", icon: "\u{1F50D}" },
  { key: "plan", label: "Plan", agent: "Mike", icon: "\u{1F4CB}" },
  { key: "prd", label: "PRD", agent: "Emma", icon: "\u{1F4DD}" },
  { key: "architecture", label: "Architecture", agent: "Bob", icon: "\u{1F3D7}\u{FE0F}" },
  { key: "code", label: "Build", agent: "Alex", icon: "\u{1F4BB}" },
  { key: "review", label: "Review", agent: "Mike", icon: "\u{2705}" },
];

export function getAgentByName(name: string): AgentInfo | undefined {
  return AGENTS.find((a) => a.name === name);
}

export function getAgentColor(name: string): string {
  return AGENTS.find((a) => a.name === name)?.color ?? "#6366F1";
}
