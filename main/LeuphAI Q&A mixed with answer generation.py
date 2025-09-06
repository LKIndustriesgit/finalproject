# Used https://www.pythontutorial.net/tkinter/tkinter-window/ tutorial for tkinter

#importing the used libraries
import torch    #used for checking users available processing unit (apple m-series chip or cpu)
import tkinter as tk    #for creating the interface
import platform #to check whether user is on mac or windows (few usages)
import threading #to use both the tkinter interface and the AI transformer at the same time
import requests #to stream the AI transformer locally via ollama
import json #for AI transformer assignment
#variables:
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 1000
system_type = platform.system() # for checking system type
input_text_height = 8  # height of input window (Number of lines)
button_pressed = False #standard state for button
user_question = "" #standard empty state for user question
debug = False #for debug

#enter button pressed event function
def enter(event=None):
    global button_pressed   #declare usage of global variable
    button_pressed = True   #set it to true (used in other function)
    global user_question    #declare usage of global variable
    user_question = input_text.get("1.0", tk.END) #change content of AI question to input of tkinter input label

#creating a tkinter window
root = tk.Tk() #name
root.title("LeuphAI Q&A Chatbot DEMO: music centre") #title on top
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}") #size

#images must be assigned after a root window is created
leuphana_image = tk.PhotoImage(file="../media/leuphana_text.png")
enter_image = tk.PhotoImage(file="../media/enter.png") #both images for tkinter

#creating main conversation protocol label
text = tk.Text(root)
text.grid(row=0, column=0, sticky="nsew") #putting it in window order
    #opening text:
text.insert(tk.END, "Welcome to this demo version of a Q&A Bot!\n Write any question concerning the range of music activities offered by the Leuphana University Lüneburg. \n Depending on your devices computing power, the answer generation may take some time, as everything is happening locally. \n")
text.tag_add("colour", "1.0", "2.105") #adding colour to text
text.tag_config("colour", foreground="green") #setting the colour to green
text['state'] = 'disabled' #making the text not editable for user

#putting leuphana logo in empty space for style reasons
leuphana_label = tk.Label(root, image=leuphana_image)
leuphana_label.grid(row=0, column=1, sticky="nsew")

#creating input label for interaction with AI
input_text = tk.Text(root)
input_text.grid(row=1, column=0, sticky="ew")
input_text['state'] = 'normal' #editable
input_text.bind('<Return>', enter) #binding enter function to return button for easier text input

#creating enter button
button = tk.Button(
   root,
   image=enter_image,   #with image
   command=enter    #and enter function as the command
)
button.grid(row=1, column=1, sticky="ew") #put in grid order
button.config(state="disabled") #disabled on start so user cant enter blank text

#for resizing geometry:
root.grid_rowconfigure(0, weight=3) #protocol row most important (grows 3x as much vertically as input row)
root.grid_rowconfigure(1, weight=1) #input row
root.grid_columnconfigure(0, weight=1) #only first column grows, as the 2nd only has images

screen_width = root.winfo_screenwidth() #windows' width as variable for geometry
screen_height = root.winfo_screenheight() #windows' height


center_x = int(screen_width/2 - WINDOW_WIDTH / 2) #determining centre of screen
center_y = int(screen_height/2 - WINDOW_HEIGHT / 2) #determining centre of screen


root.geometry(f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{center_x}+{center_y}') #geometry of window

#logo icon for tkinter app:
#determining OS
if system_type == 'Windows':
    root.iconbitmap('media/leuphana_logo_icon.ico')
else:
    try:
        photo = tk.PhotoImage(file='../media/leuphana_logo_icon.png') #png for all other OS except windows
        root.iconphoto(False, photo)
    except tk.TclError:
        print("icon file not found.")


#checking microchip architecture; if m series chip, using it, else use cpu
device = "mps" if torch.has_mps else "cpu"
if debug == True:
    print(f"Using device: {device}")



#running the question through the ollama transformer (otherwise, the 4 bit version of mistral would not run on my computer)
#put in a separate function from main, to not block UI interaction with answer generation
def ask_ollama(context, question):
    prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:" #loading in the Q&A context as a prompt
    response = requests.post(
        "http://localhost:11434/api/generate",  #locally connecting to ollama transformer
        json={
            "model": "mistral", #finally decided on MistralAI, as it both gave back good results and conforms to european data standards
            "prompt": prompt
        },
        stream=True  # using streaming of answer in smaller chunks as it is supposedly faster on slow computers
    )

    answer = "" #empty answer string
    for line in response.iter_lines(): #getting all streamed lines
        if line:    #if there is content
            data = json.loads(line) #load it
            # Each line chunk has a 'response' field with newly generated text
            answer += data.get('response', '')
            if data.get('done', False): #if data has tag 'done', stop
                break
    return answer.strip()

#main loop (called ai_loop to avoid confusion with tks mainloop() )
def ai_loop():
    if debug:   #to view AI in console
        print("📚 Leuphana QA Chatbot (Ollama)")
        print("Type 'exit' to quit.")
        print("--------------------------------------------------")
    #opening the prepared context
    with open("../media/text/own text/music", "r") as file:
        context = file.read()

    global user_question #declaring the variable global is important to distinct from function-only vars
    while True:
        global button_pressed
        if button_pressed:  #only taking the content of the input field if the button is pressed
            q = user_question.strip()   #for cleaning up tkinter output
            answer = ask_ollama(context, q) #calling the transformer function with the user input from tkinter
            if debug:
                print("Bot:", answer)
            root.after(0, post_response, q, answer) #to make the response posting possible within tkinters logic
            input_text.delete("1.0", tk.END) #clearing the tkinter input field
            button_pressed = False #unpressing the button

#response posting function (as used above)
def post_response(user_question, answer):
    text['state'] = 'normal'    #making the main conversational protocol editable
    text.insert(tk.END, f"You: {user_question}\nBot: {answer}\n") #inserting protocol (+ newline to separate requests)
    text['state'] = 'disabled' #making protocol not editable again so user cant manipulate it

#function to make enter button only pressable if content in input field
def check_input_field():
    content = input_text.get("1.0", tk.END).strip() #get content
    if content: #check for content
        button.config(state="normal")
    else:
        button.config(state="disabled")
    root.after(100, check_input_field) #check every 100 milliseconds

#threading logic required as tkinter mainloop() logic prevents any code after from happening until tkinter is closed
threading.Thread(target=ai_loop, daemon=True).start()
threading.Thread(target=check_input_field, daemon=True).start()
root.mainloop() #main tkinter loop

