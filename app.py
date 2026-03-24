"""
AI 创业团队 - 多智能体协作平台
基于 Claude Opus 4.6 驱动的 7 人精英团队
"""
import streamlit as st
from agents import AGENTS, run_ceo_agent

st.set_page_config(
    page_title="AI 创业团队",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 全局样式 ──────────────────────────────────────────────
st.markdown("""
<style>
/* 全局字体 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif; }

/* 背景 */
.stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); }
.stApp > header { background: transparent; }

/* 侧边栏 */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.1);
}
[data-testid="stSidebar"] * { color: white !important; }

/* 主内容 */
.main .block-container { padding: 1.5rem 2rem; max-width: 1200px; }

/* 聊天消息 */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
    margin: 0.5rem 0 !important;
    backdrop-filter: blur(10px) !important;
}
[data-testid="stChatMessage"] * { color: #e8e8f0 !important; }

/* 输入框 */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(139,92,246,0.5) !important;
    border-radius: 12px !important;
    color: white !important;
}
[data-testid="stChatInput"] textarea { color: white !important; }

/* Agent 卡片 */
.agent-card {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    padding: 0.85rem 1rem;
    margin: 0.4rem 0;
    transition: all 0.3s ease;
    cursor: default;
}
.agent-card:hover {
    background: rgba(255,255,255,0.1);
    border-color: rgba(139,92,246,0.5);
    transform: translateX(4px);
}
.agent-card-active {
    background: rgba(139,92,246,0.2) !important;
    border-color: #8b5cf6 !important;
    box-shadow: 0 0 20px rgba(139,92,246,0.3);
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 20px rgba(139,92,246,0.3); }
    50% { box-shadow: 0 0 35px rgba(139,92,246,0.6); }
}
.agent-name { font-weight: 600; font-size: 0.9rem; color: white; }
.agent-role { font-size: 0.75rem; color: rgba(255,255,255,0.6); margin-top: 2px; }

/* 工具调用气泡 */
.tool-call-bubble {
    background: linear-gradient(135deg, rgba(139,92,246,0.15), rgba(59,130,246,0.15));
    border: 1px solid rgba(139,92,246,0.4);
    border-radius: 12px;
    padding: 0.75rem 1rem;
    margin: 0.3rem 0;
    font-size: 0.88rem;
}
.tool-result-bubble {
    background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(5,150,105,0.1));
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 12px;
    padding: 0.75rem 1rem;
    margin: 0.3rem 0;
    font-size: 0.88rem;
}

/* 标题 */
.page-title {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.25rem;
}
.page-subtitle {
    color: rgba(255,255,255,0.5);
    font-size: 0.9rem;
    margin-bottom: 1.5rem;
}

/* CEO 标识 */
.ceo-badge {
    background: linear-gradient(135deg, #f59e0b, #ef4444);
    border-radius: 20px;
    padding: 0.3rem 0.8rem;
    font-size: 0.75rem;
    font-weight: 700;
    color: white;
    display: inline-block;
    margin-bottom: 0.5rem;
}

/* 示例按钮 */
.stButton > button {
    background: rgba(139,92,246,0.2) !important;
    border: 1px solid rgba(139,92,246,0.4) !important;
    border-radius: 10px !important;
    color: white !important;
    font-size: 0.8rem !important;
    padding: 0.4rem 0.8rem !important;
    text-align: left !important;
    width: 100% !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(139,92,246,0.35) !important;
    border-color: #8b5cf6 !important;
    transform: translateY(-1px) !important;
}

/* 分割线 */
hr { border-color: rgba(255,255,255,0.1) !important; }

/* 滚动条 */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.4); border-radius: 3px; }

/* 白色文字覆盖 */
h1,h2,h3,h4,h5,h6,p,span,div,label { color: rgba(255,255,255,0.9); }
.stMarkdown p { color: rgba(255,255,255,0.85) !important; }
</style>
""", unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_history" not in st.session_state:
    st.session_state.api_history = []
if "active_agents" not in st.session_state:
    st.session_state.active_agents = set()

# ── 侧边栏 ────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="ceo-badge">👑 CEO 驱动</div>', unsafe_allow_html=True)
    st.markdown("### 🏢 AI 创业团队")
    st.markdown('<p style="color:rgba(255,255,255,0.5);font-size:0.8rem;">Claude Opus 4.6 驱动</p>', unsafe_allow_html=True)
    st.markdown("---")

    # CEO
    st.markdown('<div class="agent-card"><div class="agent-name">👑 CEO</div><div class="agent-role">总指挥 · 战略决策</div></div>', unsafe_allow_html=True)
    st.markdown("**团队成员**")

    for key, agent in AGENTS.items():
        is_active = key in st.session_state.active_agents
        card_class = "agent-card agent-card-active" if is_active else "agent-card"
        status_dot = "🟢" if is_active else "⚪"
        st.markdown(
            f'<div class="{card_class}">'
            f'<div class="agent-name">{agent.emoji} {agent.name} {status_dot}</div>'
            f'<div class="agent-role">{agent.role}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("**💡 快速指令**")
    examples = [
        "帮我启动一个线上知识付费项目",
        "分析当前短视频电商的市场机会",
        "制定一套从0到1的私域流量体系",
        "设计一个SaaS产品的冷启动方案",
    ]
    for example in examples:
        if st.button(f"→ {example}", key=f"btn_{example[:8]}"):
            st.session_state.pending_input = example
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ 清空对话", use_container_width=True):
        st.session_state.messages = []
        st.session_state.api_history = []
        st.session_state.active_agents = set()
        st.rerun()

# ── 主界面 ────────────────────────────────────────────────
col1, col2 = st.columns([6, 1])
with col1:
    st.markdown('<div class="page-title">🏢 AI 创业团队</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">7 位顶级专家 · CEO 统一调度 · 全栈互联网项目支持</div>', unsafe_allow_html=True)

# 显示历史消息
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]

    if role == "user":
        with st.chat_message("user", avatar="🧑‍💼"):
            st.markdown(content)
    elif role == "ceo":
        with st.chat_message("assistant", avatar="👑"):
            st.markdown(content)
    elif role == "tool_call":
        with st.chat_message("assistant", avatar=msg.get("emoji", "🤖")):
            st.markdown(
                f'<div class="tool-call-bubble">⚡ <b>{msg["agent_name"]}</b> 正在处理：{msg["task"]}</div>',
                unsafe_allow_html=True
            )
    elif role == "tool_result":
        with st.chat_message("assistant", avatar=msg.get("emoji", "🤖")):
            st.markdown(
                f'<div class="tool-result-bubble">✅ <b>{msg["agent_name"]}</b> 完成任务</div>',
                unsafe_allow_html=True
            )
            st.markdown(msg["result"])

# 处理待发送的示例输入
pending = st.session_state.pop("pending_input", None)

# 用户输入
user_input = st.chat_input("告诉 CEO 你的业务目标或问题...")

if pending:
    user_input = pending

if user_input:
    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(user_input)

    # 流式处理 CEO 回复
    ceo_text = ""
    ceo_placeholder = None

    with st.chat_message("assistant", avatar="👑"):
        for event in run_ceo_agent(user_input, st.session_state.api_history):
            etype = event["type"]

            if etype == "text_start":
                ceo_placeholder = st.empty()

            elif etype == "text":
                ceo_text += event["content"]
                if ceo_placeholder:
                    ceo_placeholder.markdown(ceo_text + "▌")

            elif etype == "tool_call":
                # 先保存当前 CEO 文本
                if ceo_text and ceo_placeholder:
                    ceo_placeholder.markdown(ceo_text)
                    st.session_state.messages.append({"role": "ceo", "content": ceo_text})
                    ceo_text = ""
                    ceo_placeholder = None

                # 激活 Agent
                st.session_state.active_agents.add(event["agent_key"])
                st.session_state.messages.append({
                    "role": "tool_call",
                    "agent_key": event["agent_key"],
                    "agent_name": event["agent_name"],
                    "emoji": event["emoji"],
                    "task": event["task"],
                })
                st.markdown(
                    f'<div class="tool-call-bubble">⚡ <b>{event["agent_name"]}</b> 正在处理：{event["task"]}</div>',
                    unsafe_allow_html=True
                )

            elif etype == "tool_result":
                st.session_state.active_agents.discard(event["agent_key"])
                st.session_state.messages.append({
                    "role": "tool_result",
                    "agent_key": event["agent_key"],
                    "agent_name": event["agent_name"],
                    "emoji": event["emoji"],
                    "result": event["result"],
                })
                st.markdown(
                    f'<div class="tool-result-bubble">✅ <b>{event["agent_name"]}</b> 完成任务</div>',
                    unsafe_allow_html=True
                )
                st.markdown(event["result"])

            elif etype == "done":
                if ceo_text and ceo_placeholder:
                    ceo_placeholder.markdown(ceo_text)
                    st.session_state.messages.append({"role": "ceo", "content": ceo_text})
                st.session_state.active_agents.clear()

    # 更新 API 历史（保留最近 20 轮）
    st.session_state.api_history.append({"role": "user", "content": user_input})
    # 只保留最近20条消息避免超出上下文
    if len(st.session_state.api_history) > 40:
        st.session_state.api_history = st.session_state.api_history[-40:]

    st.rerun()
