import json
import os
import difflib
import re

from listen import listen
from wake import WakeWord

KB_FILE = "knowledge.json"
MEM_FILE = "memory.json"

# ---------- LOAD ----------
with open(KB_FILE, "r") as f:
    KB = json.load(f)

try:
    with open(MEM_FILE, "r") as f:
        MEM = json.load(f)
except:
    MEM = {}

# ---------- SPEAK ----------
def speak(text):
    if not text:
        return

    text = text.replace('"', '').replace("'", "")
    print("MECK:", text)

    os.system(f'pico2wave -w /tmp/meck.wav "{text}"')
    os.system('aplay /tmp/meck.wav')

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

# ---------- MEMORY ----------
def save_memory():
    with open(MEM_FILE, "w") as f:
        json.dump(MEM, f, indent=2)

def learn():
    speak("What question should I remember?")
    q = normalize(listen())

    if not q:
        speak("I did not hear the question.")
        return

    speak("What is the answer?")
    a = listen()

    if not a:
        speak("I did not hear the answer.")
        return

    MEM[q] = a
    save_memory()
    speak("Saved.")

def forget():
    speak("Which question should I forget?")
    q = normalize(listen())

    if not q:
        speak("I did not hear the question.")
        return

    if q in MEM:
        del MEM[q]
        save_memory()
        speak("Deleted.")
    else:
        speak("Memory not found.")

# ---------- HANDLE ----------
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

# ---------- MAIN ----------
def main():
    speak("MECK sleeping.")
    wake = WakeWord()

    awake = False

    while True:
        try:
            if not awake:
                wake.listen()
                awake = True
                speak("Yes?")
                continue

            command = listen()
            if not command:
                continue

            command = command.lower()

            if any(x in command for x in [
                "sleep",
                "go to sleep",
                "stop listening"
            ]):
                speak("Going to sleep.")
                awake = False
                continue

            response = handle(command)
            speak(response)

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
