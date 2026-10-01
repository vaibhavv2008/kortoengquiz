import csv
import random
from datetime import date, timedelta
import os

VOCAB_FILE = "500_beginner_korean_words.csv"
PROFILE_FILE = "user_profile.txt"
MASTERY_FILE = "mastery_data.txt"

vocab_data = {}

user_profile = {
    "streak": 0,
    "last_study_date": "",
    "total_correct": 0
}


def load_data():
    global vocab_data, user_profile

    vocab_data = {}

    user_profile = {
        "streak": 0,
        "last_study_date": "",
        "total_correct": 0
    }

    # Load vocabulary CSV
    try:
        with open(VOCAB_FILE, "r", encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file)

            next(reader, None)

            for row in reader:
                if len(row) >= 3 and row[1].strip() and row[2].strip():
                    korean_word = row[1].strip()
                    english_word = row[2].strip()

                    vocab_data[korean_word] = {
                        "english": english_word,
                        "mastery": 0
                    }

    except FileNotFoundError:
        print("Error: CSV file not found.")

    # Load user profile
    try:
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r", encoding="utf-8") as file:
                lines = file.readlines()

                if len(lines) >= 3:
                    user_profile["streak"] = max(
                        0,
                        int(lines[0].strip())
                    )

                    user_profile["last_study_date"] = lines[1].strip()

                    user_profile["total_correct"] = max(
                        0,
                        int(lines[2].strip())
                    )

    except (OSError, ValueError):
        print("Warning: Invalid user profile found. Starting fresh.")

    # Load word mastery scores
    try:
        if os.path.exists(MASTERY_FILE):
            with open(MASTERY_FILE, "r", encoding="utf-8") as file:
                for line in file:
                    word, comma, score = line.strip().rpartition(",")

                    if comma and word in vocab_data:
                        vocab_data[word]["mastery"] = int(score)

    except (OSError, ValueError):
        print("Warning: Invalid mastery data was ignored.")

    update_streak()


def save_data():
    with open(PROFILE_FILE, "w", encoding="utf-8") as file:
        file.write(f"{user_profile['streak']}\n")
        file.write(f"{user_profile['last_study_date']}\n")
        file.write(f"{user_profile['total_correct']}\n")

    with open(MASTERY_FILE, "w", encoding="utf-8") as file:
        for word, data in vocab_data.items():
            if data["mastery"] != 0:
                file.write(f"{word},{data['mastery']}\n")


def reset_all_data():
    global user_profile

    user_profile = {
        "streak": 0,
        "last_study_date": "",
        "total_correct": 0
    }

    for word in vocab_data:
        vocab_data[word]["mastery"] = 0

    if os.path.exists(PROFILE_FILE):
        os.remove(PROFILE_FILE)

    if os.path.exists(MASTERY_FILE):
        os.remove(MASTERY_FILE)


def update_streak():
    last_date_string = user_profile["last_study_date"]

    if not last_date_string:
        return

    try:
        last_date = date.fromisoformat(last_date_string)

    except ValueError:
        user_profile["streak"] = 0
        user_profile["last_study_date"] = ""
        return

    yesterday = date.today() - timedelta(days=1)

    if last_date < yesterday:
        user_profile["streak"] = 0


def record_study_session():
    today = date.today().isoformat()

    if user_profile["last_study_date"] != today:
        user_profile["streak"] += 1
        user_profile["last_study_date"] = today


def get_quiz_batch(mode="kr_to_en", amount=10):
    if mode == "weak_words":
        pool = [
            word for word, data in vocab_data.items()
            if data["mastery"] < 0
        ]

        return random.sample(pool, min(amount, len(pool)))

    # Weighted selection without repeating a word in the same quiz.
    available_words = list(vocab_data.keys())
    batch = []

    while available_words and len(batch) < amount:
        weights = [
            max(1, 10 - vocab_data[word]["mastery"])
            for word in available_words
        ]

        selected_word = random.choices(
            available_words,
            weights=weights,
            k=1
        )[0]

        batch.append(selected_word)
        available_words.remove(selected_word)

    return batch


def accepted_answers(text):
    text = text.strip().casefold()

    answers = {text}

    # Example: "hi/bye" accepts "hi", "bye", or "hi/bye".
    if "/" in text:
        for part in text.split("/"):
            part = part.strip()

            if part:
                answers.add(part)

    # Example: "goodbye (to someone leaving)"
    # also accepts "goodbye".
    if " (" in text and text.endswith(")"):
        main_translation = text.split(" (", 1)[0].strip()

        if main_translation:
            answers.add(main_translation)

    return answers


def check_answer_logic(word, user_answer, mode="kr_to_en"):
    english = vocab_data[word]["english"]

    if mode == "kr_to_en":
        correct_answer = english
    else:
        correct_answer = word

    cleaned_answer = user_answer.strip().casefold()

    is_correct = cleaned_answer in accepted_answers(correct_answer)

    if is_correct:
        vocab_data[word]["mastery"] += 1
        user_profile["total_correct"] += 1

    else:
        vocab_data[word]["mastery"] -= 1

    return is_correct, correct_answer
