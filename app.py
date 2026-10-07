import streamlit as st
from langchain.messages import HumanMessage

from agent import agent
from tools import WORK_DIR


st.set_page_config(
    page_title="Coding Companion",
    page_icon="💻",
)

st.title("💻 Coding Companion")
st.caption(f"Working folder: {WORK_DIR}")

# Full agent history, including tool calls and results
if "agent_messages" not in st.session_state:
    st.session_state.agent_messages = []

# Only user questions and final answers for display
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if st.sidebar.button("Clear chat"):
    st.session_state.agent_messages = []
    st.session_state.chat_messages = []
    st.rerun()

st.sidebar.caption("Clearing chat does not delete project files.")

for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask me to create, edit or debug code...")

if question:
    st.session_state.chat_messages.append({
        "role": "user",
        "content": question,
    })

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Working..."):
                result = agent.invoke(
                    {
                        "messages": (
                            st.session_state.agent_messages
                            + [HumanMessage(question)]
                        )
                    },
                    config={"recursion_limit": 30},
                )

            st.session_state.agent_messages = result["messages"]
            answer = result["messages"][-1].text

            st.markdown(answer)

            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": answer,
            })

        except Exception as error:
            st.error(f"Request failed: {type(error).__name__}")
            st.warning(
                "Some file operations may already have happened. "
                "Inspect the files before repeating the request."
            )