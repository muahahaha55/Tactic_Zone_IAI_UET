import streamlit as st
import time
from graph import Workflow
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from typing import Dict
import asyncio
import threading
from init import get_initial_graph_state, system_init, setup_scheduled_updates

st.set_page_config(
    page_title="Tactic Zone IAI-UET",
    page_icon="🎯",
    layout="wide"
)

st.markdown("""
    <style>
    .stAppDeployButton {
        display: none !important;
    }
    #MainMenu {
        visibility: hidden;
    }
    footer {
        visibility: hidden;
    }
    .main-header {
        color: #1E88E5;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .sub-header {
        color: #424242;
        font-family: 'Helvetica Neue', sans-serif;
    }
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        border-radius: 10px;
        padding: 10px 25px;
        font-weight: bold;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    .chat-message {
        padding: 15px;
        border-radius: 10px;
        margin: 5px 0;
    }
    </style>
""", unsafe_allow_html=True)

async def process_query(workflow: Workflow, initial_state: dict, result_container: dict):
    await Workflow.fetch_response(workflow, initial_state, result_container)

def run_async_task_in_thread(workflow, initial_state, result_container):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_query(workflow, initial_state, result_container))

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("<h1 class='main-header'>🎯 Tactic Zone IAI-UET</h1>", unsafe_allow_html=True)
    st.markdown("<h3 class='sub-header'>Your AI-Powered Tactical Analysis Partner</h3>", unsafe_allow_html=True)

    st.markdown("---")

    with st.container():
        st.info("💡 Tell me about the match and I'll help you with tactical insights.")

if "workflow" not in st.session_state:
    load_dotenv()
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    st.session_state.workflow = Workflow(llm)
    st.session_state.LLM = llm

if "is_initialized" not in st.session_state:
    system_init(st.session_state.LLM)
    setup_scheduled_updates(**st.session_state)
    st.session_state.is_initialized = True

if st.button("Close!"):
    st.write("Closing...")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type your question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    initial_state = get_initial_graph_state()
    initial_state["user_query"] = prompt

    with st.chat_message("ai", avatar="🤖"):
        message_placeholder = st.empty()

        result_container = {"response": None, "done": False}
        thread = threading.Thread(target=run_async_task_in_thread,
                                  args=(st.session_state.workflow, initial_state, result_container))
        thread.start()

        thinking_dots = [".", "..", "..."]
        dot_index = 0

        while not result_container["done"]:
            message_placeholder.markdown(f"*Thinking{thinking_dots[dot_index]}*")
            dot_index = (dot_index + 1) % len(thinking_dots)
            time.sleep(0.3)

        response = result_container["response"]

        if st.session_state.get("enable_typing_effect", True):
            paragraphs = response.split('\n')
            current_text = ""

            for i, paragraph in enumerate(paragraphs):
                if i > 0:
                    current_text += '\n'
                current_text += paragraph

                message_placeholder.markdown(current_text)
                time.sleep(0.1)

            message_placeholder.markdown(response)
        else:
            message_placeholder.markdown(response)

    st.session_state.messages.append({"role": "ai", "content": response})