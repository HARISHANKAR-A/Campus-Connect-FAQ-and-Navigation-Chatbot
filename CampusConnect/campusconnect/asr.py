import io
from functools import lru_cache

from faster_whisper import WhisperModel

from . import config as C

ALLOWED = ("en", "ta", "te", "ml", "hi")


@lru_cache(maxsize=1)
def _model():
    return WhisperModel(C.WHISPER_MODEL, device="cpu", compute_type=C.WHISPER_COMPUTE)


def transcribe(audio_bytes: bytes):
    model = _model()
    buf = io.BytesIO(audio_bytes)
    segments, info = model.transcribe(buf, beam_size=5, vad_filter=True)
    probs = dict(info.all_language_probs or [])
    probs.setdefault(info.language, info.language_probability)
    lang = max(ALLOWED, key=lambda code: probs.get(code, 0.0))
    if lang != info.language:
        buf.seek(0)
        segments, info = model.transcribe(buf, language=lang, beam_size=5, vad_filter=True)
    text = " ".join(s.text.strip() for s in segments).strip()
    return text, lang
