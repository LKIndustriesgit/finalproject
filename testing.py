from transformers import pipeline

# Load the question-answering model
qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

# Define a static context (you can also load this from a file or expand it)
with open("context.txt", "r") as file:
    context = file.read()

print("📚 Leuphana QA Chatbot")
print("Type 'exit' to quit.")
print("--------------------------------------------------")

while True:
    question = input("You: ")
    if question.lower() in ['exit', 'quit']:
        print("Goodbye!")
        break

    result = qa_pipeline({
        'context': context,
        'question': question
    })

    print("Bot:", result['answer'])