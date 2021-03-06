import os
import streamlit as st
import pandas as pd
import nltk
import argparse

from transformers import pipeline
from annotated_text import annotated_text
from quaseldoku.qa_methods import keyword_search


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


def bert_answer_question(question, paragraph, qa_pipeline, top_k=3):
    return qa_pipeline(question=question, context=paragraph, top_k=top_k)


@st.experimental_memo(show_spinner=False)
def answer_question(question, document_base, ecu_search_index, search_n_best=3):

    # needs to initialized here because cant be hashed and therefore not used as parameter to call this function
    # which is necessary when using the experimental_memo decorator
    qa_pipeline = init_pipeline()

    # perform keyword search on ecu test index and retrieve best result
    key_word_res = keyword_search.query(question, ecu_search_index)
    if len(key_word_res['hits']) < 1:
        return []
    
    n_best_hashes = key_word_res['hits'][:search_n_best]
    
    # with retrieved hash look up context, title, etc. in document base
    best_documents = document_base[document_base['Hash'].isin(n_best_hashes)]

    # running text bodies of best n documents through bert model and merge results with document
    possible_answers = []
    with st.spinner('asking BERT ...'):
        for _, row in best_documents.iterrows():
            bert_answers = bert_answer_question(question, row['Body'], qa_pipeline, top_k=3)
            for ba in bert_answers:
                possible_answers.append({**row, **ba})

    # sort answers according to bert score
    possible_answers = sorted(possible_answers, key=lambda x: x['score'], reverse=True)

    # find sentence containing the answer for every bert answer and only keep the best one for every unique sentence
    selected_answers = []
    for pa in possible_answers:
        # find sentence in context containing answer
        sentences = nltk.sent_tokenize(pa['Body'], language='german')
        token_count = 0
        start_token = pa['start']
        answer_sentence = ''
        for s in sentences:
            token_count += len(s)
            if token_count >= start_token:
                answer_sentence = s
                break
        # if sentence already in answer dont keep this answer
        matching_answers = [a for a in selected_answers if a['sentence'] == answer_sentence]
        if len(matching_answers) > 0:
            continue
        else:
            selected_answers.append({'sentence': answer_sentence, **pa})

    # reset answer counter because new answer were generated                
    st.session_state.answer_counter = 0

    return selected_answers


def render_answer(answer, doku_server_url):

    # base link to doku (will be either to web server running doku or local file)
    h_color = "#31ab0f"

    title = answer['Title']
    link = doku_server_url + answer['Filename']
    text = answer['Body']
    bert_answer = answer['answer']
    score = round(answer['score'], 2)
    sentence = answer['sentence']

    # append title to link to show correct paragraph
    link += f'#{title.lower()}'

    # format title for display later
    title_display = title.replace('-', ' ')

    # find answer in sentence in order to highlight substring
    answer_start = sentence.find(bert_answer)
    answer_end = answer_start + len(bert_answer)

    # highlight answer in context
    _c_prfx = sentence[:answer_start] 
    _c_sffx = sentence[answer_end:]

    annotated_text(
    "\""+_c_prfx,
    (bert_answer, str(score), h_color),
    _c_sffx + "\"")

    # create vertical space
    st.markdown("\n")

    with st.expander(f"(klicke um zugeh??rigen Abschnitt anzuzeigen)"):
        st.markdown(f'*{text}*')
    st.markdown(f'*????  F??r weiterf??hrende Information siehe das Kapitel [{title_display}]({link}) in der ECU-Test-Dokumentation*')


def parse_args():

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--document-base', type=str, help="path to .csv holding the document base aka parsed ecu test doku")
    parser.add_argument('--search-index', type=str, help="path to folder containing the search index for ecu test doku")
    parser.add_argument('--doku-url', type=str, help="url and port where server hosting the doku is running on")
    try:
        return parser.parse_args()
    except SystemExit as e:
        os._exit(e.code)


if __name__ == "__main__":

    args = parse_args()

    # init pipeline once here so model gets cached on startup
    init_pipeline()

    # load document base
    document_base = load_document_base(args.document_base)

    # load search index
    ecu_search_index = args.search_index

    # define base url to doku server
    doku_server_url = args.doku_url

    # init session state
    if 'answer_counter' not in st.session_state:
        st.session_state['answer_counter'] = 0

    st.markdown('# ECU-Test-Doku Q&A-System')
    text_input = st.text_input(
        "Hier kannst Du eine Frage stellen ...",
        placeholder='Was ist ein Traceschritt?',
        key="text_input",
        on_change=None,
        args=()
    )

    if text_input:
        answers = answer_question(text_input, document_base, ecu_search_index)
        if len(answers) > 0:
            col1, col2, _ = st.columns(3)
            bt_next_answer = col1.button('nicht die richtige Antwort?') 
            if bt_next_answer:
                if st.session_state.answer_counter < len(answers) - 1:
                    st.session_state.answer_counter += 1
                else:
                    st.session_state.answer_counter = 0
            col2.markdown(f"*Antwort {st.session_state.answer_counter+1} von {len(answers)}*")
            render_answer(answers[st.session_state.answer_counter], doku_server_url)
        else:
            st.markdown("*Keine Ergebnisse zu der Suchanfrage gefunden* ????")

