import json
import re

import numpy as np
from sentence_transformers import SentenceTransformer

from . import config as C
from .maps import directions_url

SCRIPTS = (("ta", 0x0B80, 0x0BFF), ("te", 0x0C00, 0x0C7F), ("ml", 0x0D00, 0x0D7F), ("hi", 0x0900, 0x097F))

CUES = re.compile(
    r"\broute\b|\bdirections?\b|\bnavigate\b|\bhow (?:do i|to|can i) (?:get|reach|go)\b"
    r"|\bwhere(?:'s| is| are)\b|\bway to\b|\bpath to\b|\btake me\b|\bon (?:the )?map\b"
    r"|रास्ता|रास्ते|मार्ग|कहाँ|कहां|कैसे पहुँच|कैसे पहुंच|दिशा"
    r"|வழி|பாதை|எங்கே|எங்கு|எப்படி செல்"
    r"|దారి|మార్గం|ఎక్కడ|ఎలా వెళ్"
    r"|വഴി|എവിടെ|എങ്ങനെ പോകാം",
    re.I,
)


def detect_text_lang(text: str) -> str:
    counts = {code: 0 for code, _, _ in SCRIPTS}
    for ch in text:
        o = ord(ch)
        for code, lo, hi in SCRIPTS:
            if lo <= o <= hi:
                counts[code] += 1
    best = max(counts, key=counts.get)
    return best if counts[best] > 0 else "en"


class Brain:
    def __init__(self):
        self.model = SentenceTransformer(C.EMBED_MODEL)
        self.faqs = json.loads(C.FAQ_PATH.read_text(encoding="utf-8"))["faqs"]
        locs = json.loads(C.LOC_PATH.read_text(encoding="utf-8"))["locations"]
        self.locs = {l["id"]: l for l in locs}

        questions, self.q_owner = [], []
        for i, faq in enumerate(self.faqs):
            for q in faq["questions"]:
                questions.append(q)
                self.q_owner.append(i)
        self.q_emb = self._enc(questions)

        self.aliases = []
        for lid, loc in self.locs.items():
            for a in [loc["name"]] + loc.get("aliases", []):
                self.aliases.append((a.lower(), lid))
        self.aliases.sort(key=lambda x: -len(x[0]))
        self.a_emb = self._enc([a for a, _ in self.aliases])

    def _enc(self, texts):
        return self.model.encode(texts, normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False)

    def retrieve(self, text):
        sims = self.q_emb @ self._enc([text])[0]
        k = int(np.argmax(sims))
        return self.faqs[self.q_owner[k]], float(sims[k])

    def find_places(self, text, lang):
        low = text.lower()
        taken, hits = [], []
        for alias, lid in self.aliases:
            pattern = r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])" if alias.isascii() else re.escape(alias)
            for m in re.finditer(pattern, low):
                s, e = m.span()
                if any(s < te and e > ts for ts, te in taken):
                    continue
                taken.append((s, e))
                hits.append((s, lid))
        hits.sort()
        ids = []
        for _, lid in hits:
            if lid not in ids:
                ids.append(lid)
        if lang == "en" and len(ids) == 2:
            for s, lid in hits:
                if re.search(r"\bfrom(?: the)?\s*$", low[:s]):
                    other = [i for i in ids if i != lid][0]
                    ids = [lid, other]
                    break
        if not ids:
            sims = self.a_emb @ self._enc([text])[0]
            k = int(np.argmax(sims))
            if sims[k] >= 0.55:
                ids = [self.aliases[k][1]]
        return ids[:2]

    def _name(self, loc, lang):
        return loc.get("names", {}).get(lang, loc["name"])

    def _route(self, ids, lang):
        dest = self.locs[ids[-1]]
        origin = self.locs[ids[0]] if len(ids) == 2 else None
        strings = C.T[lang]
        if origin:
            text = strings["route_from"].format(origin=self._name(origin, lang), dest=self._name(dest, lang))
        else:
            text = strings["route"].format(dest=self._name(dest, lang))
        verified = dest.get("verified", True) and (origin is None or origin.get("verified", True))
        return {
            "kind": "route",
            "text": text,
            "map_url": directions_url(dest, origin),
            "verified": verified,
            "score": 1.0,
        }

    def _unknown(self, lang):
        examples = ", ".join(l["name"] for l in list(self.locs.values())[:6])
        return {"kind": "unknown", "text": C.T[lang]["unknown"].format(examples=examples), "score": 0.0}

    def respond(self, text, lang):
        faq, score = self.retrieve(text)
        if CUES.search(text):
            ids = self.find_places(text, lang)
            if ids:
                return self._route(ids, lang)
            if score < 0.6:
                return self._unknown(lang)
        if score >= C.FAQ_THRESHOLD:
            answers = faq["answers"]
            return {
                "kind": "faq",
                "text": answers.get(lang) or answers["en"],
                "score": score,
                "verified": faq.get("verified", True),
                "category": faq.get("category", ""),
            }
        return {"kind": "fallback", "text": C.T[lang]["fallback"], "score": score}
