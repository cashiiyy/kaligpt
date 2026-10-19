#!/usr/bin/env python3
# agents/web_ui.py
# KaliGPT v1.3 - Dynamic Web View (HackerX)
# Interactive Browser-based CyberSecurity AI Agent Workspace

import os
import sys
import json
import webbrowser
import threading
import argparse
from pathlib import Path
from flask import Flask, render_template, request, jsonify

# Windows encoding support
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Import KaliGPT utilities
from .utils.agent_configs import (
    _load_config,
    _save_config,
    get_api_key,
    get_default_provider,
    get_ai_specific_default_model,
    update_default_provider,
    update_ai_specific_default_model,
    update_api_key
)
from .utils.tools import get_tools_info, get_available_tools_data
from .utils.prompts import WEB_BUG_BOUNTY_AGENT, WEB_PENTESTER_AGENT, SYSTEM_PROMPT

# Paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "web" / "templates"
STATIC_DIR = BASE_DIR / "web" / "static"

app = Flask(
    __name__,
    template_folder=str(TEMPLATES_DIR),
    static_folder=str(STATIC_DIR)
)

# Tool function registry
TOOLS = get_tools_info()
TOOL_MAP = {func.__name__: func for func in TOOLS} if TOOLS else {}

ROLE_PROMPTS = {
    "web_bounty": WEB_BUG_BOUNTY_AGENT,
    "pentest": WEB_PENTESTER_AGENT,
    "code_audit": (
        "You are an expert offensive security code auditor specializing in vulnerability discovery. "
        "Analyze source code thoroughly for CWE top 25 flaws, SQL injection, RCE, logic errors, and privilege escalation. "
        "Provide actionable exploitation proof-of-concept and hardened patch code."
    ),
    "osint": (
        "You are an expert OSINT and Reconnaissance analyst. Guide the operator in gathering passive intelligence, "
        "subdomain enumeration, DNS records, historical archives, and mapping attack surfaces efficiently."
    )
}

# --- ROUTES ---

@app.route("/")
def index():
    """Serves the dynamic web view interface."""
    return render_template("index.html")


@app.route("/api/status", methods=["GET"])
def get_status():
    """Returns server and agent status."""
    cfg = _load_config()
    def_provider = cfg.get("default_provider", "ollama")
    def_model = cfg.get(def_provider, {}).get("default_model", "")
    return jsonify({
        "status": "online",
        "default_provider": def_provider,
        "default_model": def_model,
        "tools_count": len(TOOL_MAP),
        "platform": sys.platform
    })


@app.route("/api/config", methods=["GET"])
def get_config():
    """Returns current AI configuration."""
    cfg = _load_config()
    return jsonify(cfg)


@app.route("/api/config/update", methods=["POST"])
def update_config():
    """Updates active provider and active model."""
    data = request.get_json() or {}
    provider = data.get("provider")
    model = data.get("model")

    if provider:
        update_default_provider(provider)
    if provider and model:
        update_ai_specific_default_model(provider, model)

    return jsonify({"success": True})


@app.route("/api/config/key", methods=["POST"])
def save_key():
    """Saves API key or host endpoint URL."""
    data = request.get_json() or {}
    vendor = data.get("vendor")
    key = data.get("key")

    if not vendor or key is None:
        return jsonify({"success": False, "error": "Missing vendor or key"}), 400

    success = update_api_key(vendor, key)
    return jsonify({"success": success})


@app.route("/api/tools", methods=["GET"])
def list_tools():
    """Returns list of available KaliGPT security tools."""
    return jsonify(get_available_tools_data())


@app.route("/api/tools/execute", methods=["POST"])
def execute_tool():
    """Executes a KaliGPT security tool directly."""
    data = request.get_json() or {}
    tool_name = data.get("tool")
    args = data.get("args", {})

    if tool_name not in TOOL_MAP:
        return jsonify({"error": f"Tool '{tool_name}' not found"}), 404

    try:
        func = TOOL_MAP[tool_name]
        if isinstance(args, dict):
            result = func(**args)
        else:
            result = func()
        return jsonify({"tool": tool_name, "result": result})
    except Exception as e:
        return jsonify({"tool": tool_name, "error": str(e)}), 500


