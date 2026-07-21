import json
import re
from typing import Any
from app.agents.base import BaseAgent
from app.utils.llm import llm_provider


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
            "You are a senior Software Engineer who writes clean, production-quality code. "
            "You implement complete, working web applications based on PRDs and architecture docs. "
            "Your code is well-structured, responsive, and visually polished. "
            "You always output COMPLETE, WORKING HTML+CSS+JS code that can be rendered in an iframe. "
            "Do NOT wrap code in markdown fences. Start HTML directly with <!DOCTYPE html>."
        )

    @property
    def avatar_emoji(self) -> str:
        return "💻"

    def _build_analyze_prompt(self, task: str, context: dict[str, Any]) -> str:
        is_iteration = context.get("is_iteration", False)
        history = context.get("conversation_history", [])
        prev_code = context.get("previous_code", "")

        prompt = f"User request: {task}\n\n"
        if is_iteration:
            prompt = "[ITERATION MODE] The user wants to modify an existing application.\n\n"
            if prev_code:
                prompt += f"Current application code (truncated):\n```\n{prev_code[:3000]}\n```\n\n"
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
                "1. What is the user really trying to build? Go beyond the literal request — what would make this genuinely useful and impressive?\n"
                "2. What features and interactions are essential for this to work well?\n"
                "3. What edge cases or usability issues need to be handled?\n"
                "4. What would make the result stand out versus a basic implementation?\n"
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
                "3. Interactions & logic — event handlers, game loops, algorithms\n"
                "4. Styling approach — colors, layout, animations, responsive breakpoints\n"
                "5. Key technical decisions — libraries, patterns, optimizations\n"
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
                f"Apply ALL the designed changes. Output the COMPLETE modified HTML file.\n\n"
            )
        else:
            prompt = (
                f"Implement a COMPLETE, WORKING web application.\n\n"
                f"User request: {task}\n\n"
                f"Analysis:\n{analysis}\n\n"
                f"Design:\n{design}\n\n"
            )

        prompt += (
            "CRITICAL REQUIREMENTS:\n"
            "1. Output a SINGLE, COMPLETE HTML file with embedded CSS and JS\n"
            "2. Start HTML with <!DOCTYPE html> directly — NO markdown code fences, NO explanation before the code\n"
            "3. ALL interactive elements MUST actually work — buttons click, games playable, forms submit\n"
            "4. For games: must have complete game loop (start → play → end), scoring, controls, and win/lose conditions\n"
            "5. For calculators: must handle all button inputs correctly, display updates in real-time\n"
            "6. Test your logic mentally before outputting — no broken event handlers, no undefined variables\n"
            "7. Use modern CSS (Grid, Flexbox, custom properties) with beautiful, polished UI\n"
            "8. Responsive design for all screen sizes\n"
            "9. Must render correctly in an iframe\n"
        )
        return prompt

    def _build_think_prompt(self, task: str, context: dict[str, Any]) -> str:
        return self._build_analyze_prompt(task, context)

    def _build_act_prompt(self, task: str, context: dict[str, Any]) -> str:
        prev_code = context.get("previous_code", "")
        is_iteration = context.get("is_iteration", False)
        history = context.get("conversation_history", [])

        if is_iteration and prev_code:
            prompt = (
                f"[ITERATION] Modify the existing application.\n\n"
                f"User request: {task}\n\n"
                f"Current code:\n{prev_code}\n\n"
            )
            if history:
                prompt += "Conversation:\n" + "\n".join(history[-6:]) + "\n\n"
            prompt += "First output your analysis of what needs to change and any bugs to fix. Then output the COMPLETE modified HTML file.\n\n"
        else:
            prompt = f"Build a COMPLETE, WORKING web application for:\n\n{task}\n\n"

        prompt += (
            "OUTPUT FORMAT — follow this exactly:\n"
            "1. **Analysis** — What is this? What features are essential? What makes it genuinely useful/impressive? What edge cases?\n"
            "2. **Design** — Layout structure, state/data model, key algorithms, interaction flow, styling approach\n"
            "3. **Implementation** — Output a SINGLE, COMPLETE HTML file starting with <!DOCTYPE html>\n\n"
            "CRITICAL:\n"
            "- Games MUST have: complete game loop (start→play→end), scoring, controls, win/lose, restart\n"
            "- Calculators MUST: handle all inputs, real-time display updates, edge cases\n"
            "- ALL interactive elements MUST work — no broken handlers, no undefined variables\n"
            "- Start HTML with <!DOCTYPE html> — NO markdown fences\n"
            "- Beautiful polished UI with modern CSS\n"
            "- Must render in an iframe\n"
        )
        return prompt

    async def think(self, task: str, context: dict[str, Any]) -> str:
        prompt = self._build_think_prompt(task, context)
        if llm_provider.is_mock:
            is_iteration = context.get("is_iteration", False)
            if is_iteration:
                return f"I'll modify the existing application based on the user's feedback. The change involves: {task[:100]}. I'll update the relevant sections while preserving the working parts."
            return f"I'll build this from scratch. The plan: create a modern, responsive single-page application with clean structure, polished styling, and working interactions."
        return await llm_provider.generate(self.get_system_prompt(), prompt)

    async def act(self, task: str, context: dict[str, Any]) -> str:
        prompt = self._build_act_prompt(task, context)
        if llm_provider.is_mock:
            return self._mock_iterate(task, context.get("previous_code", ""), context.get("is_iteration", False))
        result = await llm_provider.generate(self.get_system_prompt(), prompt, temperature=0.4)
        code = self._extract_html(result)
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
<section style="padding:80px 24px;text-align:center">
<div style="max-width:500px;margin:0 auto">
<h2 style="font-size:28px;font-weight:700;margin-bottom:8px">Get in Touch</h2>
<p style="color:#94a3b8;margin-bottom:32px">We'd love to hear from you</p>
<form onsubmit="event.preventDefault();this.innerHTML='<p style=\\'color:#22c55e;font-size:18px;padding:40px\\'>Message sent! We\\'ll get back to you soon.</p>'" style="display:flex;flex-direction:column;gap:16px">
<input placeholder="Your name" style="padding:12px 16px;border-radius:8px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.05);color:#e2e8f0;font-size:14px;outline:none">
<input placeholder="Email" type="email" style="padding:12px 16px;border-radius:8px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.05);color:#e2e8f0;font-size:14px;outline:none">
<textarea placeholder="Your message" rows="4" style="padding:12px 16px;border-radius:8px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.05);color:#e2e8f0;font-size:14px;outline:none;resize:vertical"></textarea>
<button type="submit" style="padding:12px 24px;border-radius:8px;border:none;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;font-weight:600;font-size:14px;cursor:pointer">Send Message</button>
</form>
</div>
</section>
"""
        if "</footer>" in code:
            return code.replace("</footer>", form_html + "</footer>")
        if "</body>" in code:
            return code.replace("</body>", form_html + "</body>")
        return code + form_html

    @staticmethod
    def _extract_html(text: str) -> str:
        fence_match = re.search(r"```html\s*\n(.*?)```", text, re.DOTALL)
        if fence_match:
            return fence_match.group(1).strip()
        fence_match = re.search(r"```\s*\n(.*?)```", text, re.DOTALL)
        if fence_match:
            content = fence_match.group(1).strip()
            if content.lower().startswith("<!doctype") or content.lower().startswith("<html"):
                return content
        if text.strip().lower().startswith("<!doctype") or text.strip().lower().startswith("<html"):
            return text.strip()
        html_start = text.find("<!DOCTYPE")
        if html_start == -1:
            html_start = text.find("<html")
        if html_start != -1:
            return text[html_start:].strip()
        return text.strip()
