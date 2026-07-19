import type { AgentInfo } from "./types";

export const AGENTS: AgentInfo[] = [
  {
    name: "Mike",
    role: "Team Leader",
    description: "Coordinates tasks and manages the team",
    avatarEmoji: "\u{1F468}\u{200D}\u{1F4BC}",
  },
  {
    name: "Emma",
    role: "Product Manager",
    description: "Analyzes requirements and creates PRDs",
    avatarEmoji: "\u{1F4CB}",
  },
  {
    name: "Bob",
    role: "Architect",
    description: "Designs system architecture",
    avatarEmoji: "\u{1F3D7}\u{FE0F}",
  },
  {
    name: "Alex",
    role: "Engineer",
    description: "Builds full-stack applications",
    avatarEmoji: "\u{1F4BB}",
  },
  {
    name: "Iris",
    role: "Deep Researcher",
    description: "Conducts deep research",
    avatarEmoji: "\u{1F50D}",
  },
];

export function getAgentByName(name: string): AgentInfo | undefined {
  return AGENTS.find((a) => a.name === name);
}
