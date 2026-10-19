# !/bin/python3

# KaliGPT v1.3 (HackerX)
# /agents/__main__.py
# Set AI API keys & launch default model agent, provide Configuration (reset model, change model etc.) management
# Last Modified: 2 feb 2026

import sys
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
from .utils.agent_configs import update_api_key, get_available_ais, get_default_provider
from .utils.agent_management import AI_MANAGEMENT_OPTIONS, agent_management

# --- Set API key ---
def set_api_keys():
    try:
        available_ais = get_available_ais()

        ais = ""
        for ai in available_ais:
            ais += f"{available_ais.index(ai) + 1}. {ai}\n"
        print(f"Available AI Vendors:\n{ais}")
        selected = int(input("Select AI Vendor by number: ")) - 1
        if 0 <= selected < len(available_ais):
            selected_ai = available_ais[selected]
            new_key = input(f"Enter new API key for {selected_ai}: ")
            if update_api_key(selected_ai, new_key):
                print(f"[+] API key for {selected_ai} updated successfully.")
            else:
                print(f"[!] Failed to update API key for {selected_ai}.")
        else:
            print("[!] Invalid selection.")

    except KeyboardInterrupt:
        print("\nSee You,\nExiting Setup - KeyBoardInterrupt")


HELP_TEXT = """
KaliGPT v1.3 - Use AI in Linux / Windows via CLI easily

Usages:
         kaligpt [MODE] [Prompt]

MODES:
    -g  [--gemini]            =  use Gemini Models (Online, text & code)
    -o  [--ollama]            =  use Ollama / Local Models (Offline, text & code)
    -or [--openrouter]        =  use OpenRouter Models (Online, text & code)
    -c  [--chatgpt]           =  use OpenAI Models (Online, text & code)
    --web                     =  AIs official Web-Chat Opener (Online)
    --setup-keys              =  setup API keys for online models
    -h  [--help]              =  show this help message and exit

Model Management:
    /change-model             = change to a different AI model
    /reset-to-default-model   = reset to KaliGPT default AI model
    /list-tools               = list available tools for AI Agent

Examples:
     kaligpt                  (uses default model and interactive prompt)
     kaligpt "Help me find XSS on target.com"
     kaligpt -o "Analyze this log"
"""


def main(args):

    match args:
        case ["-h" | "--help", *_]:
            print(HELP_TEXT)
            return

        case ["-g" | "--gemini", *rest]:
            subprocess.run(["python", "-m", "agents.gemini", *rest])
            return

        case ["-o" | "--ollama", *rest]:
            subprocess.run(["python", "-m", "agents.ollama", *rest])
            return

        case ["-or" | "--openrouter", *rest]:
            subprocess.run(["python", "-m", "agents.openrouter", *rest])
            return

        case ["-c" | "--chatgpt", *rest]:
            subprocess.run(["python", "-m", "agents.chatgpt", *rest])
            return

        case ["--web", *rest]:
            subprocess.run(["python", "-m", "agents.web_launcher", *rest])
            return

        case ["--setup-keys"]:
            set_api_keys()

        case [option] if option in AI_MANAGEMENT_OPTIONS[:4]:
            agent_management(option)

        case _:
            default_model = get_default_provider()
            command = ["python", "-m", f"agents.{default_model}"]
            if args:
                command.extend(args)

            try:
                subprocess.run(command)

            except Exception as e:
                print(f"Exception occurred: {e}")

            except KeyboardInterrupt:
                print("\n\n")

if __name__ == "__main__":
    # print(sys.argv[1:])
    main(sys.argv[1:])
