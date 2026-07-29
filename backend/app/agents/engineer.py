import json
import re
from typing import Any
from app.agents.base import BaseAgent
from app.utils.llm import llm_provider


TAILWIND_CDN = '<script src="https://cdn.tailwindcss.com"></script>'
GOOGLE_FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">'

DESIGN_SYSTEM = """DESIGN SYSTEM (MANDATORY — you MUST follow these rules):

Tech Stack:
- HTML5 + Tailwind CSS (via CDN) + Vanilla JavaScript
- Inter font via Google Fonts
- Icons: use inline SVG or emoji (no external icon library needed)

CRITICAL: Include these EXACT lines in your <head>:
<script src="https://cdn.tailwindcss.com"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<script>tailwind.config={theme:{extend:{fontFamily:{sans:['Inter','system-ui','sans-serif']}}}}</script>

Visual Rules:
- Use Tailwind utility classes ONLY — NEVER use inline styles or <style> tags (except for animations/keyframes)
- Background: bg-zinc-950 or bg-gray-950 (dark theme) OR bg-white with gray-50 sections (light theme)
- Cards: bg-white/5 backdrop-blur border border-white/10 rounded-xl shadow-lg (dark) OR bg-white shadow-md rounded-xl (light)
- Text: text-white / text-zinc-100 for primary, text-zinc-400 for secondary (dark)
- Accent colors: indigo-500, violet-500, emerald-500, amber-500 as needed
- Buttons: px-6 py-3 rounded-xl font-semibold transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]
- Spacing: consistent p-6, gap-4, mb-8 patterns; generous whitespace
- Hover: always add hover effects on interactive elements (color change, scale, shadow)
- Responsive: use max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 for containers
- NEVER use placeholder text — write realistic, specific content matching the app's purpose
- NEVER use default browser blue (#0000FF) or bare <a> link colors

Layout Rules:
- Use flex and grid layouts — NEVER use position:absolute for layout (only for overlays/modals)
- Hero sections: full-width, centered content, large heading
- Feature grids: grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6
- Navigation: sticky top-0 with backdrop-blur
- Footer: border-t with py-8
"""


class EngineerAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "Alex"

    @property
    def role(self) -> str:
        return "Senior Software Engineer"

    @property
    def description(self) -> str:
        return (
            "You are a senior software engineer who writes high-quality, production-grade code. "
            "You implement complete, runnable web applications based on PRDs and architecture documents. "
            "Your code is well-structured, responsive, and visually polished. "
            "You always output a complete, runnable HTML file with Tailwind CSS. "
            "Do not wrap code in Markdown code blocks."
        )

    @property
    def avatar_emoji(self) -> str:
        return "💻"

    def get_act_system_prompt(self) -> str:
        return (
            f"You are {self.name}, {self.role}. "
            "You write COMPLETE, WORKING HTML+Tailwind CSS+JS code that runs in an iframe. "
            "Always output a single HTML file starting with <!DOCTYPE html>. "
            "NEVER refuse to write code. NEVER say you cannot provide code. "
            "NEVER wrap code in markdown fences. Start HTML directly. "
            "You MUST use Tailwind CSS via CDN — never write raw CSS in <style> tags. "
            "When given a task, IMMEDIATELY write the full implementation code. "
            "Do NOT explain or analyze — just output the code starting with <!DOCTYPE html>."
        )

    def _build_act_prompt(self, task: str, context: dict[str, Any]) -> str:
        prev_code = context.get("previous_code", "")
        is_iteration = context.get("is_iteration", False)
        prd = context.get("prd", "")
        architecture = context.get("architecture", "")
        console_errors = context.get("console_errors", [])

        if is_iteration and prev_code:
            prompt = (
                f"[ITERATION] Modify the existing application based on the user's request.\n\n"
                f"User request: {task}\n\n"
                f"Current code:\n{prev_code}\n\n"
            )
            if console_errors:
                prompt += (
                    "BROWSER CONSOLE ERRORS (REAL errors — YOU MUST FIX THEM):\n"
                    + "\n".join(f"- {e}" for e in console_errors)
                    + "\n\n"
                    "DEBUGGING CHECKLIST:\n"
                    "1. Check for mismatched/missing braces {}, brackets [], parentheses ()\n"
                    "2. Check for missing commas in arrays and objects\n"
                    "3. Check for unclosed strings or template literals\n"
                    "4. Check for syntax errors near the reported line\n"
                    "5. Verify all functions are properly closed\n"
                    "6. Verify all HTML tags are properly closed\n\n"
                )
            prompt += (
                "Make the requested changes to the existing code. "
                "Preserve everything that still works. Only modify what needs to change. "
                "Output the COMPLETE modified HTML file.\n\n"
                f"{DESIGN_SYSTEM}\n\n"
                "START your output with <!DOCTYPE html> — NO explanation, NO markdown fences, NO analysis."
            )
        else:
            prompt = f"Build a COMPLETE, WORKING web application for:\n\n{task}\n\n"
            if prd:
                prompt += f"Product Requirements (from PM):\n{prd[:3000]}\n\n"
            if architecture:
                prompt += f"Architecture (from Architect):\n{architecture[:3000]}\n\n"
            prompt += (
                f"{DESIGN_SYSTEM}\n\n"
                "CRITICAL RULES:\n"
                "- You MUST build EXACTLY what the user requested — same app type, same name, same features\n"
                "- ALL interactive elements MUST work — buttons click, forms submit, calculations run\n"
                "- Test every function call mentally — no undefined variables, no broken handlers\n"
                "- Responsive design for all screen sizes using Tailwind responsive classes\n"
                "- Must render correctly in an iframe\n"
                "- For games: complete game loop (start→play→end), scoring, controls, win/lose, restart\n"
                "- For games: start/game-over screens as HTML overlays with z-index above canvas\n"
                "- For games: use document.addEventListener for key events (iframe compat)\n"
                "- For games: add tabindex='0' to game container and .focus() on start\n"
                "- For calculators: handle all inputs, real-time display, edge cases\n\n"
                "START your output with <!DOCTYPE html> — NO explanation, NO markdown fences, NO analysis."
            )

        return prompt

    def _build_think_prompt(self, task: str, context: dict[str, Any]) -> str:
        is_iteration = context.get("is_iteration", False)
        prev_code = context.get("previous_code", "")
        history = context.get("conversation_history", [])

        if is_iteration:
            prompt = f"[ITERATION] User request: {task}\n\n"
            if prev_code:
                prompt += f"Current code:\n{prev_code}\n\n"
            if history:
                prompt += "Recent conversation:\n" + "\n".join(history[-6:]) + "\n\n"
            prompt += "Briefly describe what needs to change (2-3 sentences). Do NOT write code."
        else:
            prompt = f"User request: {task}\n\nBriefly describe your implementation plan (2-3 sentences). Do NOT write code."
        return prompt

    def _build_analyze_prompt(self, task: str, context: dict[str, Any]) -> str:
        is_iteration = context.get("is_iteration", False)
        history = context.get("conversation_history", [])
        prev_code = context.get("previous_code", "")

        prompt = f"User request: {task}\n\n"
        if is_iteration:
            prompt = "[ITERATION MODE] The user wants to modify an existing application.\n\n"
            if prev_code:
                prompt += f"Current application code:\n```\n{prev_code}\n```\n\n"
            if history:
                prompt += "Recent conversation:\n" + "\n".join(history[-6:]) + "\n\n"
            prompt += (
                "Analyze what specific changes are needed. Identify:\n"
                "1. What parts of the current code need to change\n"
                "2. What new features/functionality to add\n"
                "3. Any bugs or issues in the current code that should be fixed\n"
                "Be thorough and specific. Do NOT write code yet."
            )
        else:
            prompt += (
                "Analyze this request thoroughly. Think about:\n"
                "1. What is the user really trying to build?\n"
                "2. What features and interactions are essential?\n"
                "3. What would make the result stand out versus a basic implementation?\n"
                "Be specific and detailed. Do NOT write code yet."
            )
        return prompt

    def _build_design_prompt(self, task: str, context: dict[str, Any], analysis: str) -> str:
        is_iteration = context.get("is_iteration", False)
        prompt = f"User request: {task}\n\nAnalysis:\n{analysis}\n\n"
        if is_iteration:
            prompt += (
                "Based on this analysis, design the implementation approach:\n"
                "1. Component structure — what HTML sections and JS modules\n"
                "2. State management — what data needs to be tracked\n"
                "3. Event handling — what user interactions to wire up\n"
                "4. Specific code changes — describe exactly what to modify\n"
                "Be concrete. Do NOT write code yet."
            )
        else:
            prompt += (
                "Based on this analysis, design the implementation:\n"
                "1. Component/layout structure — HTML sections and hierarchy\n"
                "2. State & data — what variables and data structures are needed\n"
                "3. Interactions & logic — event handlers, algorithms\n"
                "4. Styling approach — Tailwind classes, colors, responsive breakpoints\n"
                "Be concrete and specific. Do NOT write code yet."
            )
        return prompt

    def _build_implement_prompt(self, task: str, context: dict[str, Any], analysis: str, design: str) -> str:
        prev_code = context.get("previous_code", "")
        is_iteration = context.get("is_iteration", False)

        if is_iteration and prev_code:
            prompt = (
                f"[ITERATION] Modify the existing application.\n\n"
                f"User request: {task}\n\n"
                f"Analysis:\n{analysis}\n\n"
                f"Design:\n{design}\n\n"
                f"Current code:\n{prev_code}\n\n"
            )
        else:
            prompt = (
                f"Implement a COMPLETE, WORKING web application.\n\n"
                f"User request: {task}\n\n"
                f"Analysis:\n{analysis}\n\n"
                f"Design:\n{design}\n\n"
            )

        prompt += (
            f"{DESIGN_SYSTEM}\n\n"
            "Output a SINGLE, COMPLETE HTML file with embedded Tailwind classes and JS.\n"
            "Start with <!DOCTYPE html> directly — NO markdown fences, NO explanation.\n"
        )
        return prompt

    async def think(self, task: str, context: dict[str, Any]) -> str:
        prompt = self._build_think_prompt(task, context)
        if llm_provider.is_mock:
            is_iteration = context.get("is_iteration", False)
            if is_iteration:
                return f"I'll modify the existing application based on the user's feedback. The change involves: {task[:100]}."
            return f"I'll build this from scratch using Tailwind CSS with a polished, professional design."
        return await llm_provider.generate(self.get_system_prompt(), prompt)

    async def act(self, task: str, context: dict[str, Any]) -> str:
        prompt = self._build_act_prompt(task, context)
        if llm_provider.is_mock:
            return self._mock_iterate(task, context.get("previous_code", ""), context.get("is_iteration", False))
        result = await llm_provider.generate(self.get_act_system_prompt(), prompt, temperature=0.4)
        code = extract_html(result)
        return code

    def _mock_iterate(self, task: str, prev_code: str, is_iteration: bool) -> str:
        from app.utils.llm import LLMProvider, _generate_landing_html
        if is_iteration and prev_code:
            task_lower = task.lower()
            if any(w in task_lower for w in ["dark", "dark mode", "toggle"]):
                return self._add_dark_toggle(prev_code)
            if any(w in task_lower for w in ["color", "colour", "warm", "cool", "scheme", "theme"]):
                return self._change_colors(prev_code, task_lower)
            if any(w in task_lower for w in ["animation", "animate", "transition", "motion"]):
                return self._add_animations(prev_code)
            if any(w in task_lower for w in ["contact", "form", "input"]):
                return self._add_contact_form(prev_code)
            return prev_code

        task_lower = task.lower()
        if any(w in task_lower for w in ["dashboard", "admin", "analytics", "chart"]):
            return LLMProvider._dashboard_html()
        if any(w in task_lower for w in ["portfolio", "personal", "resume", "about"]):
            return LLMProvider._portfolio_html()
        if any(w in task_lower for w in ["calculator", "tool", "converter"]):
            return LLMProvider._calculator_html()
        if any(w in task_lower for w in ["snake", "\u8d2a\u5403\u86c7"]):
            return LLMProvider._snake_html()
        if any(w in task_lower for w in ["2048", "1024"]):
            return LLMProvider._game_2048_html()
        if any(w in task_lower for w in ["game", "tetris", "puzzle", "play", "\u6e38\u620f"]):
            return LLMProvider._game_2048_html()
        if any(w in task_lower for w in ["todo", "task", "list", "checklist"]):
            return LLMProvider._todo_html()
        if any(w in task_lower for w in ["counter", "count", "increment"]):
            return LLMProvider._counter_html()
        if any(w in task_lower for w in ["ecommerce", "shop", "store", "product", "cart"]):
            return LLMProvider._ecommerce_html()
        return _generate_landing_html()

    def _add_dark_toggle(self, code: str) -> str:
        insert = """
<div style="position:fixed;top:12px;right:12px;z-index:9999">
<button onclick="document.body.classList.toggle('dark-mode')" style="padding:6px 12px;border-radius:8px;border:1px solid rgba(255,255,255,.2);background:rgba(255,255,255,.1);color:#fff;cursor:pointer;font-size:12px">Toggle Dark</button>
</div>
<style>.dark-mode{filter:invert(1) hue-rotate(180deg)}.dark-mode img,.dark-mode video{filter:invert(1) hue-rotate(180deg)}</style>
"""
        if "</body>" in code:
            return code.replace("</body>", insert + "</body>")
        return code + insert

    def _change_colors(self, code: str, task: str) -> str:
        if "warm" in task:
            code = code.replace("#6366f1", "#f59e0b").replace("#8b5cf6", "#ef4444").replace("#06b6d4", "#f97316")
        elif "cool" in task:
            code = code.replace("#6366f1", "#0ea5e9").replace("#8b5cf6", "#6366f1").replace("#06b6d4", "#22d3ee")
        else:
            code = code.replace("#6366f1", "#10b981").replace("#8b5cf6", "#059669").replace("#06b6d4", "#34d399")
        return code

    def _add_animations(self, code: str) -> str:
        anim_style = """
<style>
*{scroll-behavior:smooth}
.fade-in{opacity:0;transform:translateY(20px);animation:fadeInUp .6s forwards}
@keyframes fadeInUp{to{opacity:1;transform:translateY(0)}}
.scale-in{animation:scaleIn .5s forwards}
@keyframes scaleIn{from{transform:scale(.8);opacity:0}to{transform:scale(1);opacity:1}}
.hover-lift{transition:transform .3s,box-shadow .3s}
.hover-lift:hover{transform:translateY(-4px);box-shadow:0 12px 40px rgba(0,0,0,.3)}
</style>
"""
        if "</head>" in code:
            code = code.replace("</head>", anim_style + "</head>")
        if 'class="feature-card' in code:
            code = code.replace('class="feature-card', 'class="feature-card fade-in hover-lift')
        return code

    def _add_contact_form(self, code: str) -> str:
        form_html = """
<section class="py-20 px-6 text-center">
<div class="max-w-lg mx-auto">
<h2 class="text-3xl font-bold mb-2">Get in Touch</h2>
<p class="text-zinc-400 mb-8">We'd love to hear from you</p>
<form onsubmit="event.preventDefault();this.innerHTML='<p class=\\'text-emerald-400 text-lg py-10\\'>Message sent! We\\'ll get back to you soon.</p>'" class="flex flex-col gap-4">
<input placeholder="Your name" class="p-3 rounded-xl border border-white/10 bg-white/5 text-zinc-100 text-sm outline-none focus:border-indigo-500 transition">
<input placeholder="Email" type="email" class="p-3 rounded-xl border border-white/10 bg-white/5 text-zinc-100 text-sm outline-none focus:border-indigo-500 transition">
<textarea placeholder="Your message" rows="4" class="p-3 rounded-xl border border-white/10 bg-white/5 text-zinc-100 text-sm outline-none resize-vertical focus:border-indigo-500 transition"></textarea>
<button type="submit" class="py-3 px-6 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-500 text-white font-semibold hover:scale-[1.02] active:scale-[0.98] transition-all duration-200">Send Message</button>
</form>
</div>
</section>
"""
        if "</footer>" in code:
            return code.replace("</footer>", form_html + "</footer>")
        if "</body>" in code:
            return code.replace("</body>", form_html + "</body>")
        return code + form_html

from app.utils.html_utils import extract_html
