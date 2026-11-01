import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FAQ_PATH = DATA_DIR / "faqs.json"
LOC_PATH = DATA_DIR / "locations.json"

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
WHISPER_COMPUTE = os.getenv("WHISPER_COMPUTE", "int8")
EMBED_MODEL = os.getenv("EMBED_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
FAQ_THRESHOLD = float(os.getenv("FAQ_THRESHOLD", "0.45"))

LANGS = {"en": "English", "ta": "தமிழ்", "te": "తెలుగు", "ml": "മലയാളം", "hi": "हिन्दी"}

APP_TITLE = "CampusConnect: Intelligent College FAQ and Navigation Chatbot"
BOT_NAME = "Campus Connect"

GREETING = (
    "Hello! I'm **Campus Connect**, your VIT Vellore assistant. "
    "Ask about admissions, academics, hostels, the library or campus places, "
    "by voice or text, in English, Tamil, Telugu, Malayalam or Hindi. "
    "Try *\"Route from PRP to Main Block\"*."
)

T = {
    "en": {
        "route": "Opening directions to **{dest}** from your current location.",
        "route_from": "Opening directions from **{origin}** to **{dest}**.",
        "unknown": "I couldn't find that place on the campus map. Try one of: {examples}.",
        "fallback": "Sorry, I couldn't find a reliable answer. Please rephrase, or contact the VIT helpdesk at +91 416 224 3091.",
    },
    "ta": {
        "route": "உங்கள் தற்போதைய இடத்திலிருந்து **{dest}** செல்லும் வழியைத் திறக்கிறேன்.",
        "route_from": "**{origin}** இலிருந்து **{dest}** செல்லும் வழியைத் திறக்கிறேன்.",
        "unknown": "அந்த இடம் வளாக வரைபடத்தில் கிடைக்கவில்லை. இவற்றில் ஒன்றை முயற்சிக்கவும்: {examples}.",
        "fallback": "மன்னிக்கவும், நம்பகமான பதில் கிடைக்கவில்லை. மீண்டும் கேளுங்கள் அல்லது +91 416 224 3091 என்ற எண்ணில் தொடர்பு கொள்ளவும்.",
    },
    "te": {
        "route": "మీ ప్రస్తుత స్థానం నుండి **{dest}** కు దారిని తెరుస్తున్నాను.",
        "route_from": "**{origin}** నుండి **{dest}** కు దారిని తెరుస్తున్నాను.",
        "unknown": "ఆ స్థలం క్యాంపస్ మ్యాప్‌లో కనబడలేదు. వీటిలో ఒకదాన్ని ప్రయత్నించండి: {examples}.",
        "fallback": "క్షమించండి, నమ్మదగిన సమాధానం దొరకలేదు. దయచేసి మళ్లీ అడగండి లేదా +91 416 224 3091 కు కాల్ చేయండి.",
    },
    "ml": {
        "route": "നിങ്ങളുടെ നിലവിലെ സ്ഥലത്തു നിന്ന് **{dest}** ലേക്കുള്ള വഴി തുറക്കുന്നു.",
        "route_from": "**{origin}** ൽ നിന്ന് **{dest}** ലേക്കുള്ള വഴി തുറക്കുന്നു.",
        "unknown": "ആ സ്ഥലം ക്യാമ്പസ് മാപ്പിൽ കണ്ടെത്തിയില്ല. ഇവയിലൊന്ന് പരീക്ഷിക്കുക: {examples}.",
        "fallback": "ക്ഷമിക്കണം, വിശ്വസനീയമായ ഉത്തരം കണ്ടെത്താനായില്ല. വീണ്ടും ചോദിക്കുക അല്ലെങ്കിൽ +91 416 224 3091 ൽ ബന്ധപ്പെടുക.",
    },
    "hi": {
        "route": "आपके वर्तमान स्थान से **{dest}** का रास्ता खोल रहा हूँ।",
        "route_from": "**{origin}** से **{dest}** तक का रास्ता खोल रहा हूँ।",
        "unknown": "वह स्थान कैंपस मानचित्र में नहीं मिला। इनमें से कोई आज़माएँ: {examples}।",
        "fallback": "क्षमा करें, भरोसेमंद उत्तर नहीं मिला। कृपया दोबारा पूछें या +91 416 224 3091 पर संपर्क करें।",
    },
}
