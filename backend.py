import csv
import random
from datetime import date, timedelta
import os

# --- DATA STORAGE ---
vocab_data = {}  
user_profile = {
    "streak": 0,
    "last_study_date": "",
    "total_correct": 0
}

def load_data():
    """Loads vocabulary and progress using basic text file handling."""
    global vocab_data, user_profile
    
    # 1. Load Vocabulary from CSV
    try:
        with open("500_beginner_korean_words.csv", mode="r", encoding="utf-8-sig") as file:
            reader = csv.reader(file)
            next(reader) 
            for row in reader:
                if len(row) >= 3:
                    korean_word = row[1].strip()
                    english = row[2].strip()
                    vocab_data[korean_word] = {'english': english, 'mastery': 0}
    except FileNotFoundError:
        print("Error: CSV file not found.")

    # 2. Load User Profile from TXT
    if os.path.exists("user_profile.txt"):
        with open("user_profile.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
            if len(lines) >= 3:
                user_profile["streak"] = int(lines[0].strip())
                user_profile["last_study_date"] = lines[1].strip()
                user_profile["total_correct"] = int(lines[2].strip())

    # 3. Load Mastery Levels from TXT
    if os.path.exists("mastery_data.txt"):
        with open("mastery_data.txt", "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    word = parts[0]
                    mastery_score = int(parts[1])
                    if word in vocab_data:
                        vocab_data[word]['mastery'] = mastery_score
                        
    update_streak()

def save_data():
    """Saves progress using basic text file writing."""
    with open("user_profile.txt", "w", encoding="utf-8") as file:
        file.write(f"{user_profile['streak']}\n")
        file.write(f"{user_profile['last_study_date']}\n")
        file.write(f"{user_profile['total_correct']}\n")

    with open("mastery_data.txt", "w", encoding="utf-8") as file:
        for word, data in vocab_data.items():
            if data['mastery'] != 0:
                file.write(f"{word},{data['mastery']}\n")

def reset_all_data():
    """Deletes save files and resets memory for a fresh start."""
    global user_profile, vocab_data
    
    # Reset profile memory
    user_profile = {
        "streak": 0,
        "last_study_date": "",
        "total_correct": 0
    }
    
    # Reset vocabulary mastery in memory
    for word in vocab_data:
        vocab_data[word]['mastery'] = 0
        
    # Delete text files from disk if they exist
    if os.path.exists("user_profile.txt"):
        os.remove("user_profile.txt")
    if os.path.exists("mastery_data.txt"):
        os.remove("mastery_data.txt")

def update_streak():
    global user_profile
    today_str = date.today().isoformat()
    last_date_str = user_profile["last_study_date"]

    if last_date_str:
        last_date = date.fromisoformat(last_date_str)
        yesterday = date.today() - timedelta(days=1)
        
        if last_date < yesterday:
            user_profile["streak"] = 0 
            
def record_study_session():
    global user_profile
    today_str = date.today().isoformat()
    if user_profile["last_study_date"] != today_str:
        user_profile["streak"] += 1
        user_profile["last_study_date"] = today_str

def get_quiz_batch(mode, amount=10):
    if mode == "weak_words":
        pool = [w for w, d in vocab_data.items() if d['mastery'] < 0]
        if not pool: return []
        return random.sample(pool, min(amount, len(pool)))
    
    pool = list(vocab_data.keys())
    weights = [max(1, 10 - vocab_data[word]['mastery']) for word in pool]
    return random.choices(pool, weights=weights, k=amount)

def check_answer_logic(word, user_answer, mode):
    english = vocab_data[word]['english']
    correct_answer = english if mode == "kr_to_en" else word
    is_correct = (user_answer.strip().lower() == correct_answer.strip().lower())

    if is_correct:
        vocab_data[word]['mastery'] += 1
        user_profile["total_correct"] += 1
    else:
        vocab_data[word]['mastery'] -= 1 

    return is_correct, correct_answer