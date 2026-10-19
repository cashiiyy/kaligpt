#!/usr/bin/env python3

# kaligpt Ollama model's thinking and tool support
# /agent/utils/ollama_tool_think_support_check.py
# Updated: 23 March 2026


from ollama import Client

try:
    from .agent_configs import get_api_key
except ImportError:
    from agent_configs import get_api_key

msg = [{"role": "user", "content": "Just say Hii"}]
MODEL: str
client: Client
SUPPORT_STAGE: int

def addition():
    pass


def check_tool_support():
    """
    Verify whether the selected model can handle tool calls.
    We send a dummy request with an empty tools list – if the call succeeds the model supports the tools argument, otherwise it raises.
    """
    try:
        client.chat(model=MODEL, messages=msg, tools=[addition])
        return True
    except:
        return False


def check_think_support():
    """
    Check if the selected model supports the think parameter.
    """
    try:
        client.chat(model=MODEL, messages=msg, think=True)
        return True
    except:
        return False


def model_support_check(model, api_url = get_api_key("ollama")):
    global client, MODEL, SUPPORT_STAGE
    try:
        import requests
        clean_url = api_url.rstrip("/")
        r = requests.get(f"{clean_url}/v1/models", timeout=2)
        if r.status_code == 200 and "data" in r.json():
            SUPPORT_STAGE = 0
            return SUPPORT_STAGE
    except Exception:
        pass

    try:
        client = Client(host=api_url)
        MODEL = model

        tool_support = check_tool_support()
        think_support = check_think_support()

        if tool_support and think_support:
            SUPPORT_STAGE = 3  # supports tools & thinking
        elif not think_support and tool_support:
            SUPPORT_STAGE = 2  # supports tools
        elif think_support and not tool_support:
            SUPPORT_STAGE = 1  # supports thinking
        else:
            SUPPORT_STAGE = 0  # nothing supported
    except Exception:
        SUPPORT_STAGE = 0

    return SUPPORT_STAGE

if __name__ == "__main__":
    print(model_support_check("gpt-oss:120b-cloud", "http://localhost:11434", ))
    print(check_tool_support())
