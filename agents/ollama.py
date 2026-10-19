#!/usr/bin/env python3

# kaligpt Ollama Agent
# /agent/ollama_.py
# Updated: 23 March 2026


import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from ollama import Client

from .utils.parse_n_print_response import parse_n_print_response
from .utils.prompts import WEB_BUG_BOUNTY_AGENT as SYSTEM_PROMPT
from .utils.agent_configs import get_ai_specific_default_model, get_api_key
from .utils.tools import get_tools_info
from .utils.agent_management import AI_MANAGEMENT_OPTIONS, agent_management
from .utils.openai_tool_adapter import openai_tool_adapter
from .utils.ollama_tool_think_support_check import model_support_check


# --- GLOBAL VARIABLES ---
OLLAMA_API_URL: str   # OLLAMA API URL as OLLAMA_API_KEY
OLLAMA_MODEL: str
TOOLS_INFO: list
TOOL_FUNCTION_MAP: dict
client: Client
SUPPORT_STAGE: int


class OpenAICompatClient:
    def __init__(self, host):
        from openai import OpenAI
        base_url = host.rstrip("/")
        if not base_url.endswith("/v1"):
            base_url += "/v1"
        self._client = OpenAI(base_url=base_url, api_key="lm-studio", timeout=1800.0)
        self.streamed = False

    def chat(self, model, messages, tools=None, think=None):
        api_messages = []
        for m in messages:
            role = m.get("role")
            content = m.get("content", "")
            if role in ("system", "user", "assistant"):
                api_messages.append({"role": role, "content": content})
            elif role == "tool":
                api_messages.append({"role": "user", "content": f"[Tool Result]: {content}"})

        kwargs = {
            "model": model,
            "messages": api_messages,
        }
        if tools:
            kwargs["tools"] = tools

        self.streamed = False

        class Msg:
            def __init__(self, c, tc):
                self.content = c
                self.tool_calls = tc

        class Resp:
            def __init__(self, m):
                self.message = m

        try:
            stream_resp = self._client.chat.completions.create(**kwargs, stream=True)
            if hasattr(stream_resp, "choices") and not hasattr(stream_resp, "__iter__"):
                choice = stream_resp.choices[0]
                content = choice.message.content or ""
                reasoning = getattr(choice.message, "reasoning_content", None)
                if not content and reasoning:
                    content = reasoning
                elif content and reasoning:
                    content = f"> [Thinking]\n> {reasoning}\n\n{content}"
                tool_calls = getattr(choice.message, "tool_calls", None) or []
                return Resp(Msg(content, tool_calls))
        except Exception:
            resp = self._client.chat.completions.create(**kwargs, stream=False)
            choice = resp.choices[0]
            content = choice.message.content or ""
            reasoning = getattr(choice.message, "reasoning_content", None)
            if not content and reasoning:
                content = reasoning
            elif content and reasoning:
                content = f"> [Thinking]\n> {reasoning}\n\n{content}"
            tool_calls = getattr(choice.message, "tool_calls", None) or []
            return Resp(Msg(content, tool_calls))

        content_parts = []
        reasoning_parts = []
        tool_calls_dict = {}
        in_thinking = False

        try:
            for chunk in stream_resp:
                if not getattr(chunk, "choices", None):
                    continue
                delta = chunk.choices[0].delta

                reasoning = getattr(delta, "reasoning_content", None)
                if reasoning:
                    if not in_thinking:
                        print("\n> [Thinking]\n> ", end="", flush=True)
                        in_thinking = True
                    print(reasoning.replace("\n", "\n> "), end="", flush=True)
                    reasoning_parts.append(reasoning)

                content_delta = getattr(delta, "content", None)
                if content_delta:
                    if in_thinking:
                        print("\n\n", end="", flush=True)
                        in_thinking = False
                    print(content_delta, end="", flush=True)
                    content_parts.append(content_delta)

                tool_calls_chunk = getattr(delta, "tool_calls", None)
                if tool_calls_chunk:
                    for tc in tool_calls_chunk:
                        idx = getattr(tc, "index", 0) or 0
                        if idx not in tool_calls_dict:
                            tool_calls_dict[idx] = tc
                        else:
                            if tc.function and tc.function.arguments:
                                prev_args = tool_calls_dict[idx].function.arguments or ""
                                tool_calls_dict[idx].function.arguments = prev_args + tc.function.arguments

            self.streamed = True
        except Exception as e:
            if not content_parts and not reasoning_parts:
                raise e

        if in_thinking:
            print("", flush=True)
        print("", flush=True)

        full_content = "".join(content_parts)
        full_reasoning = "".join(reasoning_parts)
        if not full_content and full_reasoning:
            full_content = full_reasoning
        elif full_content and full_reasoning:
            full_content = f"> [Thinking]\n> {full_reasoning}\n\n{full_content}"

        tool_calls = list(tool_calls_dict.values())
        return Resp(Msg(full_content, tool_calls))


def initialize_agent():
    global SUPPORT_STAGE, OLLAMA_API_URL
    global OLLAMA_MODEL
    OLLAMA_MODEL = get_ai_specific_default_model("ollama")

    # Check Models for Tools & thinking support and specify SUPPORT_STAGE based on that
    OLLAMA_API_URL = get_api_key("ollama")

    SUPPORT_STAGE = model_support_check(OLLAMA_MODEL, OLLAMA_API_URL)


