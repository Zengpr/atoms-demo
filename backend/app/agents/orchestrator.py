import json
import re
import asyncio
import time
import logging
from typing import Any, AsyncIterator

logger = logging.getLogger(__name__)
from app.agents.base import BaseAgent
from app.agents.leader import LeaderAgent
from app.agents.pm import PMAgent
from app.agents.architect import ArchitectAgent
from app.agents.engineer import EngineerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.seo import SEOAgent
from app.agents.ads import AdsAgent
from app.agents.data_analyst import DataAnalystAgent
from app.utils.html_utils import extract_html
from app.utils.llm import llm_provider


MOCK_DELAY = 0.5
HEARTBEAT_SEC = 3


async def _mock_delay():
    if llm_provider.is_mock:
        await asyncio.sleep(MOCK_DELAY)


async def _heartbeat(name: str, emoji: str, message: str) -> AsyncIterator[dict[str, Any]]:
    while True:
        await asyncio.sleep(HEARTBEAT_SEC)
        yield {
            "event": "agent_thinking",
            "data": {"agent": name, "emoji": emoji, "message": message},
        }


async def _stream_llm_as_events(
    agent: BaseAgent,
    stream_method: str,
    task: str,
    context: dict[str, Any],
    waiting_msg: str = "",
) -> AsyncIterator[dict[str, Any]]:
    method = getattr(agent, stream_method)
    full_text = ""
    first_token = True
    gen = method(task, context)
    heartbeat_gen = _heartbeat(agent.name, agent.avatar_emoji, waiting_msg or f"正在等待 {agent.name}...")

    gen_task = asyncio.create_task(gen.__anext__())
    hb_task = asyncio.create_task(heartbeat_gen.__anext__())

    done_set: set[asyncio.Task] = set()
    pending = {gen_task, hb_task}

    try:
        while pending:
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            done_set.update(done)

            for t in done:
                if t is gen_task:
                    try:
                        chunk = t.result()
                        if first_token:
                            first_token = False
                            hb_task.cancel()
                            try:
                                await hb_task
                            except (asyncio.CancelledError, StopAsyncIteration):
                                pass
                        full_text += chunk
                        yield {
                            "event": "agent_stream",
                            "data": {"agent": agent.name, "emoji": agent.avatar_emoji, "chunk": chunk},
                        }
                        gen_task = asyncio.create_task(gen.__anext__())
                        pending.add(gen_task)
                    except StopAsyncIteration:
                        pass
                    except Exception as e:
                        logger.error(f"Stream error for {agent.name}: {e}")
                elif t is hb_task:
                    try:
                        ev = t.result()
                        yield ev
                        hb_task = asyncio.create_task(heartbeat_gen.__anext__())
                        pending.add(hb_task)
                    except (StopAsyncIteration, asyncio.CancelledError):
                        pass

    finally:
        gen_task.cancel()
        hb_task.cancel()
        for t in {gen_task, hb_task}:
            try:
                await t
            except (asyncio.CancelledError, StopAsyncIteration, Exception):
                pass

    yield {
        "event": "agent_stream_done",
        "data": {"agent": agent.name, "emoji": agent.avatar_emoji, "full_text": full_text},
    }


async def _collect_stream(stream: AsyncIterator[dict[str, Any]]) -> str:
    full = ""
    async for ev in stream:
        if ev["event"] == "agent_stream_done":
            full = ev["data"]["full_text"]
    return full


async def _collect_code_with_heartbeat(
    agent: BaseAgent,
    task: str,
    context: dict[str, Any],
    waiting_msg: str = "",
) -> AsyncIterator[dict[str, Any]]:
    gen = agent.act_stream(task, context)
    hb = _heartbeat(agent.name, agent.avatar_emoji, waiting_msg or f"{agent.avatar_emoji} {agent.name} 正在生成代码...")
    code = ""
    act_task = asyncio.create_task(gen.__anext__())
    hb_task = asyncio.create_task(hb.__anext__())
    pending = {act_task, hb_task}
    first_token = True
    try:
        while pending:
            done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
            for t in done:
                if t is act_task:
                    try:
                        chunk = t.result()
                        if first_token:
                            first_token = False
                            hb_task.cancel()
                            try:
                                await hb_task
                            except (asyncio.CancelledError, StopAsyncIteration):
                                pass
                        code += chunk
                        act_task = asyncio.create_task(gen.__anext__())
                        pending.add(act_task)
                    except StopAsyncIteration:
                        pass
                    except Exception as e:
                        logger.error(f"Code collect error for {agent.name}: {e}")
                elif t is hb_task:
                    try:
                        ev = t.result()
                        yield ev
                        hb_task = asyncio.create_task(hb.__anext__())
                        pending.add(hb_task)
                    except (StopAsyncIteration, asyncio.CancelledError):
                        pass
    finally:
        act_task.cancel()
        hb_task.cancel()
        for t in {act_task, hb_task}:
            try:
                await t
            except (asyncio.CancelledError, StopAsyncIteration, Exception):
                pass

    yield {
        "event": "code_collected",
        "data": {"agent": agent.name, "emoji": agent.avatar_emoji, "code": code},
    }


