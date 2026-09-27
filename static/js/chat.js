/* ═══════════════════════════════════════════════════════════════════════════
   GenZi Chat — Frontend Logic
   ═══════════════════════════════════════════════════════════════════════════ */

// ── State ────────────────────────────────────────────────────────────────────
let currentMode = "chat";
let isLoading = false;

const modeConfig = {
    chat:      { label: "💬 Ngobrol",      placeholder: "Ketik pesan lo di sini bestie..." },
    translate: { label: "🔄 Translate-in",  placeholder: "Tulis kalimat formal atau Gen Z buat di-translate..." },
    kamus:     { label: "📖 Kamus Receh",   placeholder: "Tanya arti slang, misal: artinya apa sih 'red flag'?" },
    curhat:    { label: "🫶 Curhat Mode",   placeholder: "Cerita aja bestie, gue dengerin..." },
    quiz:      { label: "🎮 Kuis Slang",    placeholder: "Ketik jawaban lo (A/B/C/D) atau minta kuis baru..." },
};

// ── DOM Elements ─────────────────────────────────────────────────────────────
const messagesContainer = document.getElementById("messagesContainer");
const messagesWrapper   = document.getElementById("messagesWrapper");
const messageInput      = document.getElementById("messageInput");
const sendBtn           = document.getElementById("sendBtn");
const currentModeEl     = document.getElementById("currentMode");
const statusText        = document.getElementById("statusText");
const quickActions      = document.getElementById("quickActions");

// ── Initialize ───────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    loadWelcomeMessage();
    messageInput.addEventListener("input", () => {
        sendBtn.disabled = messageInput.value.trim().length === 0;
    });
});

// ── Welcome Message ──────────────────────────────────────────────────────────
async function loadWelcomeMessage() {
    showTypingIndicator();
    try {
        const res = await fetch("/api/welcome");
        const data = await res.json();
        removeTypingIndicator();
        appendMessage("bot", data.message);
    } catch (err) {
        removeTypingIndicator();
        appendMessage("bot", "Hai bestie! GenZi di sini~ ada yang bisa gue bantuin? ✨");
    }
}

// ── Send Message ─────────────────────────────────────────────────────────────
async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text || isLoading) return;

    // Prepend mode context
    let fullMessage = text;
    if (currentMode === "translate") {
        if (!text.toLowerCase().includes("translate") && !text.toLowerCase().includes("terjemah")) {
            fullMessage = `Translate ini ke bahasa Gen Z: "${text}"`;
        }
    } else if (currentMode === "kamus") {
        if (!text.toLowerCase().includes("arti") && !text.toLowerCase().includes("maksud") && !text.toLowerCase().includes("apa itu")) {
            fullMessage = `Jelasin dong arti dari: "${text}"`;
        }
    } else if (currentMode === "curhat") {
        // Let it flow naturally, curhat mode is just vibes
    } else if (currentMode === "quiz") {
        // Check if it looks like a quiz answer
        if (/^[a-dA-D]$/i.test(text)) {
            await answerQuiz(text);
            return;
        }
    }

    appendMessage("user", text);
    messageInput.value = "";
    messageInput.style.height = "auto";
    sendBtn.disabled = true;
    hideQuickActions();

    isLoading = true;
    setStatus("GenZi lagi ngetik... ✍️");
    showTypingIndicator();

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: fullMessage }),
        });

        const data = await res.json();
        removeTypingIndicator();

        if (res.ok) {
            appendMessage("bot", data.message);
        } else {
            appendMessage("bot", data.error || "Aduh error nih bestie, coba lagi ya 😭");
        }
    } catch (err) {
        removeTypingIndicator();
        appendMessage("bot", "Yah koneksi lo lagi bermasalah nih bestie 😩 Coba lagi ya!");
    }

    isLoading = false;
    setStatus("Online · siap ngobrol ✨");
}

// ── Answer Quiz ──────────────────────────────────────────────────────────────
async function answerQuiz(answer) {
    appendMessage("user", answer);
    messageInput.value = "";
    sendBtn.disabled = true;

    isLoading = true;
    setStatus("GenZi lagi cek jawaban... 🤔");
    showTypingIndicator();

    try {
        const res = await fetch("/api/quiz/answer", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ answer }),
        });

        const data = await res.json();
        removeTypingIndicator();
        appendMessage("bot", data.message);
    } catch (err) {
        removeTypingIndicator();
        appendMessage("bot", "Gagal cek jawaban nih 😭 Coba lagi ya bestie!");
    }

    isLoading = false;
    setStatus("Online · siap ngobrol ✨");
}

