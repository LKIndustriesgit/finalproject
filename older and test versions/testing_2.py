#pytorch
#framework for training AI models
#Ollama
#for locally hosted models
#also supports API
#little demo of model (Potential usage, i.e. answers and questions)
from transformers import pipeline, set_seed

generator = pipeline("text-generation", model="utter-project/EuroLLM-1.7B-Instruct")
set_seed(42)

context_style = """
Leuphana College Bachelor's Program – Student Services and Procedures

During your studies at Leuphana College, Student Services provides support for administrative procedures such as...
"""

result = generator(context_style, max_length=200, num_return_sequences=1)

print(result[0]['generated_text'])