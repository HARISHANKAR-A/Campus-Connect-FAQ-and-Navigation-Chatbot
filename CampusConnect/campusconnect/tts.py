import io
import re

from gtts import gTTS


def speak(text: str, lang: str) -> bytes:
    clean = re.sub(r"https?://\S+", "", text)
    clean = re.sub(r"\[PLACEHOLDER[^\]]*\]", "", clean)
    clean = clean.replace("*", "").strip()
    buf = io.BytesIO()
    gTTS(text=clean, lang=lang).write_to_fp(buf)
    return buf.getvalue()
