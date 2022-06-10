import nltk
from transformers import pipeline

def init_pipeline():
    return pipeline(
        "question-answering",
        model="deutsche-telekom/bert-multi-english-german-squad2",
        tokenizer="deutsche-telekom/bert-multi-english-german-squad2",
    )

def init_nltk():
    nltk.download('punkt')

if __name__ == '__main__':

    init_pipeline()
    init_nltk()