# --- CHAT DISPATCHER ---

def handle_ollama_chat(model: str, messages: list, system_prompt: str):
    """Executes chat using Ollama or OpenAI-compatible local server with streaming to prevent timeout."""
    host = get_api_key("ollama") or "http://localhost:11434"
    clean_host = host.rstrip("/")

    # Detect OpenAI-compatible server (LM Studio port 1234 or /v1/models response)
    is_openai_compat = ":1234" in clean_host
    if not is_openai_compat:
        try:
            import requests
            r = requests.get(f"{clean_host}/v1/models", timeout=3.0)
            if r.status_code == 200 and "data" in r.json():
                is_openai_compat = True
        except Exception:
            pass

    formatted_msgs = [{"role": "system", "content": system_prompt}] + messages

    if is_openai_compat:
        from openai import OpenAI
        base_url = clean_host
        if not base_url.endswith("/v1"):
            base_url += "/v1"

        client = OpenAI(base_url=base_url, api_key="lm-studio", timeout=1800.0)

        # Stream chunks to keep socket active and capture reasoning
        try:
            stream_resp = client.chat.completions.create(
                model=model,
                messages=formatted_msgs,
                stream=True
            )
            content_parts = []
            reasoning_parts = []
            for chunk in stream_resp:
                if not getattr(chunk, "choices", None):
                    continue
                delta = chunk.choices[0].delta
                reasoning = getattr(delta, "reasoning_content", None)
                if reasoning:
                    reasoning_parts.append(reasoning)
                content_delta = getattr(delta, "content", None)
                if content_delta:
                    content_parts.append(content_delta)

            full_content = "".join(content_parts)
            full_reasoning = "".join(reasoning_parts)
            if not full_content and full_reasoning:
                full_content = full_reasoning
            return {"response": full_content, "thinking": full_reasoning or None}
        except Exception:
            # Fallback to standard non-streaming
            resp = client.chat.completions.create(
                model=model,
                messages=formatted_msgs,
                stream=False
            )
            choice = resp.choices[0]
            content = choice.message.content or ""
            reasoning = getattr(choice.message, "reasoning_content", None)
            if not content and reasoning:
                content = reasoning
            return {"response": content, "thinking": reasoning}
    else:
        from ollama import Client
        client = Client(host=clean_host, timeout=1800.0)
        try:
            stream_resp = client.chat(
                model=model,
                messages=formatted_msgs,
                stream=True
            )
            content_parts = []
            reasoning_parts = []
            in_think = False
            for chunk in stream_resp:
                delta = chunk["message"]["content"]
                if "<think>" in delta:
                    in_think = True
                    delta = delta.replace("<think>", "")
                if "</think>" in delta:
                    in_think = False
                    parts = delta.split("</think>")
                    reasoning_parts.append(parts[0])
                    delta = parts[1] if len(parts) > 1 else ""
                if in_think:
                    reasoning_parts.append(delta)
                else:
                    content_parts.append(delta)

            full_content = "".join(content_parts).strip()
            full_reasoning = "".join(reasoning_parts).strip()
            if not full_content and full_reasoning:
                full_content = full_reasoning
            return {"response": full_content, "thinking": full_reasoning or None}
        except Exception:
            resp = client.chat(
                model=model,
                messages=formatted_msgs
            )
            content = resp["message"]["content"]
            thinking = None
            if "<think>" in content and "</think>" in content:
                parts = content.split("</think>")
                thinking = parts[0].replace("<think>", "").strip()
                content = parts[1].strip()
            return {"response": content, "thinking": thinking}


def handle_gemini_chat(model: str, messages: list, system_prompt: str):
    """Executes chat using Google Gemini."""
    api_key = get_api_key("gemini")
    if not api_key or "YOUR_" in api_key:
        raise ValueError("Gemini API key is not configured. Please set it in Config.")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)

    contents = []
    for m in messages:
        role = "user" if m.get("role") == "user" else "model"
        contents.append(types.Content(
            role=role,
            parts=[types.Part.from_text(text=m.get("content", ""))]
        ))

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.7
    )

    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=config
    )
    return {"response": response.text or "", "thinking": None}