// ── Quick Message ────────────────────────────────────────────────────────────
function sendQuickMessage(text) {
    messageInput.value = text;
    sendBtn.disabled = false;
    sendMessage();
}

// ── Request New Quiz ─────────────────────────────────────────────────────────
async function requestQuiz() {
    isLoading = true;
    setStatus("GenZi lagi siapin kuis... 🎮");
    showTypingIndicator();

    try {
        const res = await fetch("/api/quiz");
        const data = await res.json();
        removeTypingIndicator();
        appendMessage("bot", data.message);
    } catch (err) {
        removeTypingIndicator();
        appendMessage("bot", "Gagal ambil kuis nih 😭");
    }

    isLoading = false;
    setStatus("Online · siap ngobrol ✨");
}

// ── Append Message ───────────────────────────────────────────────────────────
function appendMessage(role, text) {
    const messageEl = document.createElement("div");
    messageEl.className = `message ${role}`;

    const avatar = role === "bot" ? "⚡" : "👤";
    const formattedText = formatMessage(text);

    messageEl.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-bubble">${formattedText}</div>
    `;

    messagesWrapper.appendChild(messageEl);
    scrollToBottom();
}

// ── Format Message (basic markdown) ──────────────────────────────────────────
function formatMessage(text) {
    // Escape HTML
    let formatted = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");

    // Bold: **text**
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

    // Italic: *text*
    formatted = formatted.replace(/\*(.*?)\*/g, "<em>$1</em>");

    // Inline code: `text`
    formatted = formatted.replace(/`(.*?)`/g, "<code style='background:rgba(124,58,237,0.2);padding:2px 6px;border-radius:4px;font-size:13px;'>$1</code>");

    // Line breaks
    formatted = formatted.replace(/\n\n/g, "</p><p>");
    formatted = formatted.replace(/\n/g, "<br>");

    return `<p>${formatted}</p>`;
}

// ── Typing Indicator ─────────────────────────────────────────────────────────
function showTypingIndicator() {
    const typingEl = document.createElement("div");
    typingEl.className = "message bot";
    typingEl.id = "typingIndicator";
    typingEl.innerHTML = `
        <div class="message-avatar">⚡</div>
        <div class="message-bubble">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;
    messagesWrapper.appendChild(typingEl);
    scrollToBottom();
}

function removeTypingIndicator() {
    const el = document.getElementById("typingIndicator");
    if (el) el.remove();
}

// ── Scroll ───────────────────────────────────────────────────────────────────
function scrollToBottom() {
    requestAnimationFrame(() => {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    });
}

// ── Switch Mode ──────────────────────────────────────────────────────────────
function switchMode(mode) {
    currentMode = mode;
    const config = modeConfig[mode];

    // Update UI
    currentModeEl.textContent = config.label;
    messageInput.placeholder = config.placeholder;

    // Update active nav
    document.querySelectorAll(".nav-btn").forEach(btn => {
        btn.classList.toggle("active", btn.dataset.mode === mode);
    });

    // Show/hide quick actions
    quickActions.style.display = mode === "chat" ? "flex" : "none";

    // If quiz mode, offer a quiz
    if (mode === "quiz") {
        requestQuiz();
    }

    // Close mobile sidebar
    closeSidebar();
    messageInput.focus();
}

// ── Sidebar Toggle ───────────────────────────────────────────────────────────
function toggleSidebar() {
    const sidebar = document.querySelector(".sidebar");
    const overlay = document.getElementById("sidebarOverlay");
    sidebar.classList.toggle("open");
    overlay.classList.toggle("show");
}

function closeSidebar() {
    const sidebar = document.querySelector(".sidebar");
    const overlay = document.getElementById("sidebarOverlay");
    sidebar.classList.remove("open");
    overlay.classList.remove("show");
}

// ── Quick Actions ────────────────────────────────────────────────────────────
function hideQuickActions() {
    quickActions.style.display = "none";
}

// ── Clear Chat ───────────────────────────────────────────────────────────────
async function clearChat() {
    try {
        await fetch("/api/clear", { method: "POST" });
    } catch (e) {
        // silent
    }
    messagesWrapper.innerHTML = "";
    quickActions.style.display = "flex";
    closeSidebar();
    loadWelcomeMessage();
}

// ── Status ───────────────────────────────────────────────────────────────────
function setStatus(text) {
    statusText.textContent = text;
}

// ── Input Handling ───────────────────────────────────────────────────────────
function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

function autoResize(el) {
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 120) + "px";
}
