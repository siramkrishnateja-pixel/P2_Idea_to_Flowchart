"""
Idea to FlowChart - Convert system ideas into visual flowcharts/architecture diagrams
Using Hugging Face APIs: Text → Mermaid Code → Visual Diagram
"""

import os
import re

from dotenv import load_dotenv
load_dotenv()

import gradio as gr
from huggingface_hub import InferenceClient

# Hugging Face model for text-to-Mermaid conversion
# Using Qwen - good at following instructions and generating structured output
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"

# System prompt to guide the LLM to generate valid Mermaid code
MERMAID_SYSTEM_PROMPT = """You are an expert at creating Mermaid.js diagrams. Your task is to convert user descriptions of systems, processes, or ideas into valid Mermaid diagram code.

Rules:
1. Output ONLY the raw Mermaid code - no markdown code blocks, no explanations, no extra text
2. Use flowchart TD or flowchart LR for process flows and system architectures
3. Use proper Mermaid syntax: nodes as [Text], (Text), or {Text}
4. Use --> for arrows, |label| for labeled arrows
5. For system architecture: show components, data flow, and relationships
6. Keep diagrams clean and readable - max 15-20 nodes
7. Start directly with "flowchart" or "graph" - no preamble

Examples of valid output:
flowchart TD
    A[User Input] --> B[Process]
    B --> C[Output]

flowchart LR
    Client -->|HTTP| API
    API --> Database"""


def extract_mermaid_code(text: str) -> str:
    """Extract Mermaid code from LLM response (handles markdown code blocks)."""
    text = text.strip()
    # Remove ```mermaid and ``` if present
    if "```mermaid" in text.lower():
        text = re.sub(r"```mermaid\s*", "", text, flags=re.IGNORECASE)
    if "```" in text:
        text = re.sub(r"```\s*", "", text)
    return text.strip()