def handle_chatgpt_chat(model: str, messages: list, system_prompt: str):
    """Executes chat using OpenAI ChatGPT."""
    api_key = get_api_key("chatgpt")
    if not api_key or "YOUR_" in api_key:
        raise ValueError("ChatGPT API key is not configured. Please set it in Config.")

    from openai import OpenAI
    client = OpenAI(api_key=api_key, timeout=300.0)
    formatted_msgs = [{"role": "system", "content": system_prompt}] + messages

    response = client.chat.completions.create(
        model=model,
        messages=formatted_msgs
    )
    content = response.choices[0].message.content or ""
    return {"response": content, "thinking": None}


def handle_openrouter_chat(model: str, messages: list, system_prompt: str):
    """Executes chat using OpenRouter."""
    api_key = get_api_key("openrouter")
    if not api_key or "YOUR_" in api_key:
        raise ValueError("OpenRouter API key is not configured. Please set it in Config.")

    from openai import OpenAI
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        timeout=300.0
    )
    formatted_msgs = [{"role": "system", "content": system_prompt}] + messages

    response = client.chat.completions.create(
        model=model,
        messages=formatted_msgs
    )
    content = response.choices[0].message.content or ""
    reasoning = getattr(response.choices[0].message, "reasoning", None)
    return {"response": content, "thinking": reasoning}


@app.route("/api/chat", methods=["POST"])
def chat():
    """Processes chat prompt with selected provider and active model."""
    data = request.get_json() or {}
    prompt = data.get("prompt", "").strip()
    provider = data.get("provider", "ollama")
    model = data.get("model")
    preset = data.get("preset", "web_bounty")
    history = data.get("history", [])

    if not prompt:
        return jsonify({"success": False, "error": "Empty prompt"}), 400

    system_prompt = ROLE_PROMPTS.get(preset, WEB_BUG_BOUNTY_AGENT)

    # Format history turns
    formatted_history = []
    for h in history:
        r = h.get("role")
        c = h.get("content", "")
        if r in ("user", "assistant") and c:
            formatted_history.append({"role": r, "content": c})

    if not formatted_history or formatted_history[-1].get("content") != prompt:
        formatted_history.append({"role": "user", "content": prompt})

    try:
        if provider == "ollama":
            result = handle_ollama_chat(model, formatted_history, system_prompt)
        elif provider == "gemini":
            result = handle_gemini_chat(model, formatted_history, system_prompt)
        elif provider == "chatgpt":
            result = handle_chatgpt_chat(model, formatted_history, system_prompt)
        elif provider == "openrouter":
            result = handle_openrouter_chat(model, formatted_history, system_prompt)
        elif provider == "litellm":
            import litellm
            formatted_msgs = [{"role": "system", "content": system_prompt}] + formatted_history
            resp = litellm.completion(model=model, messages=formatted_msgs)
            result = {
                "response": resp.choices[0].message.content or "",
                "thinking": None
            }
        else:
            return jsonify({"success": False, "error": f"Unsupported provider: {provider}"}), 400

        return jsonify({
            "success": True,
            "response": result.get("response", ""),
            "thinking": result.get("thinking"),
            "tool_calls": []
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


def open_browser(url: str):
    """Opens browser after server start."""
    try:
        webbrowser.open(url)
    except Exception:
        pass


def run_server(host="127.0.0.1", port=5000, no_browser=False):
    """Runs the Flask web view server."""
    url = f"http://{host}:{port}"
    print(f"\n\033[92m[+] KaliGPT Dynamic Web View starting at: {url}\033[0m")
    print(f"\033[96m[*] Press Ctrl+C to stop server.\033[0m\n")

    if not no_browser:
        threading.Timer(1.2, open_browser, args=[url]).start()

    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KaliGPT Dynamic Web View Interface")
    parser.add_argument("--host", default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=5000, help="Port to listen on (default: 5000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open browser")
    args = parser.parse_args()

    run_server(host=args.host, port=args.port, no_browser=args.no_browser)
