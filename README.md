# Kor to Eng Quiz

A desktop quiz for learning beginner Korean vocabulary. You're shown a Korean word and type its English meaning. The app tracks your daily streak, remembers the words you struggle with, and shows those more often.

Built with Python and [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter).

<p align="center">
  <img src="screenshot.png" alt="Kor to Eng Quiz dashboard" width="800">
</p>

---

## Features

- **Korean → English quiz** with 10 questions per session
- **Smart word selection:** words you get wrong come up more often
- **Flexible answers:** not case-sensitive, and entries like `hi/bye` accept `hi` or `bye`
- **Skip button** to reveal the answer
- **Daily streak** and **total correct** counter
- **Weakness analysis** screen listing the words you struggle with
- **Auto-save** after every answer
- **Reset progress** button

---

## Setup

1. Install Python 3.8 or newer.
2. Install the required package:

   ```bash
   pip install customtkinter
   ```

   *(Optional, Windows only)* `pip install pywinstyles` for the translucent window effect. The app works fine without it.

3. Put `500_beginner_korean_words.csv` in the same folder as `main.py`.

---

## Run

From the project folder:

```bash
python main.py
```

---

## How to use

1. **Dashboard:** click **START QUIZ** to begin, **VIEW ANALYSIS** to see your weak words, or **RESET PROGRESS** to start over.
2. **Quiz:** type the English meaning and press `Enter` (or click **SUBMIT**). Click **SKIP** if you don't know it.
3. **Results:** after 10 questions you'll see your score. Click **RETURN TO DASHBOARD** to go back.

Correct answers raise a word's score and wrong or skipped answers lower it. Words with a score below zero show up as weak words and appear more often in quizzes.

---

## Project structure

```
.
├── main.py                          # App window and quiz screens
├── Backend.py                       # Quiz logic and saving
├── screenshot.png                   # Screenshot used in this README
├── 500_beginner_korean_words.csv    # Vocabulary list
├── user_profile.txt                 # Auto-created: streak and total correct
└── mastery_data.txt                 # Auto-created: your word scores
```

---

## Vocabulary file format

A UTF-8 CSV with a header row. The Korean word goes in column 2 and the English meaning in column 3. Column 1 is ignored.

```csv
id,korean,english
1,안녕하세요,hello
2,감사합니다,thank you
3,안녕,hi/bye
```

---

## Troubleshooting

| Problem | Fix |
| --- | --- |
| *"Vocabulary could not be loaded"* | Make sure the CSV is in the same folder as `main.py` and run the app from that folder. |
| `ModuleNotFoundError: customtkinter` | Run `pip install customtkinter`. |
