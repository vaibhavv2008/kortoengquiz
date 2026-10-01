import platform
import customtkinter as ctk
import Backend

# ==========================================
# APP SETUP & THEME
# ==========================================

app = ctk.CTk()
app.geometry("900x650")
app.title("Kor to Eng Quiz")

ctk.set_appearance_mode("Dark")

# Acrylic effect only runs on Windows.
if platform.system() == "Windows":
    try:
        import pywinstyles
        pywinstyles.apply_style(app, "acrylic")

    except ImportError:
        print("pywinstyles is not installed. Acrylic effect disabled.")

# Neon Color Palette
COLOR_PANEL = "#111827"
COLOR_CYAN = "#00D2FF"
COLOR_PURPLE = "#7000FF"
COLOR_PINK = "#FF007A"

Backend.load_data()

# Global quiz state
current_batch = []
current_index = 0
score = 0
TOTAL_Q = 10


# ==========================================
# FUNCTIONS: QUIZ LOGIC
# ==========================================

def start_quiz():
    global current_batch, current_index, score

    current_index = 0
    score = 0

    current_batch = Backend.get_quiz_batch("kr_to_en", TOTAL_Q)

    if not current_batch:
        lbl_start_subtitle.configure(
            text="Vocabulary could not be loaded. Check the CSV file.",
            text_color=COLOR_PINK
        )
        return

    # Saves the streak as soon as the learner starts studying.
    Backend.record_study_session()
    Backend.save_data()

    frame_start.pack_forget()
    frame_analysis.pack_forget()

    btn_return.pack_forget()

    entry_answer.pack(pady=20, fill="x", padx=150)
    frame_quiz_buttons.pack(pady=15, fill="x", padx=150)

    frame_quiz.pack(
        fill="both",
        expand=True,
        padx=40,
        pady=40
    )

    update_ui()


def update_ui():
    word_key = current_batch[current_index]

    lbl_word.configure(
        text=word_key,
        text_color="white"
    )

    lbl_feedback.configure(text="")

    entry_answer.delete(0, "end")

    entry_answer.configure(state="normal")
    btn_submit.configure(state="normal")
    btn_skip.configure(state="normal")

    progress = current_index / len(current_batch)

    progress_bar.set(progress)

    lbl_progress.configure(
        text=f"Question {current_index + 1} of {len(current_batch)}"
    )

    entry_answer.focus()


def process_answer(event=None):
    global score

    # Stops fast repeated Enter presses from submitting twice.
    if current_index >= len(current_batch):
        return

    if entry_answer.cget("state") != "normal":
        return

    word_key = current_batch[current_index]
    user_input = entry_answer.get()

    is_correct, correct_answer = Backend.check_answer_logic(
        word_key,
        user_input,
        "kr_to_en"
    )

    if is_correct:
        score += 1

        lbl_feedback.configure(
            text=f"✨ Correct! ({correct_answer})",
            text_color=COLOR_CYAN
        )

    else:
        lbl_feedback.configure(
            text=f"❌ Oops! It means: {correct_answer}",
            text_color=COLOR_PINK
        )

    Backend.save_data()

    move_to_next()


def skip_question():
    if current_index >= len(current_batch):
        return

    word_key = current_batch[current_index]

    _, correct_answer = Backend.check_answer_logic(
        word_key,
        "",
        "kr_to_en"
    )

    lbl_feedback.configure(
        text=f"⏭️ Skipped! It means: {correct_answer}",
        text_color="#F59E0B"
    )

    Backend.save_data()

    move_to_next()


def move_to_next():
    global current_index

    entry_answer.configure(state="disabled")
    btn_submit.configure(state="disabled")
    btn_skip.configure(state="disabled")

    current_index += 1

    progress_bar.set(current_index / len(current_batch))

    # Shows feedback for one second before moving forward.
    if current_index < len(current_batch):
        app.after(1000, update_ui)

    else:
        app.after(1000, end_quiz)


def end_quiz():
    lbl_word.configure(
        text="Session Complete!",
        text_color=COLOR_CYAN
    )

    lbl_feedback.configure(
        text=f"Final Score: {score} / {len(current_batch)}",
        text_color="white"
    )

    entry_answer.pack_forget()
    frame_quiz_buttons.pack_forget()

    btn_return.pack(pady=15)


def return_to_start():
    frame_quiz.pack_forget()
    frame_analysis.pack_forget()

    btn_return.pack_forget()

    lbl_streak.configure(
        text=f"🔥 Streak: {Backend.user_profile['streak']} Days"
    )

    lbl_total.configure(
        text=(
            "✅ Total Correct Answers: "
            f"{Backend.user_profile['total_correct']}"
        )
    )

    frame_start.pack(
        fill="both",
        expand=True,
        padx=40,
        pady=40
    )