def initialize_configs():
    global OLLAMA_API_URL, TOOLS_INFO, TOOL_FUNCTION_MAP, client
    try:
        OLLAMA_API_URL = get_api_key("ollama")

        initialize_agent()

        # initialize client (detect OpenAI-compatible server like LM Studio vs native Ollama)
        is_openai_compat = False
        try:
            import requests
            r = requests.get(f"{OLLAMA_API_URL}/v1/models", timeout=2)
            if r.status_code == 200 and "data" in r.json():
                is_openai_compat = True
        except Exception:
            pass

        if is_openai_compat:
            client = OpenAICompatClient(host=OLLAMA_API_URL)
        else:
            client = Client(host=OLLAMA_API_URL)

        tools = get_tools_info()
        TOOLS_INFO = [openai_tool_adapter(f) for f in tools]

        if not TOOLS_INFO:
            print("[!] No external tools loaded.")

        # --- TOOL EXECUTION HELPER (Your Original Function) ---
        TOOL_FUNCTION_MAP = {func.__name__: func for func in tools} if tools else {}

    except Exception as e:
        print(f"Failed to initialize Ollama Agent: {e}\n[!] OLLAMA_API_URL may be misconfigured or unreachable.")
        sys.exit(1)


MAX_TURNS = 6   # user+assistant pairs

def trim_history(history):
    """ Trim chat history to keep within MAX_TURNS """
    system = [m for m in history if m["role"] == "system"]
    rest = [m for m in history if m["role"] != "system"]
    return system + rest[-MAX_TURNS * 2:]


def execute_function_calls(function_calls):
    response_parts = []

    for call in function_calls:
        func_name = getattr(call.function, "name", "")
        if isinstance(call.function.arguments, str):
            import json
            try:
                func_args = json.loads(call.function.arguments)
            except Exception:
                func_args = {}
        else:
            func_args = dict(call.function.arguments)

        print(f"\n[HackerX Tool Use] name: {func_name}, args: {func_args}")

        if func_name in TOOL_FUNCTION_MAP:
            try:
                result_text = TOOL_FUNCTION_MAP[func_name](**func_args)
            except Exception as e:
                result_text = f"Tool execution failed with error: {e}"
        else:
            result_text = f"Tool {func_name} not found!"

        response_parts.append({
                "name": func_name,
                "result": str(result_text)
            })

    return response_parts


def request_resp(messages, tools):

    match SUPPORT_STAGE:
        case 0:
            # No thinking & tools supported
            response = client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
            )
            return response

        case 1:
            # Thinking supported
            response = client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                think=True,
            )
            return response

        case 2:
            # tools supported
            response = client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                tools=tools,
            )
            return response

        case _:
            # Both Thinking and Tools supported
            response = client.chat(
                model=OLLAMA_MODEL,
                messages=messages,
                tools=tools,
                think=True,
            )
            return response


def ask(user_input, history, tools):
    """Ask Ollama Models for Response based on Support Stage

        Stage   Description
        0       Not Supports both Tool & Thinking
        1       Supports Thinking
        2       Supports Tools
        3       Supports Both Tools & Thinking.
    """

    messages = trim_history(history) + [{"role": "user", "content": user_input}]
    full_content: str

    while True:
        try:
            response = request_resp(messages=messages, tools=tools)

            tool_calls = []
            full_content = ""

            if response.message.content:
                # print(chunk.message.content, end="", flush=True)
                full_content += response.message.content
            if response.message.tool_calls:
                tool_calls.extend(response.message.tool_calls)

            # Append full assistant message to history
            messages.append({
                "role": "assistant",
                "content": full_content,
                "tool_calls": tool_calls
            })

            if tool_calls:
                tool_results = execute_function_calls(tool_calls)
                messages.append({
                    "role": "tool",
                    "content": str(tool_results)
                })
            else:
                break

        except Exception as e:
            print(f"[!] Error: {e}")
            sys.exit(1)

    return full_content, messages


def main(prompt=None):

    # Initialize chat history with system prompt
    chat_history: list = [{"role": "system", "content": SYSTEM_PROMPT}]

    initialize_configs()   # initialize configs for Ollama

    # Print tool banner
    print(f"㉿ HackerX ( ollama/{OLLAMA_MODEL} )")
    while True:
        try:
            if prompt is None:
                prompt = str(input("\nYou ➤ "))

            prompt_clean = prompt.lower().strip()
            if prompt_clean in ("-h", "--help", "help"):
                from .__main__ import HELP_TEXT
                print(HELP_TEXT)
                prompt = None
                continue

            if prompt_clean in ("exit", "quit", "/exit", "/quit", "/bye"):
                print("\n   Exiting HackerX. See you later!")
                break

            if prompt.lower().replace("-", " ").strip() in AI_MANAGEMENT_OPTIONS:
                agent_management(prompt.lower().replace("-", " ").strip())
                initialize_agent()
                prompt = None
                continue

            response, chat_history = ask(
                history=chat_history,
                user_input=prompt,
                tools=TOOLS_INFO
            )

            if not getattr(client, "streamed", False):
                parse_n_print_response(response)
            prompt = None

        except KeyboardInterrupt:
            print("\n   Exiting HackerX. See you later!")
            break

        except Exception as err:
            print(f"\n[!] An error occurred: {err}")
            break

if __name__ == "__main__":

    if len(sys.argv) > 1:
        args = ' '.join(sys.argv[1:])
        if args.strip() in ("-h", "--help", "help"):
            from .__main__ import HELP_TEXT
            print(HELP_TEXT)
            sys.exit(0)
        main(args)
    else:
        main()
