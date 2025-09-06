# Q & A Data would be better like FAQ because it is already structured in the right way
from transformers import pipeline
import torch


# --- Step 1: Match relevant rows for each question ---
def get_context(df, question):
    # Lowercase question for matching
    q = question.lower()
    # Try to match on topic/en/enumeration (works for your structure)
    mask = df['topic/en/enumeration'].str.lower().str.contains(q, na=False)
    # If no hit, try matching on details
    if not mask.any():
        mask = df['details'].str.lower().str.contains(q, na=False)
    # Combine all matched rows' details into one string
    if mask.any():
        return " ".join(df[mask]['details'].dropna().astype(str).tolist())
    # Fallback: full context (can restrict length if needed)
    return " ".join(df['details'].dropna().astype(str).tolist())

device = "mps" if torch.has_mps else "cpu"

print(f"Using device: {device}")

# Load the question-answering pipeline with device setting
qa_pipeline = pipeline(
    "question-answering",
    model="deepset/xlm-roberta-base-squad2",
    device=0 if device == "mps" else -1,
    torch_dtype=torch.float32  # Force float32 to avoid bfloat16 issues
)

print("📚 Leuphana QA Chatbot")
print("Type 'exit' to quit.")
print("--------------------------------------------------")

with open("../text/own text/music", "r") as file:
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





