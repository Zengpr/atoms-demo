import json
import re
from typing import AsyncIterator, Optional
from openai import AsyncOpenAI
from app.config import settings


def _build_mock_responses() -> dict[str, str]:
    return {
        "leader": json.dumps({
            "plan": "I'll coordinate the team to build this application. Here's our approach:",
            "steps": [
                {"agent": "pm", "task": "Analyze requirements and create PRD"},
                {"agent": "architect", "task": "Design system architecture"},
                {"agent": "engineer", "task": "Implement the application code"}
            ],
            "summary": "Team of 3 agents will collaborate to deliver this project."
        }),
        "pm": json.dumps({
            "prd": {
                "title": "Product Requirements Document",
                "overview": "A modern web application based on user requirements",
                "features": [
                    {"name": "Responsive Layout", "description": "Mobile-first responsive design", "priority": "P0"},
                    {"name": "Interactive UI", "description": "Smooth animations and transitions", "priority": "P0"},
                    {"name": "Data Display", "description": "Clear data visualization and presentation", "priority": "P1"},
                    {"name": "Navigation", "description": "Intuitive navigation structure", "priority": "P0"}
                ],
                "user_stories": [
                    "As a user, I want a clean, modern interface so I can easily navigate",
                    "As a user, I want responsive design so it works on any device",
                    "As a user, I want smooth interactions so the experience feels polished"
                ],
                "acceptance_criteria": [
                    "Application renders correctly in modern browsers",
                    "All interactive elements are functional",
                    "Design follows modern UI/UX best practices"
                ]
            }
        }),
        "architect": json.dumps({
            "architecture": {
                "tech_stack": {
                    "frontend": "HTML5 + CSS3 + Vanilla JavaScript",
                    "styling": "CSS Grid + Flexbox + CSS Variables + Animations",
                    "icons": "Inline SVG icons"
                },
                "component_structure": [
                    {"name": "Header", "description": "Navigation bar with logo and menu"},
                    {"name": "Hero", "description": "Main landing section with CTA"},
                    {"name": "Features", "description": "Feature grid section"},
                    {"name": "Content", "description": "Main content area"},
                    {"name": "Footer", "description": "Footer with links and info"}
                ],
                "design_system": {
                    "colors": {"primary": "#6366f1", "secondary": "#8b5cf6", "accent": "#06b6d4"},
                    "typography": "System font stack with gradient text accents",
                    "spacing": "8px base unit, consistent spacing scale",
                    "border_radius": "12px for cards, 8px for buttons, 20px for badges"
                }
            }
        }),
        "researcher": json.dumps({
            "research": {
                "findings": [
                    "Modern web applications prioritize performance and user experience",
                    "CSS Grid and Flexbox provide powerful layout capabilities without frameworks",
                    "CSS custom properties enable dynamic theming",
                    "Progressive enhancement ensures broad compatibility"
                ],
                "best_practices": [
                    "Mobile-first responsive design",
                    "Semantic HTML for accessibility",
                    "CSS animations for smooth interactions",
                    "Performance optimization with lazy loading"
                ],
                "recommendations": "Focus on clean, performant implementation using modern CSS features and vanilla JavaScript."
            }
        }),
        "engineer_default": _generate_landing_html(),
    }


