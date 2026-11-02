import os
from typing import TypedDict
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

# Lets create the state first
class pipelinestate(TypedDict):
    raw_input: str
    edited_text: str
    script_text: str
    final_output: str


load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.7)

def editor_node(state: pipelinestate) -> dict:
    """Stage 1: Edits grammar, removes typos and refines tone."""

    prompt = f"""
    You are a professional editor.
    Clean up grammar, remove typos, and refine the tone.

    Original Text:
    {state['raw_input']}
    """

    edited_text = llm.invoke(prompt).content

    return {"edited_text": edited_text}


def script_node(state: pipelinestate) -> dict:
    """Stage 2: Converts edited text into a YouTube script."""

    prompt = f"""
    You are a professional YouTube content creator.
    Convert the following text into an engaging YouTube video script.

    Edited Text:
    {state['edited_text']}
    """

    script_text = llm.invoke(prompt).content

    return {"script_text": script_text}


def translation_node(state: pipelinestate) -> dict:
    """Stage 3: Translates the script into Hinglish."""

    prompt = f"""
    You are a professional translator.
    Translate the following script into natural Hinglish.

    Keep the headings, bullet points, and formatting clean.

    Script Text:
    {state['script_text']}
    """

    final_output = llm.invoke(prompt).content

    return {"final_output": final_output}


# Now your state and nodes are ready, now it is time to create the graph and run the pipeline

# create the graph
graph = StateGraph(pipelinestate)

# add the nodes to the graph
graph.add_node("editor", editor_node)
graph.add_node("script", script_node)
graph.add_node("translation", translation_node)

# add the edges to the graph
graph.add_edge(START, "editor")
graph.add_edge("editor", "script")
graph.add_edge("script", "translation")
graph.add_edge("translation", END)

# compile the graph
app = graph.compile()

result = app.invoke({
    "raw_input": "AI is transforming the way we live and work. It has the potential to revolutionize industries, improve efficiency, and create new opportunities. However, it also raises ethical concerns and challenges that need to be addressed."
})

from rich.console import Console
from rich.markdown import Markdown
console = Console()
console.print("\n[bold green]FINAL HINGLISH SCRIPT[/bold green]")
console.print("=" * 60)
console.print(Markdown(result["final_output"]))