def show_analysis():
    frame_start.pack_forget()

    textbox_weak_words.configure(state="normal")
    textbox_weak_words.delete("1.0", "end")

    weak_words = [
        word
        for word, data in Backend.vocab_data.items()
        if data["mastery"] < 0
    ]

    if not weak_words:
        textbox_weak_words.insert(
            "0.0",
            "You have no weak words right now!\n"
            "Play some quizzes, and missed words will appear here.\n"
        )

    else:
        textbox_weak_words.insert(
            "0.0",
            f"You are currently struggling with "
            f"{len(weak_words)} words:\n\n"
        )

        for word in weak_words[:30]:
            english = Backend.vocab_data[word]["english"]

            textbox_weak_words.insert(
                "end",
                f"• {word}  ➔  {english}\n"
            )

    textbox_weak_words.configure(state="disabled")

    frame_analysis.pack(
        fill="both",
        expand=True,
        padx=40,
        pady=40
    )


def reset_progress():
    Backend.reset_all_data()

    lbl_streak.configure(text="🔥 Streak: 0 Days")

    lbl_total.configure(
        text="✅ Total Correct Answers: 0"
    )

    lbl_start_subtitle.configure(
        text="Progress cleared! Ready for a fresh start.",
        text_color=COLOR_CYAN
    )


def close_app():
    app.destroy()


# ==========================================
# WIDGETS: START SCREEN
# ==========================================

frame_start = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

frame_start.pack(
    fill="both",
    expand=True,
    padx=40,
    pady=40
)

lbl_start_title = ctk.CTkLabel(
    frame_start,
    text="SYSTEM INITIALIZED",
    font=("Consolas", 18, "bold"),
    text_color=COLOR_CYAN
)

lbl_start_title.pack(pady=(10, 0))

lbl_start_main = ctk.CTkLabel(
    frame_start,
    text="Kor to Eng Quiz",
    font=("Helvetica", 50, "bold")
)

lbl_start_main.pack(pady=(0, 2))

lbl_start_subtitle = ctk.CTkLabel(
    frame_start,
    text="Welcome back.",
    font=("Consolas", 14),
    text_color="#6B7280"
)

lbl_start_subtitle.pack(pady=(0, 10))

# Stats panel
frame_stats = ctk.CTkFrame(
    frame_start,
    fg_color=COLOR_PANEL,
    corner_radius=15,
    border_width=1,
    border_color="#374151"
)

frame_stats.pack(
    pady=10,
    fill="x",
    padx=100
)

lbl_streak = ctk.CTkLabel(
    frame_stats,
    text=f"🔥 Streak: {Backend.user_profile['streak']} Days",
    font=("Helvetica", 16, "bold"),
    text_color=COLOR_PINK
)

lbl_streak.pack(pady=(15, 2))

lbl_total = ctk.CTkLabel(
    frame_stats,
    text=(
        "✅ Total Correct Answers: "
        f"{Backend.user_profile['total_correct']}"
    ),
    font=("Helvetica", 15)
)

lbl_total.pack(pady=(2, 15))

btn_start = ctk.CTkButton(
    frame_start,
    text="START QUIZ",
    command=start_quiz,
    height=45,
    corner_radius=8,
    font=("Consolas", 16, "bold"),
    fg_color=COLOR_PURPLE,
    hover_color="#5B00D1"
)

btn_start.pack(
    pady=(15, 8),
    fill="x",
    padx=150
)

btn_analysis = ctk.CTkButton(
    frame_start,
    text="VIEW ANALYSIS",
    command=show_analysis,
    height=45,
    corner_radius=8,
    fg_color="transparent",
    border_width=2,
    text_color=COLOR_CYAN,
    border_color=COLOR_CYAN,
    hover_color="#082F49",
    font=("Consolas", 15, "bold")
)

btn_analysis.pack(
    pady=8,
    fill="x",
    padx=150
)

btn_reset = ctk.CTkButton(
    frame_start,
    text="RESET PROGRESS",
    command=reset_progress,
    height=45,
    corner_radius=8,
    fg_color="transparent",
    border_width=2,
    text_color="#F59E0B",
    border_color="#F59E0B",
    hover_color="#3A2E13",
    font=("Consolas", 15, "bold")
)

btn_reset.pack(
    pady=8,
    fill="x",
    padx=150
)

