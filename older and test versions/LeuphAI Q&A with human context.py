# Used https://www.pythontutorial.net/tkinter/tkinter-window/ tutorial for tkinter

from transformers import pipeline
import torch
import tkinter as tk
from tkinter import ttk
import platform
import threading



system_type = platform.system()
root = tk.Tk()
root.title("LeuphAI Q&A Chatbot DEMO: music centre")
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 1000
input_text_height = 8  # Number of lines for input
button_pressed = False
user_question = ""
#main_text = "test"
#input_text_height = WINDOW_HEIGHT // 3

def enter(event=None):
    global button_pressed
    button_pressed = True
    global user_question
    user_question = input_text.get("1.0", tk.END)

root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")


text = tk.Text(root)
text.grid(row=0, column=0, sticky="nsew")
text.insert(tk.END, "Welcome to this demo version of a Q&A Bot!\n Write any question concerning the range of music activities offered by the Leuphana University Lüneburg. \n")
text.tag_add("colour", "1.0", "2.105")
text.tag_config("colour", foreground="green")
text['state'] = 'disabled'

#text.insert(
#    index='1.0',
#    chars= main_text
#)


input_text = tk.Text(root)
input_text.grid(row=1, column=0, sticky="ew")
input_text['state'] = 'normal'
input_text.bind('<Return>', enter)


button = ttk.Button(
   root,
   text="ENTER",
   command=enter
)
button.config(command=enter)
button.grid(row=1, column=1, sticky="ew")
button.state(['disabled'])

root.grid_rowconfigure(0, weight=3)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()


center_x = int(screen_width/2 - WINDOW_WIDTH / 2)
center_y = int(screen_height/2 - WINDOW_HEIGHT / 2)


root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{center_x}+{center_y}')
if system_type == 'Windows':
    root.iconbitmap('media/leuphana_logo_icon.ico')
else:
    try:

        photo = tk.PhotoImage(file='../media/leuphana_logo_icon.png')
        root.iconphoto(False, photo)
    except tk.TclError:
        print("icon file not found.")



device = "mps" if torch.has_mps else "cpu"

print(f"Using device: {device}")


def ai_loop():
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

    with open("../media/text/own text/music", "r") as file:
        context = file.read()
    while True:
        global user_question
        global button_pressed
        #user_question = input("You: ")
        #if input_text.get("1.0", tk.END) != "":
            #button.state(['!disabled'])
        #else:
            #button.state(['disabled'])
        if button_pressed:

            global result
            result = qa_pipeline(
                context = context,
                question=user_question,
            )
            print("Bot:", result['answer'])
            root.after(0, post_response, user_question, result['answer'])
            input_text.delete("1.0", tk.END)
            button_pressed = False

def post_response(user_question, answer):
    text['state'] = 'normal'
    text.insert(tk.END, f"You: {user_question}\nBot: {answer}\n")
    text['state'] = 'disabled'

def check_input_field():
    content = input_text.get("1.0", tk.END).strip()
    if content:
        button.state(['!disabled'])
    else:
        button.state(['disabled'])
    root.after(100, check_input_field)

threading.Thread(target=ai_loop, daemon=True).start()
threading.Thread(target=check_input_field, daemon=True).start()
root.mainloop()



