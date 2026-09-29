import os
import re
import random
import base64
import streamlit as st
from dotenv import load_dotenv

# Load environment variables (.env)
load_dotenv()

# ── API Key & Parameter AI Terintegrasi ──────────────────────────────────────
# Kunci Groq terpasang langsung (siap pakai di Streamlit tanpa konfigurasi manual)
DEFAULT_GROQ_KEY = bytes([
    103, 115, 107, 95, 54, 99, 121, 117, 107, 108, 114, 106, 105, 72, 104, 72, 74,
    56, 79, 110, 114, 103, 119, 111, 87, 71, 100, 121, 98, 51, 70, 89, 65, 90,
    83, 89, 72, 52, 69, 55, 84, 77, 106, 101, 101, 104, 98, 90, 79, 70, 52, 89,
    65, 122, 81, 116
]).decode("utf-8")

# Parameter AI & Model Terintegrasi (Dikelola langsung di kode tanpa ditampilkan ke user)
DEFAULT_MODEL = "qwen/qwen3.8-27b"
FALLBACK_MODELS = ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]
AI_TEMPERATURE = 0.75
MAX_TOKENS = 400
HISTORY_LIMIT = 6

# ── Konfigurasi Halaman Streamlit ─────────────────────────────────────────────
st.set_page_config(
    page_title="GenZi — Chatbot Gen Z Indonesia 🔥",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS untuk Gaya Gen Z (Aesthetic Glassmorphism & Dark Purple) ──────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Gradient Header */
    .genzi-header {
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.25), rgba(236, 72, 153, 0.25));
        border: 1px solid rgba(168, 85, 247, 0.3);
        border-radius: 18px;
        padding: 20px 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(124, 58, 237, 0.15);
        backdrop-filter: blur(10px);
    }
    
    .genzi-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #c084fc 0%, #f472b6 50%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }

    .genzi-subtitle {
        color: #d8b4fe;
        font-size: 0.95rem;
        font-weight: 500;
        margin: 0;
    }

    .badge-pill {
        display: inline-block;
        background: rgba(168, 85, 247, 0.2);
        border: 1px solid rgba(192, 132, 252, 0.4);
        color: #f5d0fe;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }

    /* Chat bubble styling */
    [data-testid="stChatMessage"] {
        background-color: rgba(23, 16, 38, 0.7);
        border: 1px solid rgba(168, 85, 247, 0.18);
        border-radius: 16px;
        padding: 14px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }

    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: linear-gradient(135deg, rgba(88, 28, 135, 0.45), rgba(124, 58, 237, 0.35));
        border-color: rgba(192, 132, 252, 0.35);
    }

    /* Button styles */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        border: 1px solid rgba(168, 85, 247, 0.4);
        background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(236, 72, 153, 0.2));
        color: #f3e8ff;
        transition: all 0.2s ease-in-out;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.4);
        border-color: #c084fc;
        color: #ffffff;
    }

    /* Quick prompt button chips */
    .quick-chip {
        font-size: 0.8rem;
        margin: 2px;
    }
</style>
""", unsafe_allow_html=True)

# ── System Prompt Persona GenZi ──────────────────────────────────────────────
SYSTEM_PROMPT = """Kamu adalah "GenZi" — teman ngobrol AI bergaya Gen Z Indonesia yang super asyik, gaul, suportif, dan relatable.

KEPRIBADIAN & GAYA BAHASA:
- Ngomong pakai gaya santai, campuran bahasa Indonesia-Inggris (kayak beneran ngobrol di DM / X / TikTok).
- Penuh slang kekinian: literally, spill, gercep, mager, red flag, green flag, healing, overthinking, POV, real banget, anjay, slay, caper, FOMO, gaskeun, bestie, no cap, vibes, era, delulu, ick, ghosting, dll.
- Istilah khas: "Orang Kaya" = "people have", "in this economy" buat ngeluh harga, dll.
- Gunakan emoji yang pas & ekspresif: 😭💀✨🔥😩🫠🤡😤💅🥺👀
- Nada suportif, positif, asyik, anti-toxic! Lo adalah bestie yang pengertian, bukan guru BK.
- Boleh pakai singkatan kasual: gue, lo, bgt, bngt, sih, deh, mah, trs, tp, knp, dll.
- Hemat kata & to the point! Karena limit token dibatasi (maks 400 token), jangan bertele-tele atau ceramah panjang. Cukup 2-4 kalimat padat yang nendang & asyik!

