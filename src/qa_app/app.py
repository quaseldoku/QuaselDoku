import os
import streamlit as st
import pandas as pd
import nltk
from annotated_text import annotated_text
from quaseldoku.qa_methods import keyword_search
from quaseldoku.helper import find_project_root
from transformers import pipeline


@st.cache
def load_document_base(path):
    return pd.read_csv(path)


@st.experimental_singleton(show_spinner=True)
def init_pipeline():
    print('init pipeline')
    return pipeline(
        "question-answering",
        model="deutsche-telekom/bert-multi-english-german-squad2",
        tokenizer="deutsche-telekom/bert-multi-english-german-squad2",
    )


@st.cache
def init_nltk():
    nltk.download('punkt')


def bert_answer_question(question, paragraph, qa_pipeline, top_k=3):
    return qa_pipeline(question=question, context=paragraph, top_k=top_k)


@st.experimental_memo(show_spinner=False)
def answer_question(question, document_base, search_n_best=3):

    qa_pipeline = init_pipeline()

    # perform keyword search on ecu test index and retrieve best result
    ecu_search_index = find_project_root(os.getcwd()) + '/data/03_primary/search_indices/ecu_test/'
    key_word_res = keyword_search.query(question, ecu_search_index)
    if len(key_word_res['hits']) < 1:
        return []
    
    n_best_hashes = key_word_res['hits'][:search_n_best]
    
    # with retrieved hash look up context, title, etc. in document base
    best_documents = document_base[document_base['Hash'].isin(n_best_hashes)]

    possible_answers = []
    with st.spinner('asking BERT ...'):
        # running text bodies of best n documents through bert model and merge results with document
        for _, row in best_documents.iterrows():
            bert_answers = bert_answer_question(question, row['Body'], qa_pipeline, top_k=3)
            for ba in bert_answers:
                possible_answers.append({**row, **ba})
                
    return sorted(possible_answers, key=lambda x: x['score'], reverse=True)


def render_answer(answer):

    # base link to doku (will be either to web server running doku or local file)
    _base_link = "http://127.0.0.1:5000/"

    h_color = "#8ef"

    title = answer['Title']
    link = _base_link + answer['Filename']
    text = answer['Body']
    bert_answer = answer['answer']
    score = round(answer['score'], 2)

    # append title to link to show correct paragraph
    link += f'#{title.lower()}'

    # format title for display later
    title_display = title.replace('-', ' ')

    # find answer in context in order to highlight substring
    answer_start = text.find(bert_answer)
    answer_end = answer_start + len(bert_answer)

    # highlight answer in context
    _c_prfx = text[:answer_start] 
    _c_sffx = text[answer_end:]

    # show sentence containing the bert answer
    sentences = nltk.sent_tokenize(text, language='german')

    # find sentence containing start token
    token_count = 0
    start_token = answer['start']
    answer_sentence = ''
    for s in sentences:
        token_count += len(s)
        if token_count >= start_token:
            answer_sentence = s
            break

    st.markdown(f'**{answer_sentence}**')
    st.button('nicht die richtige Antwort?')

    annotated_text(
    _c_prfx,
    (bert_answer, str(score), h_color),
    _c_sffx)

    st.markdown("***")
    st.markdown(f'**🔗 Lies mehr dazu im Kapitel [{title_display}]({link})**')


if __name__ == "__main__":

    document_base = load_document_base(find_project_root(os.getcwd()) + '/data/03_primary/doku_paragraphs.csv')
    init_nltk()

    st.markdown('# ECU-Test-Doku Q&A-System')
    text_input = st.text_input(
        "Hier kannst Du eine Frage stellen ...",
        placeholder='Was ist ein Traceschritt?',
        key="text_input",
        on_change=None,
        args=()
    )

    if text_input:
        answers = answer_question(text_input, document_base)
        
        # only render best answer for now
        if len(answers) > 0:
            render_answer(answers[0])
        else:
            st.markdown("*Keine Ergebnisse zu der Suchanfrage gefunden* 😔")


