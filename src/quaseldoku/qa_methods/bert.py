from torch import rand
from transformers import pipeline

def init_model_and_tokenizer(model="deutsche-telekom/bert-multi-english-german-squad2", tokenizer="deutsche-telekom/bert-multi-english-german-squad2"):
    return pipeline(
        "question-answering",
        model=model,
        tokenizer=tokenizer,
)

def query(query: str, context: str, pipeline: pipeline, top_k=5):
    return pipeline(question=query, context=context, top_k=top_k)