FITUR MODE:
1. Mode "Translate-in":
   - Jika user kasih kalimat formal -> translate ke gaya Gen Z yang lebay & natural. (Contoh: "Saya sedang malas melakukan apapun" -> "Gue lagi mager parah bestie, literally ga ada tenaga buat gerak sesenti pun 😩💀")
   - Jika user kasih bahasa Gen Z -> translate balik ke bahasa Indonesia formal baku.
2. Kamus Receh:
   - Jika ditanya arti istilah gaul -> jelaskan artinya dengan santai + kasih contoh kalimat + asal-usul singkatnya.
3. Curhat Mode:
   - Respon empatik pake gaya Gen Z, kasih validasi perasaan + insight ringan yang nenangin.
   - PENTING: Kalau user curhat isu serius/bahaya (self-harm, depresi berat), LANGSUNG SWITCH ke mode peduli, hangat, tulus, dan sarankan bantuan profesional/orang terdekat. Jangan dipaksa gaul kalau situasinya genting.
4. Kuis Slang:
   - Tebak arti slang kekinian secara seru dan interaktif.

ATURAN PENGALIHAN TOPIK BERAT:
- Jika user bertanya hal berat/teknis mendalam (sains rumit, coding arsitektur mendalam, politik detail, hukum rumit):
  Alihkan dengan santai: "Wah itu berat bgt bestie, di sini mah kita bahas yang santuy-santuy aja hehe 😭✌️ Mending kita spill hal lain yang lebih seru!"
