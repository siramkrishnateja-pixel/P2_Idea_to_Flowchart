---
title: Idea to FlowChart
emoji: 📊
colorFrom: indigo
colorTo: slate
sdk: gradio
sdk_version: 5.22.0
python_version: 3.10
app_file: app.py
pinned: false
---

# Idea to FlowChart

Convert your system ideas into visual flowcharts and architecture diagrams using AI.

**Pipeline:**
1. **Text → Mermaid Code** – Hugging Face Inference API (Qwen 7B)
2. **Mermaid Code → Diagram** – Gradio Markdown (native Mermaid rendering)

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Get a Hugging Face API token

1. Create a free account at [huggingface.co](https://huggingface.co)
2. Go to [Settings → Access Tokens](https://huggingface.co/settings/tokens)
3. Create a token with **Read** access

### 3. Run the app

```bash
python app.py
```

Then paste your token in the app’s **Hugging Face API Token** field when you use it.

**Using environment variable (recommended):**

```bash
# Windows PowerShell
$env:HF_TOKEN = "hf_your_token_here"
python app.py

# Linux/Mac
export HF_TOKEN="hf_your_token_here"
python app.py
```

## Usage

1. Describe your system or idea in plain English (e.g. “User logs in, server validates, returns dashboard”).
2. Paste your Hugging Face API token (or rely on `HF_TOKEN`).
3. Click **Generate Diagram**.
4. View the flowchart. You can edit the Mermaid code and the diagram will update live.

## Example prompts

- *User sends login request to server, server validates credentials and returns token*
- *E-commerce checkout: Add to cart, payment, order confirmation*
- *Microservices: API Gateway, Auth Service, Order Service, Database*
- *User registration flow with email verification*
- *Data pipeline: Collect from sensors, process in Spark, store in warehouse*

## Project structure

```
P2_Idea_to_FlowChart/
├── app.py           # Main Gradio application
├── requirements.txt # Python dependencies
└── README.md        # This file
```

## Notes

- Free Hugging Face tier: ~300 requests/hour.
- Diagram quality depends on how clearly you describe the flow.
- You can refine the generated Mermaid code directly in the app.