def text_to_mermaid(system_idea: str, api_token: str | None) -> tuple[str, str]:
    """
    Step 1: Convert text description to Mermaid code using Hugging Face API.
    Returns (mermaid_code, error_message). If success, error_message is empty.
    """
    if not system_idea or not system_idea.strip():
        return "", "Please enter a system idea or description."

    token = api_token or os.environ.get("HF_API_KEY") or os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
    if not token:
        return "", (
            "⚠️ Hugging Face API token required. "
            "Get one at https://huggingface.co/settings/tokens and paste it in the API Token field below, "
            "or set HF_API_KEY environment variable."
        )

    try:
        client = InferenceClient(token=token, model=MODEL_ID)
        user_prompt = f"""Convert this system/idea into a Mermaid flowchart or architecture diagram:

"{system_idea.strip()}"

Output only the Mermaid code:"""

        response = client.chat_completion(
            messages=[
                {"role": "system", "content": MERMAID_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1024,
            temperature=0.3,
        )

        content = response.choices[0].message.content
        if not content:
            return "", "No response generated. Try a different description."

        mermaid_code = extract_mermaid_code(content)
        if not mermaid_code:
            return "", "Could not extract Mermaid code from response."

        # Validate it looks like Mermaid (starts with flowchart, graph, etc.)
        if not re.match(r"^(flowchart|graph|sequenceDiagram|classDiagram)\s", mermaid_code, re.IGNORECASE):
            # Prepend flowchart TD if it seems like raw node definitions
            if " --> " in mermaid_code or " -> " in mermaid_code:
                mermaid_code = "flowchart TD\n    " + mermaid_code.replace("\n", "\n    ")

        return mermaid_code, ""

    except Exception as e:
        error_msg = str(e)
        if "401" in error_msg or "Unauthorized" in error_msg:
            return "", "Invalid API token. Check your Hugging Face token."
        if "429" in error_msg or "Rate" in error_msg.lower():
            return "", "Rate limit exceeded. Please wait a moment and try again."
        return "", f"API Error: {error_msg}"


def mermaid_to_display(mermaid_code: str) -> str:
    """
    Step 2: Wrap Mermaid code for Gradio Markdown rendering.
    Gradio renders Mermaid when wrapped in ```mermaid blocks.
    """
    if not mermaid_code:
        return ""
    return f"```mermaid\n{mermaid_code}\n```"


def generate_diagram(system_idea: str, api_token: str) -> tuple[str, str, str]:
    """
    Full pipeline: Text → Mermaid Code → Display.
    Returns (mermaid_code, markdown_display, error_message).
    """
    mermaid_code, error = text_to_mermaid(system_idea, api_token)
    if error:
        return "", "", error

    markdown = mermaid_to_display(mermaid_code)
    return mermaid_code, markdown, ""


# Example prompts for users
EXAMPLES = [
    "User sends login request to server, server validates credentials and returns token",
    "E-commerce checkout: Add to cart, payment, order confirmation",
    "Microservices architecture: API Gateway, Auth Service, Order Service, Database",
    "User registration flow with email verification",
    "Data pipeline: Collect data from sensors, process in Spark, store in warehouse",
]


with gr.Blocks(
    title="Idea to FlowChart",
    theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="slate"),
    css="""
    .diagram-container { min-height: 400px; }
    .examples-box { padding: 1rem; background: var(--block-background-fill); border-radius: 8px; }
    """
) as demo:
    gr.Markdown(
        """
        # 🎯 Idea to FlowChart
        **Convert your system ideas into visual flowcharts and architecture diagrams**
        
        Describe your system, process, or idea in plain English. The AI will generate a Mermaid diagram that you can visualize below.
        
        **Powered by:** Hugging Face Inference API (Text → Mermaid) + Gradio (Mermaid → Diagram)
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            idea_input = gr.Textbox(
                label="Describe your system or idea",
                placeholder="e.g., User logs in, server validates, returns dashboard...",
                lines=4,
            )
            api_token_input = gr.Textbox(
                label="Hugging Face API Token",
                type="password",
                placeholder="hf_xxxxxxxx (get one at huggingface.co/settings/tokens)",
            )
            generate_btn = gr.Button("✨ Generate Diagram", variant="primary")

            gr.Examples(
                examples=EXAMPLES,
                inputs=idea_input,
                label="Try these examples",
            )

        with gr.Column(scale=1):
            error_output = gr.Markdown(visible=False)
            diagram_display = gr.Markdown(
                value="*Your diagram will appear here after generation.*",
                elem_classes=["diagram-container"],
            )
            mermaid_code_output = gr.Code(
                label="Mermaid Code (editable - paste above to regenerate)",
                language="mermaid",
                lines=10,
                visible=True,
            )

    def on_generate(idea: str, token: str):
        mermaid_code, markdown, error = generate_diagram(idea, token)
        if error:
            return (
                gr.update(value=f"❌ **Error:** {error}", visible=True),
                "```mermaid\nflowchart TD\n    A[Enter your idea] --> B[Click Generate]\n```",
                "",
            )
        return (
            gr.update(value="", visible=False),
            markdown,
            mermaid_code,
        )

    generate_btn.click(
        fn=on_generate,
        inputs=[idea_input, api_token_input],
        outputs=[error_output, diagram_display, mermaid_code_output],
    )

    # Allow editing Mermaid code and re-rendering
    def on_code_change(mermaid_code: str):
        if mermaid_code:
            return mermaid_to_display(mermaid_code)
        return "*Edit the Mermaid code and it will update the diagram.*"

    mermaid_code_output.change(
        fn=on_code_change,
        inputs=[mermaid_code_output],
        outputs=[diagram_display],
    )

    gr.Markdown(
        """
        ---
        ### 💡 Tips
        - Be specific about the steps/components in your system
        - Mention relationships (e.g., "sends request to", "validates", "returns")
        - For architecture: name the services/components and how they connect
        """
    )

if __name__ == "__main__":
    demo.launch()
