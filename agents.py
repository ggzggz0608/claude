"""
AI 团队多智能体系统 - 核心 Agent 定义与编排
"""
import os
import json
from dataclasses import dataclass
from typing import Generator
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-opus-4-6"
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


@dataclass
class AgentConfig:
    name: str
    role: str
    emoji: str
    color: str
    system_prompt: str
    tool_name: str
    tool_description: str


AGENTS: dict[str, AgentConfig] = {
    "data_expert": AgentConfig(
        name="数据专家",
        role="市场调研 & 数据分析",
        emoji="📊",
        color="#4CAF50",
        tool_name="call_data_expert",
        tool_description="调用数据专家进行市场调研、竞品分析、用户画像分析、行业趋势研究、数据报告撰写",
        system_prompt="""你是一位顶级数据分析专家，拥有10年市场调研经验。
你的核心职责：
- 深度市场调研与竞品分析
- 用户画像与需求洞察
- 行业趋势预测与数据报告
- 关键指标定义与监测体系

输出标准：数据驱动、逻辑严谨、图文并茂（用表格/列表呈现数据）
语言风格：专业、客观、有说服力

请用中文回答，结构清晰，重点突出。""",
    ),
    "project_manager": AgentConfig(
        name="项目操盘手",
        role="互联网项目策划 & 执行",
        emoji="🎯",
        color="#2196F3",
        tool_name="call_project_manager",
        tool_description="调用项目操盘手进行项目规划、商业模式设计、执行方案制定、资源调配、风险管控",
        system_prompt="""你是一位经验丰富的互联网项目操盘手，曾主导过多个年营收千万的项目。
你的核心职责：
- 商业模式设计与验证
- 项目全流程规划（时间线、里程碑）
- 执行方案与SOP制定
- 资源调配与团队协作
- 风险识别与应对策略

输出标准：落地可执行、有具体时间节点、分工明确
语言风格：务实、高效、行动导向

请用中文回答，给出具体可执行的方案。""",
    ),
    "content_creator": AgentConfig(
        name="内容创作者",
        role="内容策划 & 创作",
        emoji="✍️",
        color="#9C27B0",
        tool_name="call_content_creator",
        tool_description="调用内容创作者进行文案撰写、内容策划、爆款标题创作、品牌故事、短视频脚本",
        system_prompt="""你是一位顶流内容创作者，精通各平台内容生态，擅长打造爆款内容。
你的核心职责：
- 爆款内容策划与创作
- 各平台内容差异化运营（小红书/抖音/微信/B站）
- 品牌故事与价值主张提炼
- 短视频脚本与文案创作
- 内容日历规划

输出标准：接地气、有传播性、符合平台调性
语言风格：生动、有感染力、能引发共鸣

请用中文回答，创作有爆款潜力的内容。""",
    ),
    "seo_ads_expert": AgentConfig(
        name="广告投放 & SEO 专家",
        role="流量获取 & 搜索优化",
        emoji="🚀",
        color="#FF5722",
        tool_name="call_seo_ads_expert",
        tool_description="调用广告投放和SEO专家进行搜索引擎优化、付费广告投放策略、关键词规划、流量增长方案",
        system_prompt="""你是一位精通全域流量的广告投放与SEO专家，ROI思维极强。
你的核心职责：
- SEO关键词策略与内容优化
- 百度/Google广告投放方案
- 信息流广告创意与优化
- 私域流量搭建与运营
- 投放数据分析与优化迭代

输出标准：数据化、ROI导向、有具体操作步骤
语言风格：精准、高效、注重转化

请用中文回答，提供可量化的流量增长方案。""",
    ),
    "social_media_manager": AgentConfig(
        name="社交媒体运营",
        role="账号运营 & 社群管理",
        emoji="📱",
        color="#00BCD4",
        tool_name="call_social_media_manager",
        tool_description="调用社交媒体运营专家进行账号矩阵规划、社群运营、粉丝增长、互动策略、品牌声量管理",
        system_prompt="""你是一位资深社交媒体运营专家，管理过百万粉丝账号矩阵。
你的核心职责：
- 多平台账号矩阵规划与运营
- 粉丝增长策略（自然增长+活动引流）
- 社群运营与用户激活
- 互动策略与口碑管理
- 品牌声量监测与危机处理

输出标准：有数据支撑、操作性强、有创意
语言风格：亲和、有趣、懂用户心理

请用中文回答，给出实用的运营策略。""",
    ),
    "sales_expert": AgentConfig(
        name="销售高手",
        role="销售策略 & 成交转化",
        emoji="💰",
        color="#FF9800",
        tool_name="call_sales_expert",
        tool_description="调用销售高手进行销售策略制定、成交话术设计、客户转化漏斗优化、价格策略、销售团队培训",
        system_prompt="""你是一位顶级销售专家，年成交额过千万，精通各类销售方法论。
你的核心职责：
- 销售策略与打法设计
- 客户转化漏斗优化
- 成交话术与异议处理
- 价格策略与促销方案
- 销售团队培训与激励

输出标准：有具体话术、可复制、转化率导向
语言风格：自信、有说服力、以客户为中心

请用中文回答，提供高转化率的销售方案。""",
    ),
    "translator": AgentConfig(
        name="翻译员",
        role="多语言翻译 & 本地化",
        emoji="🌐",
        color="#00BCD4",
        tool_name="call_translator",
        tool_description="调用翻译员进行多语言翻译、内容本地化、跨文化沟通、国际化策略、多语言文案撰写",
        system_prompt="""你是一位精通10国语言的资深翻译专家，擅长商业文案翻译与跨文化沟通。
你的核心职责：
- 高质量多语言翻译（中/英/日/韩/西/法/德/阿拉伯语等）
- 内容本地化与文化适配
- 品牌名称与口号的跨语言创作
- 国际化营销文案撰写
- 跨文化商业沟通建议

输出标准：信达雅、文化敏感度高、保留原文语气与风格
语言风格：精准、流畅、专业

请提供高质量的翻译与本地化建议，并说明关键的文化差异点。""",
    ),
}

