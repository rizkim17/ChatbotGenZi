# ⚡ ChatbotGenZi — AI Bestie Bergaya Gen Z Indonesia 🔥

Chatbot berbasis **Streamlit** dengan persona khas **Gen Z Indonesia**: santai, campuran Indo-Inggris, penuh slang viral (*literally, spill, gercep, mager, red flag, healing, overthinking, POV, real banget, people have, in this economy*), empatik, suportif, dan anti-toxic.

Ditenagai oleh model **Qwen** via **Groq Cloud API** dengan optimasi hemat kuota (maksimal 400 token & limit memory context).

---

## ✨ Fitur Utama

1. **💬 Ngobrol Santuy**: Ngobrol bebas seputar lifestyle, hiburan (series, musik, TikTok, meme), circle pertemanan, dan motivasi harian. Topik berat/teknis mendalam dialihkan dengan santuy.
2. **🔄 Mode Translate-in**:
   - Terjemahkan kalimat formal kaku ke bahasa Gen Z yang ekspresif.
   - Terjemahkan bahasa gaul Gen Z ke bahasa Indonesia baku formal.
3. **📖 Kamus Receh**: Jelasin arti istilah gaul (*red flag, no cap, delulu, people have, dll*) lengkap dengan contoh kalimat dan asal-usulnya.
4. **🫶 Curhat Mode**: Validasi perasaan, empatik, no judging. *Catatan:* otomatis switch ke mode serius & peduli jika mendeteksi isu genting/kesehatan mental berat.
5. **🎮 Kuis Slang Harian**: Mini game tebak arti slang interaktif langsung di web.

---

## ⚙️ Optimasi Limit Groq Gratis & Konfigurasi

- **🔑 Groq API Key Terintegrasi**: API Key sudah langsung terpasang di sistem (zero configuration), sehingga ketika dijalankan di Streamlit lokal maupun cloud bisa langsung dipakai tanpa perlu input manual. (Tetap mendukung custom key via file `.env` atau sidebar jika ingin ganti).
- **🪙 Batas Token Output**: Maksimal **400 tokens** per respons agar hemat dan aman dari batas *Tokens Per Minute (TPM)* di akun gratis.
- **🌡️ Temperature (Fixed di Kode)**: Disetel permanen di kode pada **0.75** (kreatif & luwes untuk gaya bahasa gaul Gen Z, namun tetap konsisten dan tidak perlu repot diatur manual di UI).
- **🧠 Window History**: Membatasi riwayat percakapan yang dikirim ke API agar kuota token input tetap efisien.

---

## 🚀 Cara Menjalankan (Streamlit)

### 1. Clone & Masuk ke Folder
```bash
git clone https://github.com/rizkim17/ChatbotGenZi.git
cd ChatbotGenZi
```

### 2. Buat & Aktifkan Virtual Environment (Opsional)
```bash
python -m venv venv
# Di Windows:
venv\Scripts\activate
# Di Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependensi
```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi Langsung
```bash
streamlit run app.py
```
Aplikasi akan otomatis terbuka di browser kamu di `http://localhost:8501` dan **langsung bisa dipakai ngobrol tanpa perlu setup apa-apa lagi!** ✨

---

## 🎨 Tampilan & Tema
- **Tema**: *Glassmorphism Dark Purple / Neon Violet & Pink* (`.streamlit/config.toml` & custom CSS).
- **Interactive Widgets**: Quick prompts inspirasi, quiz selector button, dan streaming chat avatar.

---

## 📦 Tech Stack
- [Streamlit](https://streamlit.io/) (Frontend & UI Interactive)
- [Groq SDK](https://console.groq.com/) (Ultra-fast LLM Inference)
- Model: `qwen/qwen3.8-27b` / `qwen/qwen3-14b`
- Python 3.10+