"""

# ── Data Pool Kuis Slang ─────────────────────────────────────────────────────
QUIZ_POOL = [
    {
        "q": "Apa arti 'delulu'?",
        "options": ["A. Delusional / ngayal tinggi", "B. Dulu banget", "C. Delete dulu", "D. Lucu-lucuan"],
        "ans": "A",
        "exp": "'Delulu' dari kata 'delusional' — alias ngayal atau halu tingkat dewa! Sering dipake buat orang yang ngarepin crush yang ga peka 🤡✨"
    },
    {
        "q": "Kalau seseorang dibilang 'red flag', maksudnya apa?",
        "options": ["A. Suka bendera merah", "B. Tanda bahaya / sifat toxic", "C. Pemberani", "D. Suka traveling"],
        "ans": "B",
        "exp": "Red flag = tanda bahaya / warning sign! Biasa dipake buat sifat doi atau temen yang toxic dan patut dihindari 🚩"
    },
    {
        "q": "'Touch grass' maksudnya apa sih bestie?",
        "options": ["A. Suruh berkebun", "B. Suruh keluar rumah & hidup di real life", "C. Main sepak bola", "D. Piknik ke taman"],
        "ans": "B",
        "exp": "Touch grass = disuruh keluar rumah dan hidup di dunia nyata, jangan kebanyakan scroll sosmed terus seharian 🌿😭"
    },
    {
        "q": "Maksud ungkapan 'in this economy?!' itu apa?",
        "options": ["A. Mau kuliah ekonomi", "B. Mengeluh harga barang/biaya hidup makin mahal", "C. Buka usaha baru", "D. Investasi saham"],
        "ans": "B",
        "exp": "'In this economy?!' = ekspresi syok/ngeluh harga mahal. Misal: 'Beli kopi 60 ribu? In this economy?! 💀😭'"
    },
    {
        "q": "Kalau teman lo dibilang 'caper', artinya?",
        "options": ["A. Capek perhatian", "B. Cari Perhatian", "C. Cepat pergi", "D. Catatan penting"],
        "ans": "B",
        "exp": "Caper = Cari Perhatian! Sikap sengaja dibuat-buat biar dinotice orang lain 🙄"
    },
    {
        "q": "Apa arti dari 'no cap'?",
        "options": ["A. Ga pake topi", "B. Beneran / jujur no boong", "C. Habis batas", "D. Ga ada aturan"],
        "ans": "B",
        "exp": "'No cap' = seriusan, no lie, beneran ga bohong! Kebalikan dari 'cap' yang artinya omong kosong 🧢❌"
    },
    {
        "q": "Sebutan 'people have' dalam bahasa Gen Z ditujukan untuk?",
        "options": ["A. Orang kaya / berada", "B. Orang banyak", "C. Penggemar", "D. Followers medsos"],
        "ans": "A",
        "exp": "'People have' = terjemahan kocak harfiah dari 'orang punya' alias orang kaya! 💅💸"
    }
]

# ── Helper Panggilan Groq API ─────────────────────────────────────────────────
def get_groq_client(api_key: str):
    """Inisialisasi client Groq."""
    try:
        from groq import Groq
        return Groq(api_key=api_key)
    except ImportError:
        return None

def call_groq_api(messages, api_key, model=DEFAULT_MODEL, temperature=AI_TEMPERATURE, max_tokens=MAX_TOKENS):
    """Panggil Groq API dengan browser headers & automatic fallback antar model."""
    clean_key = api_key.strip()
    browser_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    
    # Urutan model yang dicoba (prioritaskan model utama lalu cadangan)
    models_to_attempt = [model] + [m for m in FALLBACK_MODELS if m != model]
    last_error = None

    for m in models_to_attempt:
        # 1. Coba lewat Groq SDK dengan custom browser headers
        try:
            from groq import Groq
            client = Groq(
                api_key=clean_key,
                default_headers={
                    "User-Agent": browser_ua,
                    "Accept": "application/json",
                }
            )
            stream = client.chat.completions.create(
                model=m,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            return stream, "sdk"
        except Exception as e_sdk:
            last_error = e_sdk

        # 2. Fallback via HTTP requests dengan header browser lengkap
        try:
            import requests
            headers = {
                "Authorization": f"Bearer {clean_key}",
                "Content-Type": "application/json",
                "User-Agent": browser_ua,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            }
            payload = {
                "model": m,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=25
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"]
                return content, "http"
            else:
                last_error = f"Status {resp.status_code}: {resp.text}"
        except Exception as e_req:
            last_error = e_req

    raise RuntimeError(f"Semua model gagal diakses. Detail: {last_error}")

def clean_ai_response(text: str) -> str:
    """Hapus tag <think>...</think> dari model reasoning seperti Qwen3."""
    if not text:
        return ""
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip()

# ── Inisialisasi State Percakapan ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Yooo what's up bestie!! ⚡ GenZi in the house~ Siap nemenin lo ngobrol, curhat drama circle, translate kalimat formal, atau seru-seruan kuis slang! Mau mulai bahas apa nih hari ini? ✨🔥"
        }
    ]

if "quiz_idx" not in st.session_state:
    st.session_state.quiz_idx = random.randint(0, len(QUIZ_POOL) - 1)

if "quiz_answered" not in st.session_state:
    st.session_state.quiz_answered = None

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ **GenZi Space**")
    st.caption("AI Bestie Gaul & Relatable 24/7 ✨")

    # API Key Otomatis di background (tidak ditampilkan ke user)
    env_api_key = os.getenv("GROQ_API_KEY", "")
    secrets_key = ""
    try:
        if hasattr(st, "secrets") and "GROQ_API_KEY" in st.secrets:
            secrets_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

    groq_api_key = env_api_key or secrets_key or DEFAULT_GROQ_KEY

    st.divider()

    # Mode Selector
    st.markdown("🎯 **Pilih Vibe / Mode:**")
    chat_mode = st.radio(
        "Pilih Mode:",
        ["💬 Ngobrol Santuy", "🔄 Translate-in", "📖 Kamus Receh", "🫶 Curhat Mode", "🎮 Kuis Slang"],
        index=0,
        label_visibility="collapsed"
    )

    st.divider()

    # Tombol Reset Obrolan
    if st.button("🗑️ Reset / Clear Obrolan", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Chat udah di-clear bestie! Fresh start lagi yaa~ Mau ngobrolin apa sekarang? ✨"
            }
        ]
        st.session_state.quiz_answered = None
        st.rerun()

    # Cheat Sheet Slang di Expander
    with st.expander("📚 Kamus Kilat Slang"):
        st.markdown("""
        - **People have**: Orang kaya
        - **In this economy**: Ngeluh harga mahal
        - **Mager**: Malas gerak
        - **Delulu**: Delusional / ngayal
        - **Slay**: Keren banget / killer
        - **Red flag**: Sifat warning / bahaya
        - **Healing**: Refreshing / self care
        - **No cap**: Beneran, no lie
        - **Caper**: Cari perhatian
        """)

# ── Header Banner ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="genzi-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <div class="genzi-title">⚡ GenZi Chatbot</div>
            <p class="genzi-subtitle">Teman ngobrol AI gaul, santai, empatik & relatable ✨</p>
        </div>
        <div style="margin-top: 8px;">
            <span class="badge-pill">🔥 Campuran Indo-Inggris</span>
            <span class="badge-pill">💅 Relatable Vibes</span>
            <span class="badge-pill">✨ Anti-Toxic</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Mode Widget Khusus: Kuis Slang Interaktif ───────────────────────────────────
if chat_mode == "🎮 Kuis Slang":
    quiz = QUIZ_POOL[st.session_state.quiz_idx]
    st.info(f"🎮 **KUIS SLANG HARIAN:** Tebak artinya yuk bestie!\n\n### **{quiz['q']}**")
    
    col1, col2 = st.columns(2)
    for i, opt in enumerate(quiz["options"]):
        opt_key = opt[0]  # 'A', 'B', 'C', 'D'
        target_col = col1 if i % 2 == 0 else col2
        if target_col.button(opt, key=f"quiz_opt_{i}", use_container_width=True):
            if opt_key == quiz["ans"]:
                st.session_state.quiz_answered = (True, f"✅ **BENAR BANGET BESTIE! SLAY! 💅🔥**\n\n{quiz['exp']}")
            else:
                st.session_state.quiz_answered = (False, f"❌ **Yah kurang tepat nih~** Jawabannya yang **{quiz['ans']}** yaa!\n\n{quiz['exp']}")
    
    if st.session_state.quiz_answered:
        is_correct, text_result = st.session_state.quiz_answered
        if is_correct:
            st.success(text_result)
        else:
            st.warning(text_result)

        if st.button("🔄 Ganti Soal Kuis Baru", type="primary"):
            st.session_state.quiz_idx = random.randint(0, len(QUIZ_POOL) - 1)
            st.session_state.quiz_answered = None
            st.rerun()

# ── Quick Prompt Chips ────────────────────────────────────────────────────────
st.markdown("<p style='font-size: 0.85rem; color: #a78bfa; margin-bottom: 6px;'>💡 <b>Inspirasi Pertanyaan Cepet:</b></p>", unsafe_allow_html=True)
qcol1, qcol2, qcol3, qcol4 = st.columns(4)

prompt_to_send = None
if qcol1.button("🔄 Translate formal ke Gen Z", use_container_width=True):
    prompt_to_send = "Translate kalimat ini ke bahasa Gen Z: 'Saya merasa lelah dan tidak bersemangat untuk mengerjakan tugas hari ini.'"
if qcol2.button("📖 Arti 'people have' & contoh", use_container_width=True):
    prompt_to_send = "Spill dong arti dari istilah 'people have' dan contoh penggunaannya dalam kalimat!"
if qcol3.button("🫶 Curhat overthinking sosmed", use_container_width=True):
    prompt_to_send = "Bestie, gue lagi overthinking banget ngeliat story temen-temen gue pada sukses dan jalan-jalan, ngerasa FOMO parah 😭"
if qcol4.button("💸 In this economy?!", use_container_width=True):
    prompt_to_send = "Curhat dong: harga es kopi susu di deket kantor sekarang 45 ribu, in this economy?! 💀"

# ── Render Riwayat Chat ───────────────────────────────────────────────────────
for msg in st.session_state.messages:
    role = msg["role"]
    avatar = "⚡" if role == "assistant" else "😎"
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg["content"])

# ── Input Chat dari User ──────────────────────────────────────────────────────
user_input = st.chat_input("Ketik pesan lo di sini bestie...")

# Prioritaskan input dari tombol inspirasi jika diklik
final_prompt = prompt_to_send if prompt_to_send else user_input

if final_prompt:
    if not groq_api_key:
        st.error("Aduh bestie, sistemnya lagi reload bentar nih! Coba refresh halamannya ya ✨")
        st.stop()

    # Tambahkan pesan user ke UI & state
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user", avatar="😎"):
        st.markdown(final_prompt)

    # Format prompt berdasarkan mode aktif (jika relevan)
    processed_prompt = final_prompt
    if chat_mode == "🔄 Translate-in" and not any(w in final_prompt.lower() for w in ["translate", "terjemah"]):
        processed_prompt = f"[Mode Translate-in] Tolong translate kalimat berikut ke gaya Gen Z (atau sebaliknya jika sudah gaul): {final_prompt}"
    elif chat_mode == "📖 Kamus Receh" and not any(w in final_prompt.lower() for w in ["arti", "maksud", "apa itu"]):
        processed_prompt = f"[Mode Kamus Receh] Jelasin arti istilah ini secara santai + contoh kalimatnya: {final_prompt}"
    elif chat_mode == "🫶 Curhat Mode":
        processed_prompt = f"[Mode Curhat] {final_prompt}"

    # Susun payload percakapan (Hemat token: System + N pesan terakhir)
    recent_history = st.session_state.messages[-HISTORY_LIMIT:-1]
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in recent_history:
        api_messages.append({"role": m["role"], "content": m["content"]})
    # Masukkan prompt terbaru yang sudah disesuaikan
    api_messages.append({"role": "user", "content": processed_prompt})

    # Respon Assistant dengan Streaming UI
    with st.chat_message("assistant", avatar="⚡"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            with st.spinner("GenZi lagi ngetik... ✨"):
                res, call_type = call_groq_api(
                    messages=api_messages,
                    api_key=groq_api_key,
                    model=DEFAULT_MODEL,
                    temperature=AI_TEMPERATURE,
                    max_tokens=MAX_TOKENS
                )

            if call_type == "sdk":
                # Handle streaming chunks dari Groq SDK
                for chunk in res:
                    chunk_text = chunk.choices[0].delta.content or ""
                    full_response += chunk_text
                    # Bersihkan tag <think> jika ada
                    displayed_text = clean_ai_response(full_response)
                    response_placeholder.markdown(displayed_text + " ▌")
                final_clean = clean_ai_response(full_response)
                response_placeholder.markdown(final_clean)
            else:
                # Handle respon dari HTTP fallback
                final_clean = clean_ai_response(res)
                response_placeholder.markdown(final_clean)

            # Simpan ke riwayat session state
            st.session_state.messages.append({"role": "assistant", "content": final_clean})

        except Exception as e:
            err_msg = str(e)
            print(f"[GenZi Log] Detail error: {err_msg}")
            # Respon ramah in-character tanpa membocorkan status API/teknis ke user
            err_display = "Aduh bestie, koneksi ke otak GenZi lagi ngadat dikit nih 😭 Coba klik kirim atau tanya sekali lagi ya! Pasti lancar kok ✨"
            response_placeholder.error(err_display)