CEO_SYSTEM_PROMPT = """你是一位卓越的 CEO（首席执行官），统领一支由6位顶级专家组成的互联网项目团队。

你的团队成员：
- 📊 数据专家（data_expert）：市场调研、数据分析、竞品研究
- 🎯 项目操盘手（project_manager）：项目策划、执行方案、资源调配
- ✍️ 内容创作者（content_creator）：文案创作、内容策划、爆款内容
- 🚀 广告投放&SEO专家（seo_ads_expert）：流量获取、搜索优化、广告投放
- 📱 社交媒体运营（social_media_manager）：账号运营、社群管理、粉丝增长
- 💰 销售高手（sales_expert）：销售策略、成交转化、客户维护

你的职责：
1. 理解用户的业务需求和目标
2. 判断需要调用哪些专家
3. 协调多个专家协同工作
4. 整合各方建议，给出综合执行方案
5. 把控整体方向，确保团队高效执行

工作原则：
- 复杂任务要多专家协同，不能只靠一人
- 给出清晰的任务优先级
- 最终输出要有整体战略视角
- 语言简洁有力，决策果断

请用中文与用户沟通，展现 CEO 的格局与执行力。"""

CEO_TOOLS = [
    {
        "name": cfg.tool_name,
        "description": cfg.tool_description,
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "需要该专家完成的具体任务描述"
                },
                "context": {
                    "type": "string",
                    "description": "相关背景信息和上下文"
                }
            },
            "required": ["task"]
        }
    }
    for cfg in AGENTS.values()
]

TOOL_TO_AGENT = {cfg.tool_name: key for key, cfg in AGENTS.items()}


def call_specialist(agent_key: str, task: str, context: str = "") -> str:
    """调用专家 Agent 完成指定任务"""
    agent = AGENTS[agent_key]
    messages = [{"role": "user", "content": f"任务：{task}\n\n背景：{context}" if context else f"任务：{task}"}]

    response = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        system=agent.system_prompt,
        messages=messages,
    )
    return response.content[0].text


def run_ceo_agent(user_input: str, history: list) -> Generator[dict, None, None]:
    """
    运行 CEO Agent，流式返回事件。
    事件格式: {"type": "text"|"tool_call"|"tool_result"|"done", ...}
    """
    messages = history + [{"role": "user", "content": user_input}]

    while True:
        with client.messages.stream(
            model=MODEL,
            max_tokens=4096,
            system=CEO_SYSTEM_PROMPT,
            tools=CEO_TOOLS,
            messages=messages,
        ) as stream:
            full_text = ""
            tool_uses = []

            for event in stream:
                if event.type == "content_block_start":
                    if event.content_block.type == "text":
                        yield {"type": "text_start"}
                    elif event.content_block.type == "tool_use":
                        tool_uses.append({
                            "id": event.content_block.id,
                            "name": event.content_block.name,
                            "input_raw": ""
                        })

                elif event.type == "content_block_delta":
                    if event.delta.type == "text_delta":
                        full_text += event.delta.text
                        yield {"type": "text", "content": event.delta.text}
                    elif event.delta.type == "input_json_delta":
                        if tool_uses:
                            tool_uses[-1]["input_raw"] += event.delta.partial_json

            final_message = stream.get_final_message()

        messages.append({"role": "assistant", "content": final_message.content})

        if final_message.stop_reason != "tool_use":
            yield {"type": "done"}
            break

        # 处理工具调用
        tool_results = []
        for block in final_message.content:
            if block.type == "tool_use":
                agent_key = TOOL_TO_AGENT.get(block.name)
                if not agent_key:
                    continue

                agent = AGENTS[agent_key]
                tool_input = block.input if isinstance(block.input, dict) else {}
                task = tool_input.get("task", "")
                context = tool_input.get("context", "")

                yield {
                    "type": "tool_call",
                    "agent_key": agent_key,
                    "agent_name": agent.name,
                    "emoji": agent.emoji,
                    "task": task,
                }

                result = call_specialist(agent_key, task, context)

                yield {
                    "type": "tool_result",
                    "agent_key": agent_key,
                    "agent_name": agent.name,
                    "emoji": agent.emoji,
                    "result": result,
                }

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        messages.append({"role": "user", "content": tool_results})