btn_close = ctk.CTkButton(
    frame_start,
    text="CLOSE",
    command=close_app,
    height=45,
    corner_radius=8,
    fg_color="transparent",
    border_width=2,
    text_color="#6B7280",
    border_color="#374151",
    hover_color="#1F2937",
    font=("Consolas", 15, "bold")
)

btn_close.pack(
    pady=8,
    fill="x",
    padx=150
)


# ==========================================
# WIDGETS: QUIZ SCREEN
# ==========================================

frame_quiz = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

lbl_progress = ctk.CTkLabel(
    frame_quiz,
    text="Question 1 of 10",
    font=("Consolas", 14),
    text_color=COLOR_CYAN
)

lbl_progress.pack(pady=(20, 5))

progress_bar = ctk.CTkProgressBar(
    frame_quiz,
    height=10,
    corner_radius=5,
    progress_color=COLOR_PURPLE
)

progress_bar.set(0)

progress_bar.pack(
    pady=(0, 40),
    fill="x",
    padx=100
)

frame_word = ctk.CTkFrame(
    frame_quiz,
    fg_color=COLOR_PANEL,
    corner_radius=15,
    border_width=1,
    border_color="#374151"
)

frame_word.pack(
    fill="x",
    padx=100,
    pady=20
)

lbl_word = ctk.CTkLabel(
    frame_word,
    text="Loading...",
    font=("Helvetica", 65, "bold")
)

lbl_word.pack(pady=40)

entry_answer = ctk.CTkEntry(
    frame_quiz,
    placeholder_text="Enter English Translation...",
    height=55,
    corner_radius=10,
    font=("Helvetica", 20),
    justify="center",
    border_color=COLOR_PURPLE
)

app.bind("<Return>", process_answer)

frame_quiz_buttons = ctk.CTkFrame(
    frame_quiz,
    fg_color="transparent"
)

frame_quiz_buttons.columnconfigure(0, weight=1)
frame_quiz_buttons.columnconfigure(1, weight=1)

btn_submit = ctk.CTkButton(
    frame_quiz_buttons,
    text="SUBMIT",
    command=process_answer,
    height=50,
    corner_radius=10,
    font=("Consolas", 18, "bold"),
    fg_color=COLOR_CYAN,
    text_color="black",
    hover_color="#00B5DB"
)

btn_submit.grid(
    row=0,
    column=0,
    padx=(0, 10),
    sticky="ew"
)

btn_skip = ctk.CTkButton(
    frame_quiz_buttons,
    text="SKIP",
    command=skip_question,
    height=50,
    corner_radius=10,
    font=("Consolas", 18, "bold"),
    fg_color="transparent",
    border_width=2,
    text_color=COLOR_CYAN,
    border_color=COLOR_CYAN,
    hover_color="#082F49"
)

btn_skip.grid(
    row=0,
    column=1,
    padx=(10, 0),
    sticky="ew"
)

btn_return = ctk.CTkButton(
    frame_quiz,
    text="RETURN TO DASHBOARD",
    command=return_to_start,
    height=50,
    corner_radius=10,
    fg_color=COLOR_PANEL,
    border_width=1,
    border_color="#6B7280",
    font=("Consolas", 16, "bold")
)

lbl_feedback = ctk.CTkLabel(
    frame_quiz,
    text="",
    font=("Helvetica", 20, "bold")
)

lbl_feedback.pack(pady=20)


# ==========================================
# WIDGETS: ANALYSIS SCREEN
# ==========================================

frame_analysis = ctk.CTkFrame(
    app,
    fg_color="transparent"
)

lbl_analysis_title = ctk.CTkLabel(
    frame_analysis,
    text="WEAKNESS ANALYSIS",
    font=("Consolas", 24, "bold"),
    text_color=COLOR_PINK
)

lbl_analysis_title.pack(pady=(20, 20))

textbox_weak_words = ctk.CTkTextbox(
    frame_analysis,
    width=600,
    height=350,
    font=("Helvetica", 18),
    fg_color=COLOR_PANEL,
    border_width=1,
    border_color="#374151",
    corner_radius=15
)

textbox_weak_words.pack(pady=20)

btn_back = ctk.CTkButton(
    frame_analysis,
    text="BACK TO DASHBOARD",
    command=return_to_start,
    height=50,
    corner_radius=8,
    fg_color="transparent",
    border_width=2,
    text_color=COLOR_CYAN,
    border_color=COLOR_CYAN,
    hover_color="#082F49",
    font=("Consolas", 16, "bold")
)

btn_back.pack(
    pady=20,
    fill="x",
    padx=250
)


# ==========================================
# START APP
# ==========================================

app.mainloop()