def _generate_landing_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Built with Atoms</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--primary:#6366f1;--primary-dark:#4f46e5;--secondary:#8b5cf6;--accent:#06b6d4;--bg:#0f0f1a;--surface:#1a1a2e;--surface-2:#25253d;--text:#e2e8f0;--text-muted:#94a3b8;--gradient:linear-gradient(135deg,var(--primary),var(--secondary),var(--accent));--radius:12px;--shadow:0 4px 24px rgba(0,0,0,.3)}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;overflow-x:hidden}
.container{max-width:1200px;margin:0 auto;padding:0 24px}
header{position:fixed;top:0;left:0;right:0;z-index:100;background:rgba(15,15,26,.8);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,.05)}
nav{display:flex;align-items:center;justify-content:space-between;padding:16px 24px;max-width:1200px;margin:0 auto}
.logo{font-size:24px;font-weight:800;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.nav-links{display:flex;gap:32px;list-style:none}
.nav-links a{color:var(--text-muted);text-decoration:none;font-size:14px;font-weight:500;transition:color .3s}
.nav-links a:hover{color:var(--text)}
.btn{display:inline-flex;align-items:center;gap:8px;padding:10px 24px;border-radius:8px;font-weight:600;font-size:14px;cursor:pointer;transition:all .3s;border:none}
.btn-primary{background:var(--gradient);color:#fff}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 8px 30px rgba(99,102,241,.4)}
.btn-outline{background:transparent;color:var(--text);border:1px solid rgba(255,255,255,.15)}
.btn-outline:hover{border-color:var(--primary);color:var(--primary)}
.hero{min-height:100vh;display:flex;align-items:center;justify-content:center;text-align:center;padding:120px 24px 80px;position:relative}
.hero::before{content:'';position:absolute;top:0;left:0;right:0;bottom:0;background:radial-gradient(ellipse at 50% 0%,rgba(99,102,241,.15) 0%,transparent 70%);pointer-events:none}
.hero-content{position:relative;z-index:1}
.badge{display:inline-flex;align-items:center;gap:8px;padding:6px 16px;border-radius:20px;background:rgba(99,102,241,.1);border:1px solid rgba(99,102,241,.3);color:var(--primary);font-size:13px;font-weight:500;margin-bottom:24px}
.badge::before{content:'';width:6px;height:6px;border-radius:50%;background:var(--primary);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.hero h1{font-size:clamp(40px,8vw,72px);font-weight:800;line-height:1.1;margin-bottom:24px;letter-spacing:-0.02em}
.hero h1 span{background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero p{font-size:18px;color:var(--text-muted);max-width:600px;margin:0 auto 40px}
.hero-buttons{display:flex;gap:16px;justify-content:center;flex-wrap:wrap}
.features{padding:100px 0}
.section-header{text-align:center;margin-bottom:64px}
.section-header h2{font-size:36px;font-weight:700;margin-bottom:16px}
.section-header p{color:var(--text-muted);font-size:16px;max-width:500px;margin:0 auto}
.features-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:24px}
.feature-card{background:var(--surface);border:1px solid rgba(255,255,255,.06);border-radius:var(--radius);padding:32px;transition:all .4s}
.feature-card:hover{transform:translateY(-4px);border-color:rgba(99,102,241,.3);box-shadow:var(--shadow)}
.feature-icon{width:48px;height:48px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:24px;margin-bottom:20px}
.feature-card:nth-child(1) .feature-icon{background:rgba(99,102,241,.15)}
.feature-card:nth-child(2) .feature-icon{background:rgba(139,92,246,.15)}
.feature-card:nth-child(3) .feature-icon{background:rgba(6,182,212,.15)}
.feature-card:nth-child(4) .feature-icon{background:rgba(236,72,153,.15)}
.feature-card:nth-child(5) .feature-icon{background:rgba(245,158,11,.15)}
.feature-card:nth-child(6) .feature-icon{background:rgba(34,197,94,.15)}
.feature-card h3{font-size:18px;font-weight:600;margin-bottom:8px}
.feature-card p{color:var(--text-muted);font-size:14px}
.stats{padding:80px 0;background:var(--surface)}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:32px;text-align:center}
.stat h3{font-size:48px;font-weight:800;background:var(--gradient);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.stat p{color:var(--text-muted);font-size:14px;margin-top:8px}
.cta{padding:100px 0;text-align:center}
.cta-box{background:var(--surface);border:1px solid rgba(255,255,255,.06);border-radius:24px;padding:80px 40px;position:relative;overflow:hidden}
.cta-box::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--gradient)}
.cta h2{font-size:36px;font-weight:700;margin-bottom:16px}
.cta p{color:var(--text-muted);margin-bottom:32px;font-size:16px}
footer{border-top:1px solid rgba(255,255,255,.05);padding:40px 0}
.footer-content{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px}
.footer-content p{color:var(--text-muted);font-size:13px}
.footer-links{display:flex;gap:24px;list-style:none}
.footer-links a{color:var(--text-muted);text-decoration:none;font-size:13px;transition:color .3s}
.footer-links a:hover{color:var(--text)}
@media(max-width:768px){.nav-links{display:none}.hero h1{font-size:36px}.hero p{font-size:16px}}
.fade-in{opacity:0;transform:translateY(20px);animation:fadeIn .6s forwards}
@keyframes fadeIn{to{opacity:1;transform:translateY(0)}}
</style>
</head>
<body>
<header><nav>
<div class="logo">Atoms</div>
<ul class="nav-links"><li><a href="#">Features</a></li><li><a href="#">Pricing</a></li><li><a href="#">Docs</a></li></ul>
<button class="btn btn-primary">Get Started</button>
</nav></header>
<section class="hero"><div class="hero-content">
<div class="badge">AI-Powered Development</div>
<h1>Build Apps with<br><span>AI Agents</span></h1>
<p>Transform your ideas into production-ready applications with our team of AI agents. From design to deployment, automatically.</p>
<div class="hero-buttons">
<button class="btn btn-primary">Start Building</button>
<button class="btn btn-outline">Watch Demo</button>
</div>
</div></section>
<section class="features"><div class="container">
<div class="section-header"><h2>Powerful Features</h2><p>Everything you need to build modern web applications</p></div>
<div class="features-grid">
<div class="feature-card fade-in"><div class="feature-icon">🤖</div><h3>AI Agent Team</h3><p>Multiple specialized agents collaborate to build your application</p></div>
<div class="feature-card fade-in" style="animation-delay:.1s"><div class="feature-icon">⚡</div><h3>Instant Generation</h3><p>Go from idea to working prototype in seconds, not hours</p></div>
<div class="feature-card fade-in" style="animation-delay:.2s"><div class="feature-icon">🎨</div><h3>Beautiful Design</h3><p>Modern, responsive designs that look great on every device</p></div>
<div class="feature-card fade-in" style="animation-delay:.3s"><div class="feature-icon">🔄</div><h3>Iterative Refinement</h3><p>Chat with agents to refine and improve your application</p></div>
<div class="feature-card fade-in" style="animation-delay:.4s"><div class="feature-icon">📦</div><h3>Full Stack</h3><p>Complete frontend, backend, and database code generation</p></div>
<div class="feature-card fade-in" style="animation-delay:.5s"><div class="feature-icon">🚀</div><h3>One-Click Deploy</h3><p>Deploy your application to the cloud with a single click</p></div>
</div>
</div></section>
<section class="stats"><div class="container"><div class="stats-grid">
<div class="stat"><h3>10K+</h3><p>Applications Built</p></div>
<div class="stat"><h3>50K+</h3><p>Active Users</p></div>
<div class="stat"><h3>99.9%</h3><p>Uptime</p></div>
<div class="stat"><h3>3s</h3><p>Avg. Generation Time</p></div>
</div></div></section>
<section class="cta"><div class="container"><div class="cta-box">
<h2>Ready to Build Something Amazing?</h2>
<p>Join thousands of developers building with AI agents</p>
<button class="btn btn-primary">Get Started Free</button>
</div></div></section>
<footer><div class="container"><div class="footer-content">
<p>&copy; 2024 Atoms. Built with AI Agents.</p>
<ul class="footer-links"><li><a href="#">Privacy</a></li><li><a href="#">Terms</a></li><li><a href="#">Contact</a></li></ul>
</div></div></footer>
<script>
document.querySelectorAll('.feature-card').forEach(card=>{const observer=new IntersectionObserver(entries=>{entries.forEach(e=>{if(e.isIntersecting){e.target.style.animationPlayState='running';observer.unobserve(e.target)}})},{threshold:.1});card.style.animationPlayState='paused';observer.observe(card)});
</script>
</body>
</html>"""


MOCK_RESPONSES: dict[str, str] = _build_mock_responses()


class LLMProvider:
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.LLM_MODEL
        self.base_url = settings.OPENAI_BASE_URL or None
        self._client: Optional[AsyncOpenAI] = None
        if self.api_key:
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )

    @property
    def is_mock(self) -> bool:
        if settings.MOCK_MODE:
            return True
        return not self.api_key or self.api_key.startswith("your-")

    async def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        if self.is_mock:
            return self._mock_generate(system_prompt, user_prompt)
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content

    async def generate_stream(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> AsyncIterator[str]:
        if self.is_mock:
            full_text = self._mock_generate(system_prompt, user_prompt)
            words = full_text.split(" ")
            for i, word in enumerate(words):
                yield word + (" " if i < len(words) - 1 else "")
            return
        stream = await self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _mock_generate(self, system_prompt: str, user_prompt: str) -> str:
        prompt_lower = user_prompt.lower()
        sp = system_prompt.lower()
        if "team leader" in sp or "coordinator" in sp:
            return MOCK_RESPONSES["leader"]
        if "product manager" in sp:
            return MOCK_RESPONSES["pm"]
        if "system architect" in sp:
            return MOCK_RESPONSES["architect"]
        if "deep researcher" in sp:
            return MOCK_RESPONSES["researcher"]
        if "software engineer" in sp or "engineer" in sp:
            return self._generate_mock_code(prompt_lower)
        return MOCK_RESPONSES["engineer_default"]

    def _generate_mock_code(self, prompt: str) -> str:
        if any(w in prompt for w in ["dashboard", "admin", "analytics", "chart"]):
            return self._dashboard_html()
        if any(w in prompt for w in ["portfolio", "personal", "resume", "about"]):
            return self._portfolio_html()
        if any(w in prompt for w in ["landing", "marketing", "startup", "saas"]):
            return _generate_landing_html()
        if any(w in prompt for w in ["calculator", "tool", "converter"]):
            return self._calculator_html()
        if any(w in prompt for w in ["game", "2048", "1024", "snake", "tetris", "puzzle", "play"]):
            return self._game_2048_html()
        if any(w in prompt for w in ["todo", "task", "list", "checklist"]):
            return self._todo_html()
        if any(w in prompt for w in ["counter", "count", "increment"]):
            return self._counter_html()
        if any(w in prompt for w in ["ecommerce", "shop", "store", "product", "cart"]):
            return self._ecommerce_html()
        return _generate_landing_html()

    @staticmethod
    def _dashboard_html() -> str:
        return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Dashboard</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--primary:#6366f1;--bg:#0f172a;--surface:#1e293b;--surface-2:#334155;--text:#f1f5f9;--text-muted:#94a3b8;--green:#22c55e;--red:#ef4444;--yellow:#eab308;--blue:#3b82f6}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text)}
.dashboard{display:grid;grid-template-columns:240px 1fr;min-height:100vh}
.sidebar{background:var(--surface);padding:24px;border-right:1px solid rgba(255,255,255,.05)}
.logo{font-size:20px;font-weight:700;background:linear-gradient(135deg,var(--primary),#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:32px}
.nav-item{display:flex;align-items:center;gap:12px;padding:10px 16px;border-radius:8px;color:var(--text-muted);font-size:14px;cursor:pointer;transition:all .2s;margin-bottom:4px}
.nav-item:hover,.nav-item.active{background:rgba(99,102,241,.1);color:var(--text)}
.nav-item.active{border-left:2px solid var(--primary)}
.main{padding:32px;overflow-y:auto}
.header{display:flex;justify-content:space-between;align-items:center;margin-bottom:32px}
.header h1{font-size:24px;font-weight:700}
.search{padding:8px 16px;border-radius:8px;border:1px solid rgba(255,255,255,.1);background:var(--surface);color:var(--text);font-size:14px;width:300px}
.stats-row{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-bottom:32px}
.stat-card{background:var(--surface);border-radius:12px;padding:24px;border:1px solid rgba(255,255,255,.05)}
.stat-card .label{font-size:13px;color:var(--text-muted);margin-bottom:8px}
.stat-card .value{font-size:28px;font-weight:700}
.stat-card .change{font-size:12px;margin-top:8px}
.stat-card .change.up{color:var(--green)}
.stat-card .change.down{color:var(--red)}
.charts-row{display:grid;grid-template-columns:2fr 1fr;gap:20px;margin-bottom:32px}
.card{background:var(--surface);border-radius:12px;padding:24px;border:1px solid rgba(255,255,255,.05)}
.card-title{font-size:16px;font-weight:600;margin-bottom:20px}
.bar-chart{display:flex;align-items:flex-end;gap:12px;height:200px;padding-top:20px}
.bar{flex:1;border-radius:6px 6px 0 0;transition:height .5s;background:linear-gradient(to top,var(--primary),#8b5cf6)}
.bar:hover{opacity:.8}
.bar-label{font-size:11px;color:var(--text-muted);text-align:center;margin-top:8px}
.donut{width:160px;height:160px;border-radius:50%;background:conic-gradient(var(--primary) 0% 40%,#8b5cf6 40% 65%,var(--blue) 65% 85%,var(--surface-2) 85%);display:flex;align-items:center;justify-content:center;margin:0 auto 20px}
.donut-inner{width:100px;height:100px;border-radius:50%;background:var(--surface);display:flex;align-items:center;justify-content:center;font-size:20px;font-weight:700}
.legend{display:flex;flex-wrap:wrap;gap:16px;justify-content:center}
.legend-item{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--text-muted)}
.legend-dot{width:8px;height:8px;border-radius:50%}
.table-container{overflow-x:auto}
table{width:100%;border-collapse:collapse}
th{text-align:left;padding:12px 16px;font-size:12px;color:var(--text-muted);font-weight:600;border-bottom:1px solid rgba(255,255,255,.05)}
td{padding:12px 16px;font-size:14px;border-bottom:1px solid rgba(255,255,255,.03)}
.badge{padding:4px 10px;border-radius:20px;font-size:11px;font-weight:600}
.badge-green{background:rgba(34,197,94,.15);color:var(--green)}
.badge-yellow{background:rgba(234,179,8,.15);color:var(--yellow)}
.badge-red{background:rgba(239,68,68,.15);color:var(--red)}
@media(max-width:768px){.dashboard{grid-template-columns:1fr}.sidebar{display:none}.stats-row{grid-template-columns:repeat(2,1fr)}.charts-row{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="dashboard">
<aside class="sidebar">
<div class="logo">Dashboard</div>
<div class="nav-item active">📊 Overview</div>
<div class="nav-item">📈 Analytics</div>
<div class="nav-item">👥 Users</div>
<div class="nav-item">💰 Revenue</div>
<div class="nav-item">⚙️ Settings</div>
</aside>
<main class="main">
<div class="header"><h1>Overview</h1><input class="search" placeholder="Search..." /></div>
<div class="stats-row">
<div class="stat-card"><div class="label">Total Users</div><div class="value">12,847</div><div class="change up">↑ 12.5%</div></div>
<div class="stat-card"><div class="label">Revenue</div><div class="value">$48.2K</div><div class="change up">↑ 8.2%</div></div>
<div class="stat-card"><div class="label">Active Now</div><div class="value">1,429</div><div class="change up">↑ 3.1%</div></div>
<div class="stat-card"><div class="label">Bounce Rate</div><div class="value">24.3%</div><div class="change down">↓ 2.4%</div></div>
</div>
<div class="charts-row">
<div class="card">
<div class="card-title">Revenue Overview</div>
<div class="bar-chart" id="barChart"></div>
</div>
<div class="card">
<div class="card-title">Traffic Sources</div>
<div class="donut"><div class="donut-inner">75%</div></div>
<div class="legend">
<div class="legend-item"><div class="legend-dot" style="background:var(--primary)"></div>Direct 40%</div>
<div class="legend-item"><div class="legend-dot" style="background:#8b5cf6"></div>Social 25%</div>
<div class="legend-item"><div class="legend-dot" style="background:var(--blue)"></div>Search 20%</div>
<div class="legend-item"><div class="legend-dot" style="background:var(--surface-2)"></div>Other 15%</div>
</div>
</div>
</div>
<div class="card">
<div class="card-title">Recent Transactions</div>
<div class="table-container"><table>
<thead><tr><th>User</th><th>Type</th><th>Amount</th><th>Status</th></tr></thead>
<tbody>
<tr><td>Alice Johnson</td><td>Subscription</td><td>$49.99</td><td><span class="badge badge-green">Completed</span></td></tr>
<tr><td>Bob Smith</td><td>One-time</td><td>$12.50</td><td><span class="badge badge-green">Completed</span></td></tr>
<tr><td>Carol White</td><td>Subscription</td><td>$49.99</td><td><span class="badge badge-yellow">Pending</span></td></tr>
<tr><td>David Brown</td><td>Refund</td><td>$25.00</td><td><span class="badge badge-red">Refunded</span></td></tr>
<tr><td>Eve Davis</td><td>Subscription</td><td>$99.99</td><td><span class="badge badge-green">Completed</span></td></tr>
</tbody>
</table></div>
</div>
</main>
</div>
<script>
const bars=[45,62,38,71,55,83,67,74,59,91,78,86];
const months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const chart=document.getElementById('barChart');
bars.forEach((h,i)=>{const col=document.createElement('div');col.style.cssText='display:flex;flex-direction:column;align-items:center;flex:1';const bar=document.createElement('div');bar.className='bar';bar.style.height=h+'%';const label=document.createElement('div');label.className='bar-label';label.textContent=months[i];col.appendChild(bar);col.appendChild(label);chart.appendChild(col)});
</script>
</body>
</html>"""

    @staticmethod
    def _portfolio_html() -> str:
        return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Portfolio</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--primary:#6366f1;--bg:#0a0a0a;--surface:#161616;--text:#fafafa;--text-muted:#888}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text)}
nav{display:flex;justify-content:space-between;align-items:center;padding:20px 40px;position:fixed;width:100%;z-index:100;background:rgba(10,10,10,.8);backdrop-filter:blur(20px)}
.logo{font-weight:800;font-size:20px}
.links{display:flex;gap:32px;list-style:none}
.links a{color:var(--text-muted);text-decoration:none;font-size:14px;transition:color .3s}
.links a:hover{color:var(--text)}
.hero{min-height:100vh;display:flex;align-items:center;padding:0 40px}
.hero-inner{max-width:800px}
.hero h1{font-size:clamp(40px,6vw,64px);font-weight:800;line-height:1.1;margin-bottom:24px}
.hero h1 span{color:var(--primary)}
.hero p{font-size:18px;color:var(--text-muted);max-width:500px;line-height:1.8;margin-bottom:40px}
.btn{display:inline-block;padding:12px 32px;border-radius:8px;background:var(--primary);color:#fff;text-decoration:none;font-weight:600;transition:transform .3s}
.btn:hover{transform:translateY(-2px)}
section{padding:100px 40px}
.section-title{font-size:12px;text-transform:uppercase;letter-spacing:3px;color:var(--primary);margin-bottom:16px}
.projects-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px;margin-top:40px}
.project-card{background:var(--surface);border-radius:16px;overflow:hidden;transition:transform .3s}
.project-card:hover{transform:translateY(-8px)}
.project-img{height:200px;background:linear-gradient(135deg,var(--primary),#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:48px}
.project-info{padding:24px}
.project-info h3{font-size:18px;font-weight:600;margin-bottom:8px}
.project-info p{font-size:14px;color:var(--text-muted)}
.tags{display:flex;gap:8px;margin-top:16px;flex-wrap:wrap}
.tag{padding:4px 12px;border-radius:20px;background:rgba(99,102,241,.1);color:var(--primary);font-size:12px}
.skills{display:flex;flex-wrap:wrap;gap:16px;margin-top:40px}
.skill{padding:12px 24px;background:var(--surface);border-radius:8px;font-size:14px;font-weight:500}
footer{padding:40px;text-align:center;color:var(--text-muted);font-size:13px;border-top:1px solid rgba(255,255,255,.05)}
@media(max-width:768px){.links{display:none}nav{padding:16px 20px}.hero{padding:0 20px}}
</style>
</head>
<body>
<nav><div class="logo">JD</div><ul class="links"><li><a href="#work">Work</a></li><li><a href="#skills">Skills</a></li><li><a href="#contact">Contact</a></li></ul></nav>
<section class="hero"><div class="hero-inner">
<h1>Hi, I'm <span>John Doe</span></h1>
<p>A full-stack developer passionate about building beautiful, functional web applications that make a difference.</p>
<a href="#work" class="btn">View My Work</a>
</div></section>
<section id="work">
<div class="section-title">Selected Work</div>
<h2 style="font-size:32px;font-weight:700">Recent Projects</h2>
<div class="projects-grid">
<div class="project-card"><div class="project-img">🎨</div><div class="project-info"><h3>Design System</h3><p>A comprehensive design system with 50+ components</p><div class="tags"><span class="tag">React</span><span class="tag">TypeScript</span><span class="tag">Storybook</span></div></div></div>
<div class="project-card"><div class="project-img">📊</div><div class="project-info"><h3>Analytics Dashboard</h3><p>Real-time data visualization platform</p><div class="tags"><span class="tag">Vue</span><span class="tag">D3.js</span><span class="tag">WebSocket</span></div></div></div>
<div class="project-card"><div class="project-img">🚀</div><div class="project-info"><h3>Launch Platform</h3><p>SaaS deployment and monitoring tool</p><div class="tags"><span class="tag">Node.js</span><span class="tag">AWS</span><span class="tag">Docker</span></div></div></div>
</div>
</section>
<section id="skills">
<div class="section-title">Expertise</div>
<h2 style="font-size:32px;font-weight:700">Skills & Technologies</h2>
<div class="skills">
<div class="skill">JavaScript</div><div class="skill">TypeScript</div><div class="skill">React</div><div class="skill">Vue</div><div class="skill">Node.js</div><div class="skill">Python</div><div class="skill">PostgreSQL</div><div class="skill">Docker</div><div class="skill">AWS</div><div class="skill">GraphQL</div>
</div>
</section>
<footer id="contact"><p>© 2024 John Doe · Built with ❤️</p></footer>
</body>
</html>"""

    @staticmethod
    def _calculator_html() -> str:
        return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Calculator</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);min-height:100vh;display:flex;align-items:center;justify-content:center}
.calculator{background:rgba(255,255,255,.05);backdrop-filter:blur(20px);border-radius:24px;padding:32px;width:340px;border:1px solid rgba(255,255,255,.1);box-shadow:0 8px 32px rgba(0,0,0,.3)}
.display{background:rgba(0,0,0,.3);border-radius:16px;padding:20px;margin-bottom:20px;text-align:right;min-height:80px;display:flex;flex-direction:column;justify-content:flex-end}
.expression{color:rgba(255,255,255,.5);font-size:14px;margin-bottom:8px;min-height:20px}
.result{color:#fff;font-size:36px;font-weight:700;word-break:break-all}
.buttons{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.btn{padding:18px;border-radius:12px;border:none;font-size:18px;font-weight:600;cursor:pointer;transition:all .2s}
.btn:active{transform:scale(.95)}
.btn-num{background:rgba(255,255,255,.08);color:#fff}
.btn-num:hover{background:rgba(255,255,255,.15)}
.btn-op{background:rgba(99,102,241,.3);color:#818cf8}
.btn-op:hover{background:rgba(99,102,241,.5)}
.btn-func{background:rgba(255,255,255,.04);color:rgba(255,255,255,.6)}
.btn-func:hover{background:rgba(255,255,255,.1)}
.btn-eq{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff}
.btn-eq:hover{opacity:.9}
.btn-clear{background:rgba(239,68,68,.2);color:#f87171}
.btn-clear:hover{background:rgba(239,68,68,.3)}
</style>
</head>
<body>
<div class="calculator">
<div class="display"><div class="expression" id="expr"></div><div class="result" id="result">0</div></div>
<div class="buttons">
<button class="btn btn-clear" onclick="clearAll()">AC</button>
<button class="btn btn-func" onclick="toggleSign()">±</button>
<button class="btn btn-func" onclick="percent()">%</button>
<button class="btn btn-op" onclick="setOp('/')">÷</button>
<button class="btn btn-num" onclick="appendNum('7')">7</button>
<button class="btn btn-num" onclick="appendNum('8')">8</button>
<button class="btn btn-num" onclick="appendNum('9')">9</button>
<button class="btn btn-op" onclick="setOp('*')">×</button>
<button class="btn btn-num" onclick="appendNum('4')">4</button>
<button class="btn btn-num" onclick="appendNum('5')">5</button>
<button class="btn btn-num" onclick="appendNum('6')">6</button>
<button class="btn btn-op" onclick="setOp('-')">−</button>
<button class="btn btn-num" onclick="appendNum('1')">1</button>
<button class="btn btn-num" onclick="appendNum('2')">2</button>
<button class="btn btn-num" onclick="appendNum('3')">3</button>
<button class="btn btn-op" onclick="setOp('+')">+</button>
<button class="btn btn-num" onclick="appendNum('0')" style="grid-column:span 2">0</button>
<button class="btn btn-num" onclick="appendDot()">.</button>
<button class="btn btn-eq" onclick="calculate()">=</button>
</div>
</div>
<script>
let current='0',expression='',operator=null,prev=null,reset=false;
const display=document.getElementById('result'),exprEl=document.getElementById('expr');
function updateDisplay(){display.textContent=current;exprEl.textContent=expression}
function appendNum(n){if(reset){current=n;reset=false}else{current=current==='0'?n:current+n}updateDisplay()}
function appendDot(){if(!current.includes('.')){current+='.';updateDisplay()}}
function setOp(op){if(prev!==null&&operator)calculate();prev=parseFloat(current);operator=op;expression=current+' '+op+' ';reset=true;updateDisplay()}
function calculate(){if(operator===null||prev===null)return;const cur=parseFloat(current);let r;switch(operator){case'+':r=prev+cur;break;case'-':r=prev-cur;break;case'*':r=prev*cur;break;case'/':r=cur!==0?prev/cur:'Error';break}expression='';operator=null;prev=null;current=String(r);reset=true;updateDisplay()}
function clearAll(){current='0';expression='';operator=null;prev=null;reset=false;updateDisplay()}
function toggleSign(){current=String(-parseFloat(current));updateDisplay()}
function percent(){current=String(parseFloat(current)/100);updateDisplay()}
</script>
</body>
</html>"""


    @staticmethod
    def _game_2048_html() -> str:
        return GAME_2048_HTML

    @staticmethod
    def _todo_html() -> str:
        return TODO_HTML

    @staticmethod
    def _counter_html() -> str:
        return COUNTER_HTML

    @staticmethod
    def _ecommerce_html() -> str:
        return ECOMMERCE_HTML


llm_provider = LLMProvider() = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>1024 Game</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f0f1a;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;color:#e2e8f0;user-select:none;-webkit-user-select:none;touch-action:none}
.header{display:flex;align-items:center;justify-content:space-between;width:360px;margin-bottom:16px}
.title{font-size:36px;font-weight:800;background:linear-gradient(135deg,#6366f1,#8b5cf6,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.scores{display:flex;gap:12px}
.score-box{background:#1a1a2e;border-radius:8px;padding:8px 16px;text-align:center;border:1px solid rgba(255,255,255,.06)}
.score-label{font-size:10px;color:#94a3b8;text-transform:uppercase;letter-spacing:1px}
.score-value{font-size:20px;font-weight:700}
.board{background:#1a1a2e;border-radius:12px;padding:12px;position:relative;border:1px solid rgba(255,255,255,.06);box-shadow:0 8px 32px rgba(0,0,0,.3)}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.cell{width:78px;height:78px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:28px;transition:all .12s;background:#25253d}
.cell[data-value="2"]{background:#3b3b5c;color:#c4b5fd;font-size:28px}
.cell[data-value="4"]{background:#4c3d7a;color:#c4b5fd;font-size:28px}
.cell[data-value="8"]{background:#6d28d9;color:#fff;font-size:28px}
.cell[data-value="16"]{background:#7c3aed;color:#fff;font-size:26px}
.cell[data-value="32"]{background:#8b5cf6;color:#fff;font-size:26px}
.cell[data-value="64"]{background:#a855f7;color:#fff;font-size:26px}
.cell[data-value="128"]{background:#c084fc;color:#fff;font-size:22px}
.cell[data-value="256"]{background:#d946ef;color:#fff;font-size:22px}
.cell[data-value="512"]{background:#e879f9;color:#fff;font-size:22px}
.cell[data-value="1024"]{background:linear-gradient(135deg,#6366f1,#06b6d4);color:#fff;font-size:18px;text-shadow:0 0 10px rgba(99,102,241,.5)}
.cell[data-value="2048"]{background:linear-gradient(135deg,#f59e0b,#ef4444);color:#fff;font-size:18px;text-shadow:0 0 10px rgba(245,158,11,.5)}
.cell.new{animation:popIn .2s ease}
.cell.merged{animation:popMerge .2s ease}
@keyframes popIn{0%{transform:scale(0)}100%{transform:scale(1)}}
@keyframes popMerge{0%{transform:scale(1)}50%{transform:scale(1.15)}100%{transform:scale(1)}}
.controls{display:flex;gap:12px;margin-top:16px}
.btn{padding:10px 20px;border-radius:8px;border:none;font-weight:600;font-size:14px;cursor:pointer;transition:all .2s}
.btn-primary{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 4px 16px rgba(99,102,241,.4)}
.btn-outline{background:transparent;color:#94a3b8;border:1px solid rgba(255,255,255,.1)}
.btn-outline:hover{border-color:#6366f1;color:#6366f1}
.msg{margin-top:16px;font-size:16px;font-weight:600;min-height:24px}
.msg.win{color:#22c55e}.msg.lose{color:#ef4444}
.instructions{margin-top:16px;color:#6366f1;font-size:12px;text-align:center}
@media(max-width:420px){.board{padding:8px}.cell{width:68px;height:68px;font-size:22px}.header{width:320px}}
</style>
</head>
<body>
<div class="header">
<div class="title">1024</div>
<div class="scores">
<div class="score-box"><div class="score-label">Score</div><div class="score-value" id="score">0</div></div>
<div class="score-box"><div class="score-label">Best</div><div class="score-value" id="best">0</div></div>
</div>
</div>
<div class="board"><div class="grid" id="grid"></div></div>
<div class="controls">
<button class="btn btn-primary" onclick="newGame()">New Game</button>
<button class="btn btn-outline" onclick="undo()">Undo</button>
</div>
<div class="msg" id="msg"></div>
<div class="instructions">Arrow keys / WASD / Swipe to move</div>
<script>
const SIZE=4;let board,score,best=0,prevState,msgEl;
function init(){board=Array.from({length:SIZE},()=>Array(SIZE).fill(0));score=0;prevState=null;msgEl=document.getElementById('msg');msgEl.textContent='';msgEl.className='msg';addRandom();addRandom();render()}
function addRandom(){const empty=[];for(let r=0;r<SIZE;r++)for(let c=0;c<SIZE;c++)if(board[r][c]===0)empty.push([r,c]);if(!empty.length)return;const[r,c]=empty[Math.floor(Math.random()*empty.length)];board[r][c]=Math.random()<.9?2:4;const cell=document.querySelector(`[data-row="${r}"][data-col="${c}"]`);if(cell)cell.classList.add('new')}
function render(){const grid=document.getElementById('grid');grid.innerHTML='';for(let r=0;r<SIZE;r++)for(let c=0;c<SIZE;c++){const cell=document.createElement('div');cell.className='cell';cell.dataset.row=r;cell.dataset.col=c;cell.dataset.value=board[r][c];cell.textContent=board[r][c]||'';grid.appendChild(cell)}document.getElementById('score').textContent=score;if(score>best){best=score;document.getElementById('best').textContent=best}}
function slide(row){let a=row.filter(v=>v!==0);const merged=[];for(let i=0;i<a.length-1;i++){if(a[i]===a[i+1]){a[i]*=2;score+=a[i];a.splice(i+1,1);merged.push(i)}}const padded=a.concat(Array(SIZE-a.length).fill(0));return{result:padded,merged}}
function move(dir){const old=board.map(r=>[...r]);const oldScore=score;let moved=false;const mergedCells=[];if(dir==='left'){for(let r=0;r<SIZE;r++){const{result,merged}=slide(board[r]);if(result.join()!==board[r].join())moved=true;board[r]=result;merged.forEach(c=>mergedCells.push([r,c]))}}else if(dir==='right'){for(let r=0;r<SIZE;r++){const{result,merged}=slide([...board[r]].reverse());result.reverse();if(result.join()!==board[r].join())moved=true;board[r]=result;merged.forEach(c=>mergedCells.push([r,SIZE-1-c]))}}else if(dir==='up'){for(let c=0;c<SIZE;c++){const col=board.map(r=>r[c]);const{result,merged}=slide(col);if(result.join()!==col.join())moved=true;result.forEach((v,r)=>board[r][c]=v);merged.forEach(r=>mergedCells.push([r,c]))}}else if(dir==='down'){for(let c=0;c<SIZE;c++){const col=board.map(r=>r[c]).reverse();const{result,merged}=slide(col);result.reverse();if(result.join()!==col.reverse().join())moved=true;result.forEach((v,r)=>board[r][c]=v);merged.forEach(r=>mergedCells.push([SIZE-1-r,c]))}}if(!moved)return false;prevState={board:old,score:oldScore};addRandom();render();mergedCells.forEach(([r,c])=>{const cell=document.querySelector(`[data-row="${r}"][data-col="${c}"]`);if(cell)cell.classList.add('merged')});checkState();return true}
function checkState(){for(let r=0;r<SIZE;r++)for(let c=0;c<SIZE;c++)if(board[r][c]===1024){msgEl.textContent='You Win!';msgEl.className='msg win';return}if(!canMove()){msgEl.textContent='Game Over!';msgEl.className='msg lose'}}
function canMove(){for(let r=0;r<SIZE;r++)for(let c=0;c<SIZE;c++){if(board[r][c]===0)return true;if(c<SIZE-1&&board[r][c]===board[r][c+1])return true;if(r<SIZE-1&&board[r][c]===board[r+1][c])return true}return false}
function newGame(){init()}
function undo(){if(!prevState)return;board=prevState.board;score=prevState.score;prevState=null;msgEl.textContent='';msgEl.className='msg';render()}
document.addEventListener('keydown',e=>{const map={ArrowLeft:'left',ArrowRight:'right',ArrowUp:'up',ArrowDown:'down',a:'left',d:'right',w:'up',s:'down'};const dir=map[e.key];if(dir){e.preventDefault();move(dir)}});
let touchStartX,touchStartY;document.addEventListener('touchstart',e=>{touchStartX=e.touches[0].clientX;touchStartY=e.touches[0].clientY});document.addEventListener('touchend',e=>{if(!touchStartX)return;const dx=e.changedTouches[0].clientX-touchStartX;const dy=e.changedTouches[0].clientY-touchStartY;const absDx=Math.abs(dx),absDy=Math.abs(dy);if(Math.max(absDx,absDy)<30)return;move(absDx>absDy?(dx>0?'right':'left'):(dy>0?'down':'up'));touchStartX=touchStartY=null});
init();
</script>
</body>
</html>"""


TODO_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Todo App</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f0f1a;min-height:100vh;display:flex;align-items:center;justify-content:center;color:#e2e8f0}
.container{width:420px;padding:32px}
h1{font-size:28px;font-weight:800;background:linear-gradient(135deg,#6366f1,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:24px}
.input-row{display:flex;gap:8px;margin-bottom:24px}
input{flex:1;padding:12px 16px;border-radius:8px;border:1px solid rgba(255,255,255,.1);background:#1a1a2e;color:#e2e8f0;font-size:14px;outline:none}
input:focus{border-color:#6366f1}
.add-btn{padding:12px 20px;border-radius:8px;border:none;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;font-weight:600;cursor:pointer;font-size:14px}
.filters{display:flex;gap:8px;margin-bottom:16px}
.filter{padding:6px 14px;border-radius:20px;border:1px solid rgba(255,255,255,.1);background:transparent;color:#94a3b8;font-size:12px;cursor:pointer}
.filter.active{background:rgba(99,102,241,.2);color:#818cf8;border-color:rgba(99,102,241,.3)}
.todo-list{display:flex;flex-direction:column;gap:8px}
.todo{display:flex;align-items:center;gap:12px;padding:14px 16px;background:#1a1a2e;border-radius:8px;border:1px solid rgba(255,255,255,.06);transition:all .2s}
.todo.done{opacity:.5}
.todo.done .todo-text{text-decoration:line-through}
.check{width:22px;height:22px;border-radius:50%;border:2px solid rgba(255,255,255,.2);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .2s;flex-shrink:0}
.check:hover{border-color:#6366f1}
.check.checked{background:#6366f1;border-color:#6366f1}
.check.checked::after{content:'✓';color:#fff;font-size:12px;font-weight:700}
.todo-text{flex:1;font-size:14px}
.del{background:none;border:none;color:#ef4444;cursor:pointer;font-size:16px;opacity:0;transition:opacity .2s}
.todo:hover .del{opacity:1}
.empty{text-align:center;color:#6366f1;padding:40px;font-size:14px}
.count{color:#94a3b8;font-size:12px;margin-top:16px}
</style>
</head>
<body>
<div class="container">
<h1>Todo List</h1>
<div class="input-row"><input id="inp" placeholder="Add a task..." onkeydown="if(event.key==='Enter')addTodo()"><button class="add-btn" onclick="addTodo()">Add</button></div>
<div class="filters"><button class="filter active" onclick="setFilter('all',this)">All</button><button class="filter" onclick="setFilter('active',this)">Active</button><button class="filter" onclick="setFilter('done',this)">Done</button></div>
<div class="todo-list" id="list"></div>
<div class="count" id="count"></div>
</div>
<script>
let todos=[],filter='all';
function addTodo(){const inp=document.getElementById('inp'),t=inp.value.trim();if(!t)return;todos.push({id:Date.now(),text:t,done:false});inp.value='';render()}
function toggle(id){const t=todos.find(t=>t.id===id);if(t)t.done=!t.done;render()}
function del(id){todos=todos.filter(t=>t.id!==id);render()}
function setFilter(f,el){filter=f;document.querySelectorAll('.filter').forEach(b=>b.classList.remove('active'));el.classList.add('active');render()}
function render(){const list=document.getElementById('list');const filtered=filter==='all'?todos:filter==='active'?todos.filter(t=>!t.done):todos.filter(t=>t.done);if(!filtered.length){list.innerHTML='<div class="empty">'+(filter==='all'?'Add your first task!':filter==='active'?'No active tasks':'No completed tasks')+'</div>'}else{list.innerHTML=filtered.map(t=>'<div class="todo'+(t.done?' done':'')+'"><div class="check'+(t.done?' checked':'')+'" onclick="toggle('+t.id+')"></div><span class="todo-text">'+t.text+'</span><button class="del" onclick="del('+t.id+')">✕</button></div>').join('')}const active=todos.filter(t=>!t.done).length;document.getElementById('count').textContent=active+' task'+(active!==1?'s':'')+' remaining'}
render();
</script>
</body>
</html>"""


COUNTER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Counter</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#0f0f1a;min-height:100vh;display:flex;align-items:center;justify-content:center;color:#e2e8f0}
.counter{text-align:center}
.count{font-size:96px;font-weight:800;background:linear-gradient(135deg,#6366f1,#8b5cf6,#06b6d4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:32px;transition:transform .1s}
.count.bump{transform:scale(1.1)}
.buttons{display:flex;gap:16px;justify-content:center}
.btn{width:64px;height:64px;border-radius:16px;border:none;font-size:28px;font-weight:700;cursor:pointer;transition:all .2s}
.btn:active{transform:scale(.9)}
.btn-inc{background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff}
.btn-dec{background:rgba(239,68,68,.2);color:#f87171}
.btn-reset{background:rgba(255,255,255,.06);color:#94a3b8;font-size:16px}
.step{margin-top:24px;color:#94a3b8;font-size:14px}
.step input{width:60px;padding:4px 8px;border-radius:6px;border:1px solid rgba(255,255,255,.1);background:#1a1a2e;color:#e2e8f0;text-align:center;font-size:14px}
</style>
</head>
<body>
<div class="counter">
<div class="count" id="count">0</div>
<div class="buttons">
<button class="btn btn-dec" onclick="change(-1)">−</button>
<button class="btn btn-reset" onclick="reset()">↺</button>
<button class="btn btn-inc" onclick="change(1)">+</button>
</div>
<div class="step">Step: <input id="step" type="number" value="1" min="1" max="100"></div>
</div>
<script>
let count=0;const el=document.getElementById('count');
function change(d){count+=d*parseInt(document.getElementById('step').value||1);el.textContent=count;el.classList.add('bump');setTimeout(()=>el.classList.remove('bump'),100)}
function reset(){count=0;el.textContent=0}
</script>
</body>
</html>"""


ECOMMERCE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Shop</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--primary:#6366f1;--bg:#0f0f1a;--surface:#1a1a2e;--text:#e2e8f0;--muted:#94a3b8}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text)}
nav{display:flex;justify-content:space-between;align-items:center;padding:16px 24px;background:var(--surface);border-bottom:1px solid rgba(255,255,255,.05)}
.logo{font-size:20px;font-weight:800;background:linear-gradient(135deg,#6366f1,#8b5cf6);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.cart-btn{position:relative;background:none;border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:8px 16px;color:var(--text);cursor:pointer;font-size:14px}
.cart-badge{position:absolute;top:-6px;right:-6px;background:#ef4444;color:#fff;width:18px;height:18px;border-radius:50%;font-size:10px;display:flex;align-items:center;justify-content:center}
.products{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px;padding:32px;max-width:1200px;margin:0 auto}
.card{background:var(--surface);border-radius:12px;overflow:hidden;border:1px solid rgba(255,255,255,.06);transition:transform .3s}
.card:hover{transform:translateY(-4px)}
.card-img{height:180px;display:flex;align-items:center;justify-content:center;font-size:48px}
.card-body{padding:20px}
.card-body h3{font-size:16px;font-weight:600;margin-bottom:4px}
.card-body p{color:var(--muted);font-size:13px;margin-bottom:12px}
.price{font-size:20px;font-weight:700;color:var(--primary)}
.add-btn{width:100%;padding:10px;border-radius:8px;border:none;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#fff;font-weight:600;cursor:pointer;font-size:13px;margin-top:12px}
.add-btn:hover{opacity:.9}
</style>
</head>
<body>
<nav><div class="logo">Shop</div><button class="cart-btn" onclick="showCart()">🛒 Cart<span class="cart-badge" id="badge">0</span></button></nav>
<div class="products" id="products"></div>
<script>
const products=[{id:1,name:'Wireless Headphones',desc:'Premium sound quality',price:79.99,emoji:'🎧'},{id:2,name:'Smart Watch',desc:'Track your fitness',price:199.99,emoji:'⌚'},{id:3,name:'Laptop Stand',desc:'Ergonomic design',price:49.99,emoji:'💻'},{id:4,name:'Mechanical Keyboard',desc:'Cherry MX switches',price:129.99,emoji:'⌨️'},{id:5,name:'Webcam HD',desc:'1080p with mic',price:59.99,emoji:'📷'},{id:6,name:'Desk Lamp',desc:'LED with dimmer',price:34.99,emoji:'💡'}];
let cart=[];
function render(){document.getElementById('products').innerHTML=products.map(p=>'<div class="card"><div class="card-img" style="background:linear-gradient(135deg,rgba(99,102,241,.2),rgba(139,92,246,.2))">'+p.emoji+'</div><div class="card-body"><h3>'+p.name+'</h3><p>'+p.desc+'</p><div class="price">$'+p.price.toFixed(2)+'</div><button class="add-btn" onclick="addToCart('+p.id+')">Add to Cart</button></div></div>').join('')}
function addToCart(id){const p=products.find(x=>x.id===id);if(p)cart.push(p);document.getElementById('badge').textContent=cart.length}
function showCart(){const total=cart.reduce((s,p)=>s+p.price,0);alert('Cart: '+cart.length+' items\\nTotal: $'+total.toFixed(2))}
render();
</script>
</body>
</html>"""
