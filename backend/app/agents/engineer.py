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
            "You always output COMPLETE, WORKING HTML+CSS+JS code that can be rendered in an iframe."
        )

    @property
    def avatar_emoji(self) -> str:
        return "💻"

    async def think(self, task: str, context: dict[str, Any]) -> str:
        prd = context.get("prd", "")
        arch = context.get("architecture", "")
        prev_code = context.get("previous_code", "")
        is_iteration = context.get("is_iteration", False)
        history = context.get("conversation_history", [])

        prompt = f"Request: {task}\n\n"
        if is_iteration:
            prompt = f"[ITERATION] The user wants to modify an existing application.\n\n{prompt}"
            if history:
                prompt += "Previous conversation:\n" + "\n".join(history[-6:]) + "\n\n"
        if prd:
            prompt += f"PRD: {prd[:500]}\n\n"
        if arch:
            prompt += f"Architecture: {arch[:500]}\n\n"
        prompt += "Describe your implementation plan briefly (2-3 sentences)."

        if llm_provider.is_mock:
            if is_iteration:
                return f"I'll modify the existing application based on the user's feedback. The change involves: {task[:100]}. I'll update the relevant sections while preserving the working parts."
            return f"I'll build this from scratch. The plan: create a modern, responsive single-page application with clean structure, polished styling, and working interactions."

        return await llm_provider.generate(self.get_system_prompt(), prompt)

    async def act(self, task: str, context: dict[str, Any]) -> str:
        prd = context.get("prd", "")
        arch = context.get("architecture", "")
        prev_code = context.get("previous_code", "")
        is_iteration = context.get("is_iteration", False)
        history = context.get("conversation_history", [])

        if is_iteration and prev_code:
            prompt = (
                f"[ITERATION] The user wants to modify the existing application.\n\n"
                f"User request: {task}\n\n"
                f"Here is the CURRENT code that needs to be modified:\n\n"
                f"{prev_code}\n\n"
                f"Apply the user's requested changes to this code. "
                f"Output the COMPLETE modified HTML file (not just the changed parts). "
                f"Keep all existing functionality while adding the requested changes.\n\n"
            )
            if history:
                prompt += "Conversation context:\n" + "\n".join(history[-6:]) + "\n\n"
        else:
            prompt = f"Implement a COMPLETE, WORKING web application for:\n\nRequest: {task}\n\n"
            if prd:
                prompt += f"PRD: {prd[:800]}\n\n"
            if arch:
                prompt += f"Architecture: {arch[:800]}\n\n"

        prompt += (
            "CRITICAL REQUIREMENTS:\n"
            "1. Output a SINGLE, COMPLETE HTML file with embedded CSS and JS\n"
            "2. Must be fully functional and render correctly in an iframe\n"
            "3. Use modern CSS (Grid, Flexbox, custom properties, animations)\n"
            "4. Responsive design for all screen sizes\n"
            "5. Beautiful, polished UI with gradients, shadows, and micro-interactions\n"
            "6. All interactive elements must work (buttons, forms, etc.)\n"
            "7. Use system font stack\n"
            "8. Output ONLY the HTML code, no markdown code fences, no explanation\n"
        )

        if llm_provider.is_mock:
            return self._mock_iterate(task, prev_code, is_iteration)

        result = await llm_provider.generate(self.get_system_prompt(), prompt, temperature=0.4)
        code = self._extract_html(result)
        return code

    def _mock_iterate(self, task: str, prev_code: str, is_iteration: bool) -> str:
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

        from app.utils.llm import _generate_landing_html
        task_lower = task.lower()
        if any(w in task_lower for w in ["dashboard", "admin", "analytics", "chart"]):
            return LLMProvider._dashboard_html()  # type: ignore
        if any(w in task_lower for w in ["portfolio", "personal", "resume", "about"]):
            return LLMProvider._portfolio_html()  # type: ignore
        if any(w in task_lower for w in ["calculator", "tool", "converter"]):
            return LLMProvider._calculator_html()  # type: ignore
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

    def _extract_html(self, text: str) -> str:
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
