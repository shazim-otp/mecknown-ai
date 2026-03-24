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
        "what is", "who is", "define", "explain"
    ]
    for w in remove_words:
        text = text.replace(w, "")
    return text.strip()

def clean_text(text):
    return re.sub(r"[^a-z0-9\s]", "", text)

# ---------- SPELL CORRECTION ----------
def correct_spelling(query, keys):
    words = query.split()
    corrected = []
    for w in words:
        match = difflib.get_close_matches(w, keys, n=1, cutoff=0.75)
        corrected.append(match[0] if match else w)
    return " ".join(corrected)

# ---------- MATCH ----------
def keyword_score(q, k):
    return len(set(q.split()) & set(k.split()))

def find_answer(q, source):
    best_score = 0
    best_answer = None
    for k, a in source.items():
        score = keyword_score(q, k)
        if score > best_score:
            best_score = score
            best_answer = a
    return best_answer

# ---------- HANDLE (MAIN AI LOGIC) ----------
def handle(text, web_mode=False):
    text = text.lower()

    if any(q in text for q in [
        "who is your developer",
        "who developed you",
        "who made you"
    ]):
        return "I am developed by Shaazim"

    q = normalize(text)
    q = clean_text(q)

    kb_keys = list(KB.keys())
    corrected_q = correct_spelling(q, kb_keys)

    # 1️⃣ MEMORY
    if corrected_q in MEM:
        return MEM[corrected_q]

    # 2️⃣ LOCAL KNOWLEDGE
    ans = find_answer(corrected_q, KB)
    if ans:
        return ans

    return "I do not have information about that yet."