def _extract_html(text: str) -> str:
    return extract_html(text)


def _try_parse_json(text: str) -> dict[str, Any] | None:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass
    first_brace = text.find('{')
    last_brace = text.rfind('}')
    if first_brace != -1 and last_brace > first_brace:
        try:
            return json.loads(text[first_brace:last_brace + 1])
        except json.JSONDecodeError:
            pass
    return None


AGENT_NAME_TO_KEY: dict[str, str] = {
    "Mike": "leader",
    "Emma": "pm",
    "Bob": "architect",
    "Alex": "engineer",
    "Iris": "researcher",
    "Sarah": "seo",
    "Adrian": "ads",
    "David": "data_analyst",
}


class Orchestrator:
    def __init__(self):
        self.agents: dict[str, BaseAgent] = {
            "leader": LeaderAgent(),
            "pm": PMAgent(),
            "architect": ArchitectAgent(),
            "engineer": EngineerAgent(),
            "researcher": ResearcherAgent(),
            "seo": SEOAgent(),
            "ads": AdsAgent(),
            "data_analyst": DataAnalystAgent(),
        }

    def _resolve_agent_key(self, key_or_name: str) -> str:
        if key_or_name in self.agents:
            return key_or_name
        mapped = AGENT_NAME_TO_KEY.get(key_or_name)
        if mapped:
            return mapped
        lower = key_or_name.lower()
        if lower in self.agents:
            return lower
        return "engineer"

    def get_agent(self, name: str) -> BaseAgent | None:
        return self.agents.get(name)

    async def run_engineer_mode(self, task: str, context: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        engineer = self.agents["engineer"]
        start = time.time()

        yield {
            "event": "agent_thinking",
            "data": {"agent": engineer.name, "emoji": engineer.avatar_emoji, "message": f"{engineer.avatar_emoji} {engineer.name} 正在处理您的请求..."},
        }

        act_prompt = engineer._build_act_prompt(task, context)
        full_text = ""
        code_started = False

        CODE_MARKERS = ["<!doctype", "<html", "```html", "```htm"]

        def _find_code_start(text: str) -> int:
            lower = text.lower()
            idx = -1
            for marker in CODE_MARKERS:
                pos = lower.find(marker)
                if pos != -1 and (idx == -1 or pos < idx):
                    idx = pos
            return idx

        gen = engineer.act_stream(task, context) if llm_provider.is_mock else llm_provider.generate_stream(engineer.get_act_system_prompt(), act_prompt, temperature=0.4, max_tokens=32768)
        hb = _heartbeat(engineer.name, engineer.avatar_emoji, "正在连接AI模型...")
        act_task = asyncio.create_task(gen.__anext__())
        hb_task = asyncio.create_task(hb.__anext__())
        pending = {act_task, hb_task}
        first_token = True

        try:
            while pending:
                done, pending_new = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
                pending = pending_new
                for t in done:
                    if t is act_task:
                        try:
                            chunk = t.result()
                            if first_token:
                                first_token = False
                                hb_task.cancel()
                                try:
                                    await hb_task
                                except (asyncio.CancelledError, StopAsyncIteration):
                                    pass
                            full_text += chunk

                            if not code_started:
                                code_idx = _find_code_start(full_text)
                                if code_idx != -1:
                                    code_started = True
                                    text_part = full_text[:code_idx].strip()
                                    text_part = re.sub(r'```.*?$', '', text_part, flags=re.DOTALL).strip()
                                    if text_part:
                                        words = text_part.split(" ")
                                        for i, w in enumerate(words):
                                            yield {
                                                "event": "agent_stream",
                                                "data": {"agent": engineer.name, "emoji": engineer.avatar_emoji, "chunk": w + (" " if i < len(words) - 1 else "")},
                                            }
                                            await asyncio.sleep(0.04)
                                    yield {
                                        "event": "agent_action",
                                         "data": {"agent": engineer.name, "emoji": engineer.avatar_emoji, "action": "正在编写代码..."},
                                    }
                            act_task = asyncio.create_task(gen.__anext__())
                            pending.add(act_task)
                        except StopAsyncIteration:
                            pass
                        except Exception as e:
                            logger.error(f"Engineer stream error: {e}")
                    elif t is hb_task:
                        try:
                            ev = t.result()
                            if not code_started:
                                yield ev
                            hb_task = asyncio.create_task(hb.__anext__())
                            pending.add(hb_task)
                        except (StopAsyncIteration, asyncio.CancelledError):
                            pass
        finally:
            act_task.cancel()
            hb_task.cancel()
            for t in {act_task, hb_task}:
                try:
                    await t
                except (asyncio.CancelledError, StopAsyncIteration, Exception):
                    pass

        code = _extract_html(full_text)
        if not code_started:
            text_only = re.sub(r'```.*?```', '', full_text, flags=re.DOTALL).strip()
            if text_only:
                words = text_only.split(" ")
                for i, w in enumerate(words):
                    yield {
                        "event": "agent_stream",
                        "data": {"agent": engineer.name, "emoji": engineer.avatar_emoji, "chunk": w + (" " if i < len(words) - 1 else "")},
                    }
                    await asyncio.sleep(0.04)

        duration = int((time.time() - start) * 1000)

        yield {
            "event": "code_generated",
            "data": {"agent": engineer.name, "code": code, "duration_ms": duration},
        }

        yield {
            "event": "message_complete",
            "data": {
                "agent": engineer.name,
                "message": "应用已生成！您可以在右侧预览，或告诉我需要修改什么——我可以调整设计、布局、颜色或添加新功能。",
                "duration_ms": duration,
            },
        }

    async def _run_plan_step(
        self,
        step: dict[str, Any],
        step_num: int,
        total_steps: int,
        task: str,
        context: dict[str, Any],
    ) -> AsyncIterator[dict[str, Any]]:
        raw_agent = step.get("agent", "engineer")
        agent_key = self._resolve_agent_key(raw_agent)
        step_task = step.get("task", task)
        agent = self.agents[agent_key]

        yield {
            "event": "agent_thinking",
            "data": {
                "agent": agent.name,
                "emoji": agent.avatar_emoji,
                "message": f"步骤 {step_num}/{total_steps}: {agent.avatar_emoji} {agent.name} — {step_task[:80]}",
            },
        }

        if agent_key == "engineer":
            engineer_task = f"ORIGINAL USER REQUEST: {task}\n\nYOUR ASSIGNMENT: {step_task}"
            full_text = ""
            code_started = False
            async for ev in _stream_llm_as_events(agent, "act_stream", engineer_task, context, f"{agent.avatar_emoji} {agent.name} 正在生成代码..."):
                if ev["event"] == "agent_stream":
                    full_text += ev["data"].get("chunk", "")
                    if not code_started:
                        lower = full_text.lower()
                        for marker in ["<!doctype", "<html", "```html"]:
                            if marker in lower:
                                code_started = True
                                yield {
                                    "event": "agent_action",
                                    "data": {"agent": agent.name, "emoji": agent.avatar_emoji, "action": "正在编写代码..."},
                                }
                                break
                    yield ev
                elif ev["event"] == "agent_stream_done":
                    full_text = ev["data"]["full_text"]

            code = _extract_html(full_text)
            if code:
                yield {
                    "event": "code_generated",
                    "data": {"agent": agent.name, "code": code},
                }
                context["previous_code"] = code
            else:
                yield {
                    "event": "agent_action",
                    "data": {"agent": agent.name, "emoji": agent.avatar_emoji, "action": "代码生成完成但未提取到有效HTML"},
                }
        else:
            full_text = ""
            async for ev in _stream_llm_as_events(agent, "think_stream", step_task, context):
                if ev["event"] == "agent_stream":
                    full_text += ev["data"].get("chunk", "")
                    yield ev
                elif ev["event"] == "agent_stream_done":
                    full_text = ev["data"]["full_text"]

            output_data = full_text
            parsed_output = _try_parse_json(full_text)
            if parsed_output:
                output_data = json.dumps(parsed_output, ensure_ascii=False)

            if agent_key == "pm":
                context["prd"] = output_data
                try:
                    prd_obj = json.loads(output_data)
                    features = prd_obj.get("prd", {}).get("features", [])
                    feat_names = ", ".join(f.get("name", "") for f in features[:3]) if features else ""
                except:
                    feat_names = ""
                yield {
                    "event": "agent_action",
                    "data": {
                        "agent": agent.name,
                        "emoji": agent.avatar_emoji,
                        "action": f"PRD 已创建 — {feat_names}" if feat_names else "PRD 已创建",
                        "prd": parsed_output,
                    },
                }
            elif agent_key == "architect":
                context["architecture"] = output_data
                yield {
                    "event": "agent_action",
                    "data": {
                        "agent": agent.name,
                        "emoji": agent.avatar_emoji,
                        "action": "架构设计完成",
                        "architecture": parsed_output,
                    },
                }
            elif agent_key == "researcher":
                context["research"] = output_data
                yield {
                    "event": "agent_action",
                    "data": {
                        "agent": agent.name,
                        "emoji": agent.avatar_emoji,
                        "action": "研究完成",
                    },
                }
            else:
                yield {
                    "event": "agent_action",
                    "data": {"agent": agent.name, "emoji": agent.avatar_emoji, "action": step_task[:100]},
                }

        if agent_key == "engineer" or step_num == total_steps:
            pass

    async def run_team_mode(self, task: str, context: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        leader = self.agents["leader"]
        enriched_context = dict(context)
        enriched_context["mode"] = "team"
        total_start = time.time()

        yield {
            "event": "agent_thinking",
            "data": {"agent": leader.name, "emoji": leader.avatar_emoji, "message": f"{leader.avatar_emoji} {leader.name} 正在协调团队..."},
        }

        leader_text = ""
        async for ev in _stream_llm_as_events(leader, "think_stream", task, enriched_context):
            if ev["event"] == "agent_stream":
                leader_text = ev["data"]["chunk"] if not leader_text else leader_text
                yield ev
            elif ev["event"] == "agent_stream_done":
                leader_text = ev["data"]["full_text"]

        plan_data = _try_parse_json(leader_text)
        if not plan_data:
            plan_data = {"plan": leader_text[:200], "steps": [], "summary": "Executing full team pipeline"}

        plan_summary = plan_data.get("plan", leader_text[:200])
        steps = plan_data.get("steps", [])

        for step in steps:
            raw = step.get("agent", "engineer")
            step["agent"] = self._resolve_agent_key(raw)

        if not steps:
            steps = [
                {"agent": "pm", "task": f"Analyze requirements for: {task}"},
                {"agent": "architect", "task": f"Design architecture for: {task}"},
                {"agent": "engineer", "task": f"Implement: {task}"},
            ]

        yield {
            "event": "agent_action",
            "data": {
                "agent": leader.name,
                "emoji": leader.avatar_emoji,
                "action": f"团队计划: {plan_summary}",
                "plan": plan_data,
                "steps": steps,
            },
        }

        await _mock_delay()

        for i, step in enumerate(steps):
            async for ev in self._run_plan_step(step, i + 1, len(steps), task, enriched_context):
                yield ev

        total_duration = int((time.time() - total_start) * 1000)

        yield {
            "event": "message_complete",
            "data": {
                "agent": leader.name,
                "message": f"团队协作完成！执行了 {len(steps)} 个步骤。在右侧预览结果，或告诉我需要调整什么。",
                "duration_ms": total_duration,
                "agents_used": list(dict.fromkeys([leader.name] + [self.agents.get(s.get('agent', ''), self.agents['engineer']).name for s in steps])),
            },
        }

    async def run_race_mode(self, task: str, context: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        engineer = self.agents["engineer"]

        yield {
            "event": "agent_thinking",
            "data": {"agent": "Race Mode", "emoji": "⚡", "message": "⚡ 竞速模式：启动两个并行实现策略..."},
        }

        start = time.time()

        code_a = ""
        yield {
            "event": "agent_thinking",
            "data": {"agent": engineer.name, "emoji": engineer.avatar_emoji, "message": f"策略A: {engineer.avatar_emoji} {engineer.name} 正在构建..."},
        }
        async for ev in _collect_code_with_heartbeat(engineer, task, context):
            if ev["event"] == "code_collected":
                code_a = ev["data"]["code"]
            else:
                yield ev

        code_a = _extract_html(code_a)

        context_b = {**context}
        if code_a:
            context_b["previous_code"] = code_a
            context_b["is_iteration"] = True
        code_b = ""
        yield {
            "event": "agent_thinking",
            "data": {"agent": engineer.name, "emoji": engineer.avatar_emoji, "message": f"策略B: {engineer.avatar_emoji} {engineer.name} 正在构建替代方案..."},
        }
        async for ev in _collect_code_with_heartbeat(engineer, f"Alternative creative approach: {task}", context_b):
            if ev["event"] == "code_collected":
                code_b = ev["data"]["code"]
            else:
                yield ev

        code_b = _extract_html(code_b)
        duration = int((time.time() - start) * 1000)

        yield {
            "event": "code_generated",
            "data": {"agent": engineer.name, "code": code_a, "variant": "A", "duration_ms": duration},
        }
        yield {
            "event": "code_generated",
            "data": {"agent": engineer.name, "code": code_b, "variant": "B", "duration_ms": duration},
        }

        yield {
            "event": "message_complete",
            "data": {
                "agent": "Race Mode",
                "message": f"竞速完成！两个变体已生成，耗时 {duration}ms。预览两个版本并告诉我你更喜欢哪个方向。",
                "duration_ms": duration,
                "variants": ["A", "B"],
            },
        }

    async def run_research_mode(self, task: str, context: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        researcher = self.agents["researcher"]
        start = time.time()

        yield {
            "event": "agent_thinking",
            "data": {"agent": researcher.name, "emoji": researcher.avatar_emoji, "message": f"{researcher.avatar_emoji} {researcher.name} 正在进行深度研究..."},
        }

        research_text = ""
        async for ev in _stream_llm_as_events(researcher, "think_stream", task, context):
            if ev["event"] == "agent_stream":
                yield ev
            elif ev["event"] == "agent_stream_done":
                research_text = ev["data"]["full_text"]

        duration = int((time.time() - start) * 1000)

        yield {
            "event": "message_complete",
            "data": {
                "agent": researcher.name,
                "message": "研究完成！您可以继续提问，或切换到工程师/团队模式开始构建。",
                "duration_ms": duration,
            },
        }

    async def run_review_mode(self, task: str, context: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        researcher = self.agents["researcher"]
        engineer = self.agents["engineer"]
        start = time.time()

        previous_code = context.get("previous_code", "")
        review_task = f"Review this code and suggest improvements:\n\n{previous_code}\n\nUser request: {task}" if previous_code else task

        yield {
            "event": "agent_thinking",
            "data": {"agent": researcher.name, "emoji": researcher.avatar_emoji, "message": f"{researcher.avatar_emoji} {researcher.name} 正在审查代码..."},
        }

        thought = ""
        async for ev in _stream_llm_as_events(researcher, "think_stream", review_task, context):
            if ev["event"] == "agent_stream":
                yield ev
            elif ev["event"] == "agent_stream_done":
                thought = ev["data"]["full_text"]

        yield {
            "event": "agent_action",
            "data": {"agent": researcher.name, "emoji": researcher.avatar_emoji, "action": "审查完成，正在应用改进..."},
        }

        await _mock_delay()

        yield {
            "event": "agent_thinking",
            "data": {"agent": engineer.name, "emoji": engineer.avatar_emoji, "message": f"{engineer.avatar_emoji} {engineer.name} 正在应用审查反馈..."},
        }

        act_context = {**context, "thought": thought, "is_iteration": True}
        code = ""
        async for ev in _collect_code_with_heartbeat(engineer, task, act_context):
            if ev["event"] == "code_collected":
                code = ev["data"]["code"]
            else:
                yield ev

        code = _extract_html(code)
        duration = int((time.time() - start) * 1000)

        yield {
            "event": "code_generated",
            "data": {"agent": engineer.name, "code": code, "duration_ms": duration},
        }

        yield {
            "event": "message_complete",
            "data": {
                "agent": researcher.name,
                "message": "审查完成！我已分析代码并应用了改进。查看预览或继续优化。",
                "duration_ms": duration,
                "agents_used": [researcher.name, engineer.name],
            },
        }

    async def run(self, task: str, mode: str, context: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        if mode == "engineer":
            async for event in self.run_engineer_mode(task, context):
                yield event
        elif mode == "race":
            async for event in self.run_race_mode(task, context):
                yield event
        elif mode == "review":
            async for event in self.run_review_mode(task, context):
                yield event
        elif mode == "research":
            async for event in self.run_research_mode(task, context):
                yield event
        else:
            async for event in self.run_team_mode(task, context):
                yield event
