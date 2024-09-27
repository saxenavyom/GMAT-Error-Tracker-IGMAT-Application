import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, Toplevel
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import json

# Load existing data if available
try:
    data = pd.read_csv('gmat_data.csv')
except FileNotFoundError:
    data = pd.DataFrame(columns=['Topic', 'Correct', 'Incorrect', 'Avg Pace'])

# Load and save custom questions from/to a JSON file
CUSTOM_QUESTIONS_FILE = 'custom_questions.json'
VOCAB_FLASHCARDS_FILE = 'vocab_flashcards.json'

def load_custom_questions():
    try:
        with open(CUSTOM_QUESTIONS_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_custom_questions(questions):
    with open(CUSTOM_QUESTIONS_FILE, 'w') as file:
        json.dump(questions, file)

def load_vocab_flashcards():
    try:
        with open(VOCAB_FLASHCARDS_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_vocab_flashcards(flashcards):
    with open(VOCAB_FLASHCARDS_FILE, 'w') as file:
        json.dump(flashcards, file)

custom_questions = load_custom_questions()
vocab_flashcards = load_vocab_flashcards()

# GMAT Error Log Tracker Functions
def save_data():
    data.to_csv('gmat_data.csv', index=False)

def add_entry():
    try:
        correct = int(correct_entry.get())
        incorrect = int(incorrect_entry.get())
        minutes = int(minutes_entry.get())
        seconds = int(seconds_entry.get())
        avg_pace = minutes * 60 + seconds  # Convert time to total seconds
        topic = topic_var.get()
        new_data = {'Topic': topic, 'Correct': correct, 'Incorrect': incorrect, 'Avg Pace': avg_pace}
        data.loc[len(data)] = new_data
        save_data()
        correct_entry.delete(0, tk.END)
        incorrect_entry.delete(0, tk.END)
        minutes_entry.delete(0, tk.END)
        seconds_entry.delete(0, tk.END)
    except ValueError:
        messagebox.showwarning("Invalid Input", "Please enter valid numbers for all fields.")

def undo_last_entry():
    if not data.empty:
        data.drop(data.tail(1).index, inplace=True)
        save_data()
    else:
        messagebox.showinfo("Info", "No more entries to undo.")

def open_data_form():
    data_form.deiconify()

def create_analysis_window():
    global analysis_window
    analysis_window = tk.Toplevel(root)
    analysis_window.title("Data Analysis")
    analysis_window.geometry("1000x600")
    global analysis_frame
    analysis_frame = ttk.Frame(analysis_window)
    analysis_frame.pack(fill='both', expand=True)
    plot_data()  # Initially plot data when the window is created

def open_analysis_form():
    if data.empty:
        messagebox.showinfo("No Data", "No data available to display charts. Please add some entries first.")
        return
    try:
        analysis_window.deiconify()  # Try to open the existing window
    except (NameError, tk.TclError):  # If the window does not exist or is destroyed
        create_analysis_window()  # Recreate the analysis window

def plot_data():
    for widget in analysis_frame.winfo_children():
        widget.destroy()

    canvas_frame = tk.Frame(analysis_frame)
    canvas_frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(canvas_frame)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    x_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
    x_scroll.pack(side=tk.BOTTOM, fill="x")

    y_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
    y_scroll.pack(side=tk.RIGHT, fill="y")

    canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

    plot_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=plot_frame, anchor="nw")

    topics = data['Topic'].unique()

    # Pie charts for each topic
    for topic in topics:
        topic_data = data[data['Topic'] == topic]
        fig, ax = plt.subplots()
        sums = topic_data[['Correct', 'Incorrect']].sum()
        ax.pie(sums, labels=['Correct', 'Incorrect'], autopct='%1.1f%%', startangle=90, colors=['green', 'red'])
        ax.set_title(f'{topic} Correct vs Incorrect')
        fig.tight_layout()

        canvas_fig = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas_fig.draw()
        canvas_fig.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        plt.close(fig)

    # Overall bar graphs
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))  # Adjust the figsize as needed for your screen
    data.groupby('Topic')['Correct'].sum().plot(kind='bar', ax=axs[0], color='blue', title='Total Correct Questions')
    data.groupby('Topic')['Incorrect'].sum().plot(kind='bar', ax=axs[1], color='red', title='Total Incorrect Questions')
    data.groupby('Topic')['Avg Pace'].mean().plot(kind='bar', ax=axs[2], color='purple', title='Average Pace (seconds)')
    fig.tight_layout()

    canvas_fig_overall = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas_fig_overall.draw()
    canvas_fig_overall.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    plt.close(fig)

    plot_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))  # Ensure the scrollable area includes all the generated content

