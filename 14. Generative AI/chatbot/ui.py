
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

load_dotenv()

model = ChatGroq(model="openai/gpt-oss-120b")

st.title("AuraBot")
st.caption("Choose your chat personality")

choice = st.selectbox(
    "Choose your chat mode:",
    ["Funny", "Sad", "Angry", "Sarcastic"]
)

if choice == "Funny":
    mode = "You are a funny AI agent who responds in a funny way in every interaction"
elif choice == "Sad":
    mode = "You are a sad AI agent who responds logicless depressing words in every interaction like you have lost everything"
elif choice == "Angry":
    mode = "You are a angry AI agent who responds aggressively and impatiently"
elif choice == "Sarcastic":
    mode = "You are a sarcastic AI agent who taunts in every chat"

if "messages" not in st.session_state:
    st.session_state.messages = [SystemMessage(content=mode)]

if "current_mode" not in st.session_state:
    st.session_state.current_mode = choice

if st.session_state.current_mode != choice:
    st.session_state.messages = [SystemMessage(content=mode)]
    st.session_state.current_mode = choice

for message in st.session_state.messages[1:]:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(message.content)

prompt = st.chat_input("Type your message...")

if prompt:
    if prompt == "0":
        st.stop()

    st.session_state.messages.append(HumanMessage(content=prompt))

    with st.chat_message("user"):
        st.write(prompt)

    response = model.invoke(st.session_state.messages)
    st.session_state.messages.append(AIMessage(content=response.content))

    with st.chat_message("assistant"):
        st.write(response.content)
