# Used https://www.pythontutorial.net/tkinter/tkinter-window/ tutorial for tkinter

from transformers import pipeline
import torch
import tkinter as tk
import platform

system_type = platform.system()
root = tk.Tk()
root.title("LeuphAI Q&A Chatbot DEMO: music centre")
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 1000


screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()


center_x = int(screen_width/2 - WINDOW_WIDTH / 2)
center_y = int(screen_height/2 - WINDOW_HEIGHT / 2)


root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{center_x}+{center_y}')
if system_type == 'Windows':
    root.iconbitmap('media/leuphana_logo.ico')
else:
    try:

        photo = tk.PhotoImage(file='media/leuphana_logo.png')
        root.iconphoto(False, photo)
    except tk.TclError:
        print("icon file not found.")
root.mainloop()


device = "mps" if torch.has_mps else "cpu"

print(f"Using device: {device}")

# Load the question-answering pipeline with device setting
qa_pipeline = pipeline(
    "question-answering",
    model="deepset/xlm-roberta-base-squad2",
    device=0 if device == "mps" else -1,
    torch_dtype=torch.float32  # Force float32 to avoid bfloat16 issues (I kept getting errors, so I found this fix after asking ChatGPT)
)

print("📚 Leuphana QA Chatbot")
print("Type 'exit' to quit.")
print("--------------------------------------------------")

with open("text/own text/music", "r") as file:
    context = file.read()
while True:
    user_question = input("You: ")
    if user_question.lower() in ['exit', 'quit']:
        print("Goodbye!")
        break
    else:

        result = qa_pipeline(
            context = context,
            question=user_question,
        )

        print("Bot:", result['answer'])





