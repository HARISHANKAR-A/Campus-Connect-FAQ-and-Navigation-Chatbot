import hashlib
import webbrowser

import streamlit as st

from campusconnect import config as C
from campusconnect.asr import transcribe
from campusconnect.nlp import Brain, detect_text_lang
from campusconnect.tts import speak

st.set_page_config(page_title="Campus Connect | VIT Vellore", page_icon="🎓", layout="wide")

st.markdown(
    """
<style>
.block-container{padding-top:1.2rem;max-width:980px}
.hero{background:linear-gradient(120deg,#0b2a5b 0%,#1d5fd1 100%);color:#fff;padding:22px 28px;
      border-radius:18px;margin-bottom:14px;box-shadow:0 8px 24px rgba(11,42,91,.28)}
.hero .brand{font-size:.8rem;letter-spacing:.14em;text-transform:uppercase;opacity:.8}
.hero h1{margin:2px 0 0;font-size:1.65rem;font-weight:700;color:#fff;line-height:1.25}
.hero p{margin:6px 0 0;opacity:.92;font-size:.93rem}
.hero .chips span{display:inline-block;background:rgba(255,255,255,.16);border-radius:999px;
      padding:3px 13px;margin:12px 6px 0 0;font-size:.8rem}
[data-testid="stChatMessage"]{background:#fff;border:1px solid #e3e9f3;border-radius:16px;
      padding:12px 18px;margin-bottom:10px;box-shadow:0 2px 8px rgba(20,33,61,.05)}
.meta{font-size:.74rem;color:#6b7a99;margin-top:4px}
.warn{font-size:.74rem;color:#9a6700;margin-top:2px}
section[data-testid="stSidebar"]{background:#0b2a5b}
section[data-testid="stSidebar"] *{color:#eaf0fb}
section[data-testid="stSidebar"] .stButton>button{background:rgba(255,255,255,.1);
      border:1px solid rgba(255,255,255,.25);color:#fff;border-radius:10px;text-align:left}
section[data-testid="stSidebar"] .stButton>button:hover{background:rgba(255,255,255,.22)}
</style>
<div class="hero">
  <div class="brand">VIT Vellore · Virtual Campus Assistant</div>
  <h1>CampusConnect: Intelligent College FAQ and Navigation Chatbot</h1>
  <p>Speak or type your question. Get answers in your language and one-tap campus directions.</p>
  <div class="chips"><span>English</span><span>தமிழ்</span><span>తెలుగు</span><span>മലയാളം</span><span>हिन्दी</span></div>
</div>
""",
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Loading multilingual NLP model (first run downloads ~470 MB)…")
def get_brain():
    return Brain()


QUICK = [
    "How can I contact admissions?",
    "What are the library timings?",
    "Route from Technology Tower to Main Building",
    "Where is the Anna Auditorium?",
    "What are the mess timings?",
]

S = st.session_state
S.setdefault("messages", [{"role": "assistant", "content": C.GREETING, "meta": {}}])
S.setdefault("last_audio", None)
S.setdefault("pending", None)
S.setdefault("fresh_audio", False)

with st.sidebar:
    st.markdown("### 🎓 Campus Connect")
    st.caption("Intelligent College FAQ and Navigation Chatbot")
    st.markdown("---")
    speak_on = st.toggle("🔊 Speak replies (needs internet)", value=False)
    auto_open = st.toggle("🗺️ Auto-open maps", value=True)
    st.markdown("---")
    st.markdown("**Quick questions**")
    for q in QUICK:
        if st.button(q, use_container_width=True, key=f"quick_{q}"):
            S.pending = q
    st.markdown("---")
    if st.button("🗑️ Clear chat", use_container_width=True):
        S.messages = [{"role": "assistant", "content": C.GREETING, "meta": {}}]
        S.last_audio = None
        st.rerun()
    st.caption("Languages: " + " · ".join(C.LANGS.values()))

with st.spinner("Starting Campus Connect…"):
    brain = get_brain()


def handle(text, lang, source):
    S.messages.append({"role": "user", "content": text, "meta": {"lang": lang, "source": source}})
    res = brain.respond(text, lang)
    meta = {
        "lang": lang,
        "kind": res["kind"],
        "score": res.get("score", 0.0),
        "verified": res.get("verified", True),
        "map_url": res.get("map_url"),
        "audio": None,
    }
    if speak_on:
        try:
            meta["audio"] = speak(res["text"], lang)
            S.fresh_audio = True
        except Exception as exc:
            meta["tts_error"] = str(exc)
    if res["kind"] == "route" and auto_open and res.get("map_url"):
        try:
            webbrowser.open(res["map_url"])
        except Exception:
            pass
    S.messages.append({"role": "assistant", "content": res["text"], "meta": meta})


chat_area = st.container()

audio = st.audio_input("🎙️ Tap to speak (English · தமிழ் · తెలుగు · മലയാളം · हिन्दी)")
typed = st.chat_input("Type your question…")

if audio is not None:
    data = audio.getvalue()
    digest = hashlib.md5(data).hexdigest()
    if digest != S.last_audio:
        S.last_audio = digest
        with st.spinner("Transcribing and detecting language…"):
            heard, spoken_lang = transcribe(data)
        if heard:
            handle(heard, spoken_lang, "voice")
        else:
            st.warning("I couldn't hear anything. Please try again closer to the microphone.")

if typed:
    handle(typed, detect_text_lang(typed), "text")

if S.pending:
    q, S.pending = S.pending, None
    handle(q, detect_text_lang(q), "text")

with chat_area:
    autoplay = S.fresh_audio
    S.fresh_audio = False
    last = len(S.messages) - 1
    for i, m in enumerate(S.messages):
        is_user = m["role"] == "user"
        with st.chat_message(m["role"], avatar="🧑‍🎓" if is_user else "🎓"):
            st.markdown(m["content"])
            meta = m.get("meta", {})
            if is_user and meta:
                icon = "🎙️ Voice" if meta.get("source") == "voice" else "⌨️ Text"
                st.markdown(f"<div class='meta'>{icon} · {C.LANGS.get(meta['lang'], meta['lang'])}</div>", unsafe_allow_html=True)
            elif meta:
                label = {"faq": "FAQ answer", "route": "Navigation", "unknown": "Unknown place", "fallback": "No match"}.get(meta.get("kind"), "")
                st.markdown(
                    f"<div class='meta'>{label} · {C.LANGS.get(meta['lang'], meta['lang'])} · confidence {meta.get('score', 0):.2f}</div>",
                    unsafe_allow_html=True,
                )
                if meta.get("map_url"):
                    st.link_button("🗺️ Open in Google Maps", meta["map_url"])
                if not meta.get("verified", True):
                    st.markdown("<div class='warn'>⚠️ Sample or placeholder data. Please confirm with the official VIT office.</div>", unsafe_allow_html=True)
                if meta.get("audio"):
                    st.audio(meta["audio"], format="audio/mp3", autoplay=autoplay and i == last)
                if meta.get("tts_error"):
                    st.caption("Voice reply unavailable (check internet).")
