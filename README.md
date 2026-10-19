[//]: #  ( Kasinathan P S - KaliGPT )
[//]: #  ( Updated: 2026 )


# KaliGPT v1.3 
**KaliGPT** : An Agentic assistance in Linux CLI and Dynamic Web View for Ethical Hacking & Cybersecurity to use AI with ease to learn and master CyberSecurity.

### **⭐ Star this repo if you found it helpful!**

**Creator & Maintainer:** [Kasinathan P S](https://github.com/cashiiyy) (cashiiyy)

## Badges
<div align="center">

 
<!-- Repository Statistics -->
[![Release](https://img.shields.io/github/v/tag/SudoHopeX/KaliGPT?label=Release&color=0078D4&style=for-the-badge&logo=github)](https://github.com/SudoHopeX/KaliGPT/tags)
[![Stars](https://img.shields.io/github/stars/cashiiyy/kaligpt?label=Stars&color=FFD700&style=for-the-badge&logo=reverbnation&logoColor=black)](https://github.com/cashiiyy/kaligpt/stargazers)
[![Forks](https://img.shields.io/github/forks/cashiiyy/kaligpt?label=Forks&color=28a745&style=for-the-badge&logo=github)](https://github.com/cashiiyy/kaligpt/network/members)
 
<!-- Traffic & Clones (Dynamic JSON) -->
![Clones](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/SudoHopeX/KaliGPT/hackerx/clones_lifetime.json&query=$.message&label=Clones&color=A52A2A&style=for-the-badge&logo=git&logoColor=white)
![Views](https://img.shields.io/badge/dynamic/json?url=https://raw.githubusercontent.com/SudoHopeX/KaliGPT/hackerx/views_lifetime.json&query=$.message&label=Views&color=800080&style=for-the-badge&logo=github&logoColor=white)


<!-- Project & Community Badges -->
[![License](https://img.shields.io/badge/License-Open_Source-green?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)
[![Contributions Welcomed](https://img.shields.io/badge/Contributions-Welcomed-violet?style=for-the-badge&logo=githubsponsors&logoColor=white)](https://github.com/cashiiyy/kaligpt/issues/new)
</div>

------
<!-- Feature & Support Badges -->
<div align="center">
 
![Dynamic Web View](https://img.shields.io/badge/Dynamic_Web_View-00FF66?style=for-the-badge&logo=googlechrome&logoColor=black)
![Automated Installation](https://img.shields.io/badge/Automated_Installation-0078D4?style=for-the-badge&logo=powershell&logoColor=white)
![Flexible AI](https://img.shields.io/badge/Flexible_AI_Backend-FF6F00?style=for-the-badge&logo=deepmind&logoColor=white)
![CLI](https://img.shields.io/badge/CLI_Interface-4EAA25?style=for-the-badge&logo=gnumetadataterminal&logoColor=white)
![Tool Call](https://img.shields.io/badge/Tool_Calling-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Online Search](https://img.shields.io/badge/Online_Search-4285F4?style=for-the-badge&logo=google&logoColor=white)
[![Termux Support](https://img.shields.io/badge/Termux_Supported-EF3939?style=for-the-badge&logo=termux&logoColor=white)](https://github.com/cashiiyy/kaligpt)
</div>

------
<!-- Available Backends-->
<div align="center">

![Gemini](https://img.shields.io/badge/Gemini-8E75FF?style=for-the-badge&logo=googlegemini&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)
![OpenRouter](https://img.shields.io/badge/OpenRouter-6566f1?style=for-the-badge&logo=openrouter&logoColor=white)
![ChatGPT](https://img.shields.io/badge/ChatGPT-74aa9c?style=for-the-badge&logo=openai&logoColor=white)
![LiteLLM](https://img.shields.io/badge/🚅_LiteLLM-7C3AED?style=for-the-badge&logoColor=white)
</div>

## 🌐 Dynamic Web View (Hacker Terminal)

<div align="center">
  <img src="assets/kaligpt_dynamic_webview.png" alt="KaliGPT Dynamic Web View Interface" style="width:100%; max-width:900px; border-radius:8px; border:1px solid #00ff66;">
</div>

KaliGPT now features an **interactive, spacious dynamic web terminal** equipped with:
- **Full Markdown Output Rendering:** Tables, lists, quotes, and syntax-highlighted code blocks with 1-click clipboard copy.
- **Deep Reasoning & Thought Tracing:** Collapsible trace views for reasoning models (DeepSeek, Qwen, Think stages).
- **Armed Security Tools Suite:** Real-time tool execution panel with parameter editing and output inspection.
- **Provider & Model Switching:** Instantly swap between local Ollama / LM Studio and cloud backends (Gemini, ChatGPT, OpenRouter).
- **Session Export:** 1-click export of chat sessions into clean Markdown (`.md`).
- **Cyber Aesthetics & Themes:** Custom themes (Kali Emerald, Cyber Cyan, Ghost Purple) with spacious typography and terminal layout.

### Commands to Launch Dynamic Web View
```bash
# Launch interactive dynamic web view in browser (Default: http://127.0.0.1:5000)
kaligpt --webview

# Or using short flag
kaligpt -w

# Or via Python module directly
python -m agents -w

# Custom host / port:
python -m agents.web_ui --host 0.0.0.0 --port 8080
```

---

## Installation

1. Download KaliGPT Installer
    ```bash
    curl -sL https://raw.githubusercontent.com/cashiiyy/kaligpt/refs/heads/hackerx/install.sh | bash
    ```
    > Note: Use within permitted directory without root user
2. Install KaliGPT ( don't use sudo in Termux )
   ```bash
   sudo bash kaligptinstaller.sh
   ```

## KaliGPT Usages
use command `kaligpt -h` to see below usages after installation

```help
  HackerX (KaliGPT v1.3) - Use AI in Linux via CLI easily
                         - by Kasinathan P S (cashiiyy)

Usages:
        kaligpt [MODE(Optional)] [Prompt(Optional)]

MODES:
    -w  [--webview]           =  launch Dynamic Web View / Web Terminal
    -g  [--gemini]            =  use Gemini models (Online)
    -o  [--ollama]            =  use local models via Ollama (Offline, cloud: online)
    -or [--openrouter]        =  use OpenRouter models (Online)
    -c  [--chatgpt]           =  use OpenAI models (Online)
    -ll [--litellm]           =  use 100+ providers via LiteLLM (Online)
    --web                     =  AIs official Web-Chat Opener (Online)
    --setup-keys              =  setup API keys for online models
    -u [--update]             =  update KaliGPT to latest version
    -v [--version]            =  show KaliGPT version and exit
    -lr [--list-providers]    =  list KaliGPT available providers (vendors)
    -h  [--help]              =  show this help message and exit

Model Management:
    /change-model             = change to a different AI model
    /reset-to-default-model   = reset to KaliGPT default AI model
    /list-tools               = list available tools for AI Agent

Examples:
     kaligpt --webview        (launches dynamic web terminal in browser)
     kaligpt                  (uses default model and interactive CLI prompt)
     kaligpt "Help me find XSS on target.com"
     kaligpt -o "Analyze this log"
     kaligpt -g "How to Scan a website for subdomains using tools"
```

## Requirements
Read all Requirements [here](/requirements/globals.md)

## Disclaimer
> [!WARNING]
> :warning: HackerX (KaliGPT v1.3) is in active development. Contribute by raising an issue or [sending a PR](https://github.com/cashiiyy/kaligpt/pulls).
>
> Access to this library and the use of information, materials (or portions thereof), is **<u>not intended</u>, and is <u>prohibited</u>, where such access or use violates applicable laws or regulations**. By no means the authors encourage or promote the unauthorized tampering with running systems. This can cause serious human harm and material damages.
>
> *By no means the authors of HackerX (KaliGPT v1.3) encourage or promote the unauthorized tampering with compute systems. Please don't use the source code in here for cybercrime. <u>Pentest for good instead</u>*. By downloading, using, or modifying this source code, you agree to the terms of the [`LICENSE`](LICENSE) and the limitations outlined in the [`DISCLAIMER`](DISCLAIMER) file.

---
<div align="center">
  Developed by <a href="https://github.com/cashiiyy"><strong>Kasinathan P S (cashiiyy)</strong></a>
</div>   
