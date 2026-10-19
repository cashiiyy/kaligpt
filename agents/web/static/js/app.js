// KaliGPT Dynamic Web View // HackerX Client Application
// Dynamic Windowing Engine, Security Tools Runner, & Full Markdown Suite

document.addEventListener("DOMContentLoaded", () => {
    // --- Application State ---
    let currentConfig = null;
    let chatHistory = [];
    let isProcessing = false;
    let highestZIndex = 50;

    // --- DOM Elements ---
    const chatFeed = document.getElementById("chatFeed");
    const userPrompt = document.getElementById("userPrompt");
    const btnSend = document.getElementById("btnSend");
    const providerSelect = document.getElementById("providerSelect");
    const modelSelect = document.getElementById("modelSelect");
    const presetSelect = document.getElementById("presetSelect");
    const btnClearChat = document.getElementById("btnClearChat");
    const btnExportChat = document.getElementById("btnExportChat");
    const dockActiveBadge = document.getElementById("dockActiveBadge");
    const toastHub = document.getElementById("toastHub");
    const taskbarClock = document.getElementById("taskbarClock");

    // Telemetry Elements
    const statProvider = document.getElementById("statProvider");
    const statModel = document.getElementById("statModel");
    const statKeyStatus = document.getElementById("statKeyStatus");
    const statTools = document.getElementById("statTools");
    const statPlatform = document.getElementById("statPlatform");

    // Tool Execution Elements
    const toolSelect = document.getElementById("toolSelect");
    const toolDescription = document.getElementById("toolDescription");
    const toolParamsInput = document.getElementById("toolParamsInput");
    const btnRunTool = document.getElementById("btnRunTool");
    const toolResultBox = document.getElementById("toolResultBox");
    const toolResultPre = document.getElementById("toolResultPre");
    const btnCopyToolResult = document.getElementById("btnCopyToolResult");

    // Configuration Vault Elements
    const cfgVendor = document.getElementById("cfgVendor");
    const cfgKey = document.getElementById("cfgKey");
    const btnSaveConfig = document.getElementById("btnSaveConfig");
    const cfgMessage = document.getElementById("cfgMessage");

    // --- Toast Notifications ---
    function showToast(message, duration = 3000) {
        if (!toastHub) return;
        const toast = document.createElement("div");
        toast.className = "cyber-toast";
        toast.textContent = message;
        toastHub.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = "0";
            toast.style.transform = "translateY(8px)";
            toast.style.transition = "all 0.3s ease";
            setTimeout(() => toast.remove(), 300);
        }, duration);
    }

    // --- Live Taskbar Clock ---
    function updateClock() {
        if (!taskbarClock) return;
        const now = new Date();
        taskbarClock.textContent = now.toLocaleTimeString([], { hour12: false });
    }
    setInterval(updateClock, 1000);
    updateClock();

    // --- Theme Switcher ---
    const themeDots = document.querySelectorAll(".theme-dot");
    const savedTheme = localStorage.getItem("kaligpt_theme") || "emerald";
    setTheme(savedTheme);

    themeDots.forEach(dot => {
        dot.addEventListener("click", () => {
            const theme = dot.getAttribute("data-theme");
            setTheme(theme);
        });
    });

    function setTheme(theme) {
        document.documentElement.setAttribute("data-theme", theme);
        localStorage.setItem("kaligpt_theme", theme);
        themeDots.forEach(d => {
            if (d.getAttribute("data-theme") === theme) {
                d.classList.add("active");
            } else {
                d.classList.remove("active");
            }
        });
    }

    // ==========================================
    // --- DYNAMIC WINDOWING ENGINE ---
    // ==========================================

    const windows = document.querySelectorAll(".cyber-window");
    const taskbarItems = document.querySelectorAll(".taskbar-item");

    function focusWindow(win) {
        if (!win || win.classList.contains("hidden")) return;
        highestZIndex += 1;
        win.style.zIndex = highestZIndex;
        windows.forEach(w => w.classList.remove("win-focused"));
        win.classList.add("win-focused");

        // Sync taskbar active glow
        taskbarItems.forEach(item => {
            if (item.getAttribute("data-window") === win.id) {
                item.classList.add("active");
            }
        });
    }

    function toggleWindow(winId) {
        const win = document.getElementById(winId);
        if (!win) return;
        if (win.classList.contains("hidden")) {
            win.classList.remove("hidden");
            focusWindow(win);
        } else if (win.classList.contains("win-focused")) {
            win.classList.add("hidden");
            syncTaskbar(winId, false);
        } else {
            focusWindow(win);
        }
    }

    function syncTaskbar(winId, isActive) {
        taskbarItems.forEach(item => {
            if (item.getAttribute("data-window") === winId) {
                if (isActive) item.classList.add("active");
                else item.classList.remove("active");
            }
        });
    }

    // Taskbar clicks
    taskbarItems.forEach(item => {
        item.addEventListener("click", () => {
            const winId = item.getAttribute("data-window");
            toggleWindow(winId);
        });
    });

    // Window Drag & Control Buttons
    windows.forEach(win => {
        // Bring to front on click
        win.addEventListener("mousedown", () => focusWindow(win));

        const header = win.querySelector(".window-header");
        const btnMin = win.querySelector(".btn-minimize");
        const btnMax = win.querySelector(".btn-maximize");
        const btnClose = win.querySelector(".btn-close");

        if (btnMin) {
            btnMin.addEventListener("click", (e) => {
                e.stopPropagation();
                win.classList.add("hidden");
                syncTaskbar(win.id, false);
            });
        }

        if (btnMax) {
            btnMax.addEventListener("click", (e) => {
                e.stopPropagation();
                win.classList.toggle("win-maximized");
                focusWindow(win);
            });
        }

        if (btnClose) {
            btnClose.addEventListener("click", (e) => {
                e.stopPropagation();
                win.classList.add("hidden");
                syncTaskbar(win.id, false);
            });
        }

        // Draggable Logic
        if (header) {
            let isDragging = false;
            let startX, startY, origLeft, origTop;

            header.addEventListener("mousedown", (e) => {
                if (win.classList.contains("win-maximized")) return;
                isDragging = true;
                focusWindow(win);

                startX = e.clientX;
                startY = e.clientY;

                const rect = win.getBoundingClientRect();
                origLeft = rect.left;
                origTop = rect.top;

                document.body.style.userSelect = "none";

                function onMouseMove(moveEvent) {
                    if (!isDragging) return;
                    const dx = moveEvent.clientX - startX;
                    const dy = moveEvent.clientY - startY;
                    win.style.left = `${Math.max(10, origLeft + dx)}px`;
                    win.style.top = `${Math.max(10, origTop + dy)}px`;
                    win.style.right = "auto";
                    win.style.bottom = "auto";
                }

                function onMouseUp() {
                    isDragging = false;
                    document.body.style.userSelect = "";
                    document.removeEventListener("mousemove", onMouseMove);
                    document.removeEventListener("mouseup", onMouseUp);
                }

                document.addEventListener("mousemove", onMouseMove);
                document.addEventListener("mouseup", onMouseUp);
            });
        }
    });

    // Default focus
    const chatWin = document.getElementById("winChat");
    if (chatWin) focusWindow(chatWin);

    // ==========================================
    // --- LOAD CONFIG & TELEMETRY ---
    // ==========================================

    async function loadConfig() {
        try {
            const res = await fetch("/api/config");
            const data = await res.json();
            currentConfig = data;

            if (providerSelect) {
                providerSelect.value = data.default_provider || "ollama";
                updateModelDropdown(data.default_provider);
            }
            updateStatusDisplay();
        } catch (err) {
            console.error("Config load error:", err);
            if (statKeyStatus) {
                statKeyStatus.innerHTML = '<span class="pulse-dot" style="background:#ff3366;"></span> Offline';
            }
        }
    }

    function updateModelDropdown(provider) {
        if (!currentConfig || !modelSelect) return;
        modelSelect.innerHTML = "";
        const providerData = currentConfig[provider] || {};
        const models = providerData.models || [];
        const activeModel = providerData.default_model || "";

        models.forEach(m => {
            const opt = document.createElement("option");
            opt.value = m;
            opt.textContent = m;
            if (m === activeModel) opt.selected = true;
            modelSelect.appendChild(opt);
        });

        if (models.length === 0) {
            const opt = document.createElement("option");
            opt.value = "default";
            opt.textContent = "default";
            modelSelect.appendChild(opt);
        }

        updateStatusDisplay();
    }

    function updateStatusDisplay() {
        if (!providerSelect || !modelSelect) return;
        const prov = providerSelect.value;
        const mod = modelSelect.value;

        if (statProvider) statProvider.textContent = prov.toUpperCase();
        if (statModel) statModel.textContent = mod;
        if (dockActiveBadge) dockActiveBadge.textContent = `${prov.toUpperCase()} // ${mod}`;

        if (currentConfig && currentConfig[prov] && statKeyStatus) {
            const key = currentConfig[prov].api_key || "";
            if (prov === "ollama") {
                statKeyStatus.innerHTML = `<span class="pulse-dot"></span> ${key || "localhost:11434"}`;
            } else if (key && !key.startsWith("YOUR_")) {
                statKeyStatus.innerHTML = `<span class="pulse-dot"></span> Configured`;
            } else {
                statKeyStatus.innerHTML = `<span class="pulse-dot" style="background:#ff3366;"></span> Key Missing`;
            }
        }
    }

    if (providerSelect) {
        providerSelect.addEventListener("change", async () => {
            const prov = providerSelect.value;
            updateModelDropdown(prov);
            await saveProviderModel(prov, modelSelect.value);
        });
    }

    if (modelSelect) {
        modelSelect.addEventListener("change", async () => {
            await saveProviderModel(providerSelect.value, modelSelect.value);
        });
    }

    async function saveProviderModel(provider, model) {
        try {
            await fetch("/api/config/update", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ provider, model })
            });
            updateStatusDisplay();
        } catch (err) {
            console.error("Failed to update config:", err);
        }
    }

    // ==========================================
    // --- FULL MARKDOWN RENDERING & CODE COPY ---
    // ==========================================

    function escapeHtml(text) {
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
    }

    function renderMarkdown(rawText) {
        if (!rawText) return "";

        let html = "";
        if (window.marked) {
            try {
                html = marked.parse(rawText);
            } catch (e) {
                console.warn("marked error, falling back:", e);
                html = fallbackMarkdown(rawText);
            }
        } else {
            html = fallbackMarkdown(rawText);
        }

        const tempDiv = document.createElement("div");
        tempDiv.innerHTML = html;

        // Code block formatting with language tag & copy button
        tempDiv.querySelectorAll("pre code").forEach(codeBlock => {
            const pre = codeBlock.parentElement;
            const classes = codeBlock.className || "";
            const match = classes.match(/language-(\w+)/);
            const lang = match ? match[1] : "code";

            const wrapper = document.createElement("div");
            wrapper.className = "code-block-wrapper";

            const header = document.createElement("div");
            header.className = "code-block-header";
            header.innerHTML = `
                <span>${lang.toUpperCase()}</span>
                <button class="btn-copy-code" title="Copy code snippet">Copy</button>
            `;

            if (window.hljs) {
                try {
                    hljs.highlightElement(codeBlock);
                } catch (_) {}
            }

            pre.parentNode.insertBefore(wrapper, pre);
            wrapper.appendChild(header);
            wrapper.appendChild(pre);

            const copyBtn = header.querySelector(".btn-copy-code");
            copyBtn.addEventListener("click", () => {
                navigator.clipboard.writeText(codeBlock.innerText).then(() => {
                    copyBtn.textContent = "Copied!";
                    copyBtn.style.color = "var(--accent)";
                    showToast("Code copied to clipboard!");
                    setTimeout(() => {
                        copyBtn.textContent = "Copy";
                        copyBtn.style.color = "";
                    }, 2000);
                });
            });
        });

        return tempDiv.innerHTML;
    }

    function fallbackMarkdown(text) {
        const esc = escapeHtml(text);
        return esc
            .replace(/```([a-zA-Z0-9_\-\.]*)\n([\s\S]*?)```/g, '<pre><code class="language-$1">$2</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
            .replace(/\*([^*]+)\*/g, '<em>$1</em>')
            .replace(/^### (.*$)/gim, '<h4>$1</h4>')
            .replace(/^## (.*$)/gim, '<h3>$1</h3>')
            .replace(/^# (.*$)/gim, '<h2>$1</h2>')
            .replace(/\n\n+/g, '</p><p>')
            .replace(/\n/g, '<br>');
    }

    // ==========================================
    // --- CHAT MESSAGE DISPATCH & FEED ---
    // ==========================================

    function appendMessage(role, content, thinking = null, toolCalls = []) {
        if (!chatFeed) return;
        const chatRow = document.createElement("div");
        chatRow.className = `chat-row ${role}`;

        const shell = document.createElement("div");
        shell.className = "bubble-shell";

        // Header
        const header = document.createElement("div");
        header.className = "bubble-header";
        const speaker = document.createElement("span");
        speaker.className = "speaker-tag";
        speaker.textContent = role === "user" ? "┌──(operator㉿kaligpt)-[~/cyber]" : "🛡️ KALIGPT // AGENT";
        const time = document.createElement("span");
        time.className = "speaker-time";
        time.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        header.appendChild(speaker);
        header.appendChild(time);
        shell.appendChild(header);

        // Thought / Reasoning Collapsible
        if (thinking && thinking.trim().length > 0) {
            const thoughtCard = document.createElement("div");
            thoughtCard.className = "thought-trace-card";

            const thoughtHead = document.createElement("div");
            thoughtHead.className = "thought-header";
            thoughtHead.innerHTML = `
                <span>🧠 <strong>REASONING & THOUGHT TRACE</strong></span>
                <span style="font-size: 0.7rem; opacity: 0.8;">[Click to Expand]</span>
            `;

            const thoughtBody = document.createElement("div");
            thoughtBody.className = "thought-body";
            thoughtBody.textContent = thinking;
            thoughtBody.style.display = "none";

            thoughtHead.addEventListener("click", () => {
                const isHidden = thoughtBody.style.display === "none";
                thoughtBody.style.display = isHidden ? "block" : "none";
                thoughtHead.querySelector("span:last-child").textContent = isHidden ? "[Collapse]" : "[Click to Expand]";
            });

            thoughtCard.appendChild(thoughtHead);
            thoughtCard.appendChild(thoughtBody);
            shell.appendChild(thoughtCard);
        }

        // Tool Calls
        if (toolCalls && toolCalls.length > 0) {
            toolCalls.forEach(tc => {
                const toolCard = document.createElement("div");
                toolCard.className = "tool-execution-badge";
                toolCard.innerHTML = `
                    <div class="tool-badge-head">
                        <span>⚡ TOOL EXECUTED: ${tc.name}</span>
                        <span>SUCCESS</span>
                    </div>
                    <div class="tool-badge-body">
                        <div><strong>Args:</strong> ${JSON.stringify(tc.args)}</div>
                        <div><strong>Result:</strong> ${String(tc.result)}</div>
                    </div>
                `;
                shell.appendChild(toolCard);
            });
        }

        // Markdown Body
        const mdBody = document.createElement("div");
        mdBody.className = "markdown-body";
        if (role === "user") {
            mdBody.innerHTML = `<span style="color:var(--accent); font-family:var(--font-mono); font-weight:700;">└─$ </span>${escapeHtml(content)}`;
        } else {
            mdBody.innerHTML = renderMarkdown(content);
        }
        shell.appendChild(mdBody);

        chatRow.appendChild(shell);
        chatFeed.appendChild(chatRow);
        chatFeed.scrollTop = chatFeed.scrollHeight;
    }

    async function sendMessage() {
        const prompt = userPrompt.value.trim();
        if (!prompt || isProcessing) return;

        isProcessing = true;
        if (btnSend) btnSend.disabled = true;
        userPrompt.value = "";
        userPrompt.style.height = "auto";

        appendMessage("user", prompt);
        chatHistory.push({ role: "user", content: prompt });

        // Typing indicator
        const typingRow = document.createElement("div");
        typingRow.className = "chat-row assistant";
        typingRow.id = "typingRow";
        typingRow.innerHTML = `
            <div class="bubble-shell">
                <div class="bubble-header">
                    <span class="speaker-tag" style="color:var(--accent);">🛡️ KALIGPT // AGENT</span>
                    <span>evaluating...</span>
                </div>
                <div style="display:flex; align-items:center; gap:8px; font-family:var(--font-mono); font-size:0.8rem; color:var(--cyan);">
                    <span class="pulse-dot" style="display:inline-block;"></span> Synthesizing cyber intelligence & evaluating tools...
                </div>
            </div>
        `;
        chatFeed.appendChild(typingRow);
        chatFeed.scrollTop = chatFeed.scrollHeight;

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    prompt: prompt,
                    provider: providerSelect ? providerSelect.value : "ollama",
                    model: modelSelect ? modelSelect.value : "default",
                    preset: presetSelect ? presetSelect.value : "web_bounty",
                    history: chatHistory.slice(-8)
                })
            });

            const data = await res.json();
            typingRow.remove();

            if (data.success) {
                appendMessage("assistant", data.response, data.thinking, data.tool_calls || []);
                chatHistory.push({ role: "assistant", content: data.response });
            } else {
                appendMessage("assistant", `### ⚠️ Execution Notice\n\n**Error:** ${data.error || "Execution failed."}\n\n*Check provider connectivity or API credentials in Config.*`);
            }
        } catch (err) {
            typingRow.remove();
            appendMessage("assistant", `### 🛑 Connection Failed\n\nUnable to reach KaliGPT backend: \`${err.message}\``);
        } finally {
            isProcessing = false;
            if (btnSend) btnSend.disabled = false;
            userPrompt.focus();
        }
    }

    if (btnSend) btnSend.addEventListener("click", sendMessage);

    if (userPrompt) {
        userPrompt.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        userPrompt.addEventListener("input", () => {
            userPrompt.style.height = "auto";
            userPrompt.style.height = Math.min(userPrompt.scrollHeight, 140) + "px";
        });
    }

    // Clear Chat
    if (btnClearChat) {
        btnClearChat.addEventListener("click", () => {
            chatHistory = [];
            const hero = document.getElementById("heroBanner");
            chatFeed.innerHTML = "";
            if (hero) chatFeed.appendChild(hero);
            showToast("Chat conversation cleared");
        });
    }

    // Export Chat to Markdown
    if (btnExportChat) {
        btnExportChat.addEventListener("click", () => {
            if (chatHistory.length === 0) {
                showToast("No conversation to export.");
                return;
            }

            let exportText = `# KaliGPT Session Log\n**Date:** ${new Date().toISOString()}\n**Provider:** ${providerSelect ? providerSelect.value : "ollama"} (${modelSelect ? modelSelect.value : "default"})\n\n---\n\n`;
            chatHistory.forEach(msg => {
                const label = msg.role === "user" ? "### 👤 OPERATOR" : "### 🛡️ KALIGPT AGENT";
                exportText += `${label}\n\n${msg.content}\n\n---\n\n`;
            });

            const blob = new Blob([exportText], { type: "text/markdown;charset=utf-8" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `kaligpt-session-${Date.now()}.md`;
            a.click();
            URL.revokeObjectURL(a);
            showToast("Session log exported!");
        });
    }

    // Quick Vector Chips (support both .hacker-chip and .vector-chip)
    document.querySelectorAll(".hacker-chip, .vector-chip").forEach(chip => {
        chip.addEventListener("click", () => {
            const prompt = chip.getAttribute("data-prompt");
            if (userPrompt) {
                userPrompt.value = prompt;
                userPrompt.focus();
                userPrompt.style.height = "auto";
                userPrompt.style.height = userPrompt.scrollHeight + "px";
            }
            const winChat = document.getElementById("winChat");
            if (winChat) {
                winChat.classList.remove("hidden");
                focusWindow(winChat);
            }
            showToast("Vector prompt loaded");
        });
    });

    // ==========================================
    // --- SECURITY TOOLS RUNNER WINDOW ---
    // ==========================================

    let toolsCatalog = {};

    async function loadTools() {
        try {
            const res = await fetch("/api/tools");
            toolsCatalog = await res.json();
            if (toolSelect) {
                toolSelect.innerHTML = "";
                Object.keys(toolsCatalog).forEach(name => {
                    const opt = document.createElement("option");
                    opt.value = name;
                    opt.textContent = name;
                    toolSelect.appendChild(opt);
                });

                if (toolSelect.options.length > 0) {
                    onToolChange();
                }
            }
        } catch (err) {
            console.error("Tools load error:", err);
        }
    }

    function onToolChange() {
        if (!toolSelect) return;
        const name = toolSelect.value;
        if (toolDescription) {
            toolDescription.textContent = toolsCatalog[name] || "No description available.";
        }

        if (toolParamsInput) {
            if (name === "keyword_search" || name === "search_as_RAG") {
                toolParamsInput.value = JSON.stringify({ query: "CVE-2024-6387", limit: 3 }, null, 2);
            } else if (name === "execute_generic_linux_command") {
                toolParamsInput.value = JSON.stringify({ command: "whoami" }, null, 2);
            } else if (name === "web_request_analysis" || name === "get_raw_response") {
                toolParamsInput.value = JSON.stringify({ url: "https://httpbin.org/get" }, null, 2);
            } else {
                toolParamsInput.value = "{}";
            }
        }
    }

    if (toolSelect) toolSelect.addEventListener("change", onToolChange);

    // Sidebar & Telemetry tool clicks
    document.querySelectorAll(".tool-entry, .tool-pill").forEach(pill => {
        pill.addEventListener("click", () => {
            const toolName = pill.getAttribute("data-tool");
            const winTools = document.getElementById("winTools");
            if (winTools) {
                winTools.classList.remove("hidden");
                focusWindow(winTools);
                syncTaskbar("winTools", true);
            }
            if (toolSelect && toolSelect.querySelector(`option[value="${toolName}"]`)) {
                toolSelect.value = toolName;
                onToolChange();
            }
        });
    });

    // Execute Tool Button
    if (btnRunTool) {
        btnRunTool.addEventListener("click", async () => {
            const name = toolSelect.value;
            let params = {};
            try {
                params = JSON.parse(toolParamsInput.value || "{}");
            } catch (e) {
                alert("Parameters must be valid JSON format");
                return;
            }

            btnRunTool.disabled = true;
            btnRunTool.innerHTML = '<span class="pulse-dot"></span> Executing...';

            try {
                const res = await fetch("/api/tools/execute", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ tool: name, args: params })
                });
                const data = await res.json();
                if (toolResultBox) toolResultBox.classList.remove("hidden");
                const output = typeof data.result === "object" ? JSON.stringify(data.result, null, 2) : String(data.result);
                if (toolResultPre) {
                    toolResultPre.textContent = output;
                    if (window.hljs) hljs.highlightElement(toolResultPre);
                }
            } catch (err) {
                if (toolResultBox) toolResultBox.classList.remove("hidden");
                if (toolResultPre) toolResultPre.textContent = `Execution Error: ${err.message}`;
            } finally {
                btnRunTool.disabled = false;
                btnRunTool.innerHTML = '<span class="btn-glyph">▶</span> EXECUTE SECURITY TOOL';
            }
        });
    }

    if (btnCopyToolResult) {
        btnCopyToolResult.addEventListener("click", () => {
            if (!toolResultPre) return;
            navigator.clipboard.writeText(toolResultPre.innerText).then(() => {
                btnCopyToolResult.textContent = "Copied!";
                setTimeout(() => btnCopyToolResult.textContent = "Copy", 2000);
                showToast("Tool output copied!");
            });
        });
    }

    // ==========================================
    // --- CONFIGURATION VAULT WINDOW ---
    // ==========================================

    if (cfgVendor) {
        cfgVendor.addEventListener("change", () => {
            const v = cfgVendor.value;
            if (currentConfig && currentConfig[v] && cfgKey) {
                cfgKey.value = currentConfig[v].api_key || "";
            }
        });
    }

    if (btnSaveConfig) {
        btnSaveConfig.addEventListener("click", async () => {
            const vendor = cfgVendor.value;
            const key = cfgKey.value.trim();

            btnSaveConfig.disabled = true;
            try {
                const res = await fetch("/api/config/key", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ vendor, key })
                });
                const data = await res.json();
                if (data.success) {
                    if (cfgMessage) {
                        cfgMessage.textContent = "[✓] Configuration credentials saved.";
                        cfgMessage.className = "modal-alert text-green";
                        cfgMessage.classList.remove("hidden");
                    }
                    showToast("Credentials saved!");
                    await loadConfig();
                } else {
                    if (cfgMessage) {
                        cfgMessage.textContent = `[!] Error: ${data.error}`;
                        cfgMessage.className = "modal-alert text-red";
                        cfgMessage.classList.remove("hidden");
                    }
                }
            } catch (err) {
                if (cfgMessage) {
                    cfgMessage.textContent = `[!] Network Error: ${err.message}`;
                    cfgMessage.className = "modal-alert text-red";
                    cfgMessage.classList.remove("hidden");
                }
            } finally {
                btnSaveConfig.disabled = false;
            }
        });
    }

    // Initialize
    loadConfig();
    loadTools();
});
