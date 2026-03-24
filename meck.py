import json
import difflib
import re

KB_FILE = "knowledge.json"
MEM_FILE = "memory.json"

# ---------- LOAD ----------
def load_json(file, default):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return default

KB = load_json(KB_FILE, {})
MEM = load_json(MEM_FILE, {})

# ---------- NORMALIZE ----------
def normalize(text):
    if not text:
        return ""

    text = text.lower()

    remove_words = [
        "meck", "please", "can you", "tell me",
        "what is", "who is", "define", "explain",
        "about", "the", "an", "a", "is", "are"
    ]

    for w in remove_words:
        text = text.replace(w, "")

    return text.strip()

def clean_text(text):
    return re.sub(r"[^a-z0-9\s]", "", text)

# ---------- MATCH ENGINE ----------
def find_answer(q, source):
    if not q:
        return None

    # 1️⃣ exact match
    if q in source:
        return source[q]

    # 2️⃣ contains match
    for k in source:
        if q in k or k in q:
            return source[k]

    # 3️⃣ keyword scoring (improved)
    best_score = 0
    best_answer = None

    q_words = set(q.split())

    for k, a in source.items():
        k_words = set(k.split())
        score = len(q_words & k_words)

        if score > best_score:
            best_score = score
            best_answer = a

    if best_score >= 1:
        return best_answer

    # 4️⃣ fuzzy match (last fallback)
    matches = difflib.get_close_matches(q, source.keys(), n=1, cutoff=0.6)
    if matches:
        return source[matches[0]]

    return None

# ---------- SMART FALLBACK ----------
def fallback_response(q):
    if not q:
        return "Please ask something."

    if "your name" in q:
        return "I am Meck."

    if "who are you" in q:
        return "I am Meck, your AI assistant."

    if "help" in q:
        return "You can ask me about technology, Meck, Mecknown, or general knowledge."

    return "I do not have information about that yet. You can train me from the admin panel."

# ---------- HANDLE ----------
def handle(text, web_mode=False):
    text = text.lower()

    # direct identity override
    if any(q in text for q in [
        "who is your developer",
        "who developed you",
        "who made you"
    ]):
        return "I am developed by Shaazim"

    q = normalize(text)
    q = clean_text(q)

    # 1️⃣ MEMORY
    if q in MEM:
        return MEM[q]

    # 2️⃣ KNOWLEDGE BASE
    ans = find_answer(q, KB)
    if ans:
        return ans

    # 3️⃣ FALLBACK
    return fallback_response(q)