# Custom Question Functions
def add_custom_question():
    question = simpledialog.askstring("New Question", "Enter your question:", parent=root)
    answer = simpledialog.askstring("New Question", "Enter the answer:", parent=root)
    if question and answer:
        custom_questions.append({"question": question, "answer": answer})
        save_custom_questions(custom_questions)
        messagebox.showinfo("Success", "Question added successfully.")

def delete_custom_question():
    question_to_delete = simpledialog.askstring("Delete Question", "Enter the question to delete:", parent=root)
    for question in custom_questions:
        if question["question"] == question_to_delete:
            custom_questions.remove(question)
            save_custom_questions(custom_questions)
            messagebox.showinfo("Success", "Question deleted successfully.")
            return
    messagebox.showinfo("Not Found", "Question not found.")

def start_custom_practice():
    if custom_questions:
        questions = [(q["question"], q["answer"]) for q in custom_questions]
        open_practice_window(questions, "Custom Practice")
    else:
        messagebox.showinfo("Custom Practice", "No custom questions available. Please add some first.")

# Exponent and Multiplication Functions
def exponent_to_superscript(base, exp):
    superscripts = {"1": "¹", "2": "²", "3": "³", "4": "⁴", "5": "⁵",
                    "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "0": "⁰"}
    exp_str = ''.join(superscripts.get(char, char) for char in str(exp))
    return f"{base}{exp_str}"

def generate_exponent_questions():
    questions = [(2, exp) for exp in range(3, 10)]  # 2^3 to 2^9
    questions.extend([(i, 2) for i in range(2, 10)])  # 2^2 to 9^2
    questions.extend([(i, j) for i in range(3, 5) for j in range(2, 5)])  # 3^2 to 4^4
    questions.extend([(i, j) for i in range(5, 6) for j in range(2, 5)])  # 5^2 to 5^4
    questions.extend([(i, 3) for i in range(6, 10)])  # 6^3 to 9^3
    questions.extend([(i, 2) for i in range(10, 26)])  # 10^2 to 25^2
    random.shuffle(questions)
    return questions[:15]  # Return only 15 random questions

def generate_multiplication_questions(min_table, max_table):
    return [(random.randint(min_table, max_table), random.randint(1, 10)) for _ in range(20)]

def open_practice_window(questions, title):
    practice_window = tk.Toplevel(root)
    practice_window.title(title)
    practice_window.geometry("400x250")

    question_label = tk.Label(practice_window, text="", font=("Helvetica", 16))
    question_label.pack(pady=(10, 5))
    
    answer_label = tk.Label(practice_window, text="", font=("Helvetica", 16))
    answer_label.pack(pady=(5, 10))

    def show_question():
        if questions:
            question, answer = questions.pop(0)
            question_label.config(text=f"What is {question}?")
            show_answer_button.config(command=lambda: answer_label.config(text=f"The answer is: {answer}"))
        else:
            messagebox.showinfo(title, "You have completed all questions!")
            practice_window.destroy()

    show_answer_button = tk.Button(practice_window, text="Show Answer", command=None, bg="#4CAF50", fg="white", font=('Helvetica', 12))
    show_answer_button.pack(pady=5)
    
    next_button = tk.Button(practice_window, text="Next", command=show_question, bg="#2196F3", fg="white", font=('Helvetica', 12))
    next_button.pack(pady=10)

    show_question()

def start_exponents():
    questions = [(exponent_to_superscript(base, exp), f"{base**exp}") for base, exp in generate_exponent_questions()]
    open_practice_window(questions, "Exponent Practice")

def start_multiplication_tables():
    min_table = simpledialog.askinteger("Input", "Enter the starting table (e.g., 1):", parent=root)
    max_table = simpledialog.askinteger("Input", "Enter the ending table (e.g., 20):", parent=root)
    if min_table is not None and max_table is not None:
        questions = [(f"{x} * {y}", f"{x*y}") for x, y in generate_multiplication_questions(min_table, max_table)]
        open_practice_window(questions, "Multiplication Practice")

def run_test():
    all_questions = [(exponent_to_superscript(base, exp), f"{base**exp}") for base, exp in generate_exponent_questions()]
    all_questions.extend([(f"{x} * {y}", f"{x*y}") for x, y in generate_multiplication_questions(1, 20)])
    all_questions.extend([(q["question"], q["answer"]) for q in custom_questions])
    random.shuffle(all_questions)
    test_questions = all_questions[:35]

    test_window = tk.Toplevel(root)
    test_window.title("Math Test")
    test_window.geometry("400x300")

    current_question = tk.StringVar(test_window)
    user_answer = tk.StringVar(test_window)
    timer_label = tk.Label(test_window, text="20", font=("Helvetica", 16))
    timer_label.pack(pady=(10, 5))
    question_label = tk.Label(test_window, textvariable=current_question, font=("Helvetica", 16))
    question_label.pack(pady=(10, 5))
    answer_entry = tk.Entry(test_window, textvariable=user_answer, font=("Helvetica", 16))
    answer_entry.pack(pady=(5, 10))
    next_button = tk.Button(test_window, text="Next", command=lambda: submit_and_next(), bg="#2196F3", fg="white", font=('Helvetica', 12))
    next_button.pack(pady=5)

    results = []
    current_index = 0
    timer_id = None

    def countdown(t):
        nonlocal timer_id
        if t > 0:
            timer_label.config(text=str(t))
            timer_id = test_window.after(1000, countdown, t-1)
        else:
            submit_and_next()

    def submit_and_next():
        nonlocal current_index, timer_id
        if timer_id:
            test_window.after_cancel(timer_id)
            timer_id = None
        if current_index < len(test_questions):
            question, correct_answer = test_questions[current_index]
            user_answer_value = user_answer.get()
            results.append((question, user_answer_value, correct_answer))
            user_answer.set("")
            current_index += 1
            if current_index < len(test_questions):
                show_question()
            else:
                finish_test()

    def show_question():
        if current_index < len(test_questions):
            current_question.set(test_questions[current_index][0])
            timer_label.config(text="20")
            countdown(20)

    def finish_test():
        correct_count = sum(1 for q, u, c in results if u == c)
        summary = f"Test completed. Score: {correct_count}/{len(results)}"
        incorrect_summary = "\n".join(f"{q}: Your answer: {u} (Correct: {c})" for q, u, c in results if u != c)
        messagebox.showinfo("Test Summary", f"{summary}\nIncorrect answers:\n{incorrect_summary}")
        test_window.destroy()

    show_question()

# Vocabulary Flashcard Functions
def add_flashcard():
    word = simpledialog.askstring("Input", "Enter the word:", parent=root)
    if word:
        meaning = simpledialog.askstring("Input", "Enter the meaning:", parent=root)
        if meaning:
            vocab_flashcards[word] = meaning
            save_vocab_flashcards(vocab_flashcards)
            messagebox.showinfo("Update", f"Added flashcard for: {word}")

def delete_flashcard():
    if not vocab_flashcards:
        messagebox.showinfo("Empty", "No flashcards to delete.")
        return
    word = simpledialog.askstring("Input", "Enter the word to delete:", parent=root)
    if word in vocab_flashcards:
        del vocab_flashcards[word]
        save_vocab_flashcards(vocab_flashcards)
        messagebox.showinfo("Update", f"Deleted flashcard for: {word}")
    else:
        messagebox.showinfo("Not found", "Flashcard not found.")

def review_flashcards():
    if not vocab_flashcards:
        messagebox.showinfo("Empty", "No flashcards to review.")
        return
    
    review_window = Toplevel(root)
    review_window.title("Review Flashcards")
    review_window.configure(bg='#FFF59D')  # A light yellow for better visibility

    words = list(vocab_flashcards.keys())
    random.shuffle(words)
    word_iter = iter(words)
    current_word = next(word_iter, None)

    word_label = tk.Label(review_window, text=current_word if current_word else "", font=('Helvetica', 18), bg='#FFF59D', wraplength=480)
    word_label.pack(pady=(20, 10), padx=10, fill='both', expand=True)

    def show_answer():
        if current_word:
            answer_label.config(text=vocab_flashcards[current_word])

    def next_card():
        nonlocal current_word
        current_word = next(word_iter, None)
        if current_word:
            word_label.config(text=current_word)
            answer_label.config(text="")
        else:
            messagebox.showinfo("Done", "No more flashcards.")
            review_window.destroy()

    answer_button = tk.Button(review_window, text="Show Answer", command=show_answer, bg="#4CAF50", fg="white", font=('Helvetica', 12))
    next_button = tk.Button(review_window, text="Next", command=next_card, bg="#2196F3", fg="white", font=('Helvetica', 12))
    answer_label = tk.Label(review_window, text="", font=('Helvetica', 18), bg='#FFF59D')

    answer_button.pack()
    answer_label.pack(pady=(10, 20), padx=10, fill='both', expand=True)
    next_button.pack()

# Main GUI setup
root = tk.Tk()
root.title("Integrated GMAT and Math Practice App")
root.geometry("400x600")
root.configure(bg='#F0F0F0')

style = ttk.Style()
style.configure('TButton', font=('Helvetica', 12), padding=10, background="#4CAF50", foreground="white")

# Navigation Buttons on the Main Window
input_button = tk.Button(root, text="Input Data", command=open_data_form, bg="#4CAF50", fg="white", font=('Helvetica', 12))
input_button.pack(fill='x', pady=5)
analysis_button = tk.Button(root, text="See Analysis", command=open_analysis_form, bg="#4CAF50", fg="white", font=('Helvetica', 12))
analysis_button.pack(fill='x', pady=5)
undo_button = tk.Button(root, text="Undo Last Entry", command=undo_last_entry, bg="#4CAF50", fg="white", font=('Helvetica', 12))
undo_button.pack(fill='x', pady=5)

multiplication_button = tk.Button(root, text="Multiplication Tables", command=start_multiplication_tables, bg="#4CAF50", fg="white", font=('Helvetica', 12))
multiplication_button.pack(pady=5, fill='x')

exponents_button = tk.Button(root, text="Exponents", command=start_exponents, bg="#4CAF50", fg="white", font=('Helvetica', 12))
exponents_button.pack(pady=5, fill='x')

add_question_button = tk.Button(root, text="Add Custom Question", command=add_custom_question, bg="#4CAF50", fg="white", font=('Helvetica', 12))
add_question_button.pack(pady=5, fill='x')

delete_question_button = tk.Button(root, text="Delete Custom Question", command=delete_custom_question, bg="#4CAF50", fg="white", font=('Helvetica', 12))
delete_question_button.pack(pady=5, fill='x')

custom_practice_button = tk.Button(root, text="Custom Practice", command=start_custom_practice, bg="#4CAF50", fg="white", font=('Helvetica', 12))
custom_practice_button.pack(pady=5, fill='x')

test_button = tk.Button(root, text="Test", command=run_test, bg="#4CAF50", fg="white", font=('Helvetica', 12))
test_button.pack(pady=5, fill='x')

add_flashcard_button = tk.Button(root, text="Add Flashcard", command=add_flashcard, bg="#4CAF50", fg="white", font=('Helvetica', 12))
add_flashcard_button.pack(pady=5, fill='x')

review_flashcard_button = tk.Button(root, text="Review Flashcards", command=review_flashcards, bg="#4CAF50", fg="white", font=('Helvetica', 12))
review_flashcard_button.pack(pady=5, fill='x')

delete_flashcard_button = tk.Button(root, text="Delete Flashcard", command=delete_flashcard, bg="#4CAF50", fg="white", font=('Helvetica', 12))
delete_flashcard_button.pack(pady=5, fill='x')

# Data Entry Form Setup
data_form = tk.Toplevel(root)
data_form.title("Data Entry Form")
data_form.geometry("300x300")
data_form.configure(bg='#F0F0F0')
data_form.withdraw()

# Entry widgets and labels in data_form, arranged neatly
entry_frame = ttk.Frame(data_form)
entry_frame.pack(pady=10, padx=10)

topic_var = tk.StringVar()
topic_label = ttk.Label(entry_frame, text="Topic:")
topic_label.pack(fill='x')
topic_dropdown = ttk.Combobox(entry_frame, textvariable=topic_var, values=[
    "Value, Order, and Factors", "Algebra, Equalities, and Inequalities",
    "Rates, Ratios, and Percents", "Statistics", "Counting", "Probability",
    "Sequence and Series", "Reading Comprehension", "Critical Reasoning",
    "Data Sufficiency", "Integral Reasoning"], state='readonly')
topic_dropdown.pack(fill='x')

correct_label = ttk.Label(entry_frame, text="Correct Questions:")
correct_label.pack(fill='x')
correct_entry = ttk.Entry(entry_frame)
correct_entry.pack(fill='x')

incorrect_label = ttk.Label(entry_frame, text="Incorrect Questions:")
incorrect_label.pack(fill='x')
incorrect_entry = ttk.Entry(entry_frame)
incorrect_entry.pack(fill='x')

avg_pace_label = ttk.Label(entry_frame, text="Avg Pace (min:sec):")
avg_pace_label.pack(fill='x')
pace_frame = ttk.Frame(entry_frame)
pace_frame.pack(fill='x')
minutes_entry = ttk.Entry(pace_frame, width=5)
minutes_entry.pack(side='left', padx=(0, 2))
seconds_entry = ttk.Entry(pace_frame, width=5)
seconds_entry.pack(side='left', padx=(2, 0))

add_button = tk.Button(data_form, text="Add Entry", command=add_entry, bg="#4CAF50", fg="white", font=('Helvetica', 12))
add_button.pack(pady=10)

root.mainloop()
