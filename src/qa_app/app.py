from importlib.resources import path
import os
from pydoc import doc
import streamlit as st
import pandas as pd
from annotated_text import annotated_text
from quaseldoku.qa_methods import keyword_search
from quaseldoku.helper import find_project_root
from transformers import pipeline

@st.cache
def load_document_base(path):
    return pd.read_csv(path)

qa_pipeline = pipeline(
    "question-answering",
    model="deutsche-telekom/bert-multi-english-german-squad2",
    tokenizer="deutsche-telekom/bert-multi-english-german-squad2",
)


# funktion um antwort von bert model zuerstellen 
def bert_answer_question(question: str, paragraph: str):
    input = {
        "question": question,
        "context": paragraph
    }
    return qa_pipeline(input)

def answer_question(question, document_base, dummy=False):

    # define color of highlighted answer text within context
    h_color = "#8ef"
    
    # base link to doku (will be either to web server running doku or local file)
    _base_link = "http://127.0.0.1:5000/"

    if dummy:
        # run question through model(s) and render results
        # BERT gives some words as answer
        _bert_answer = '''
        Traceschritte übernehmen die wesentlichen Aufgaben der Signalverarbeitung. 
        Über die reinen Signalbewertungen hinaus können Traceschritte aber auch Signalberechnungen vornehmen.'''

        # get score of answer
        _score = 0.73

        # get context where answer is located in
        _context = '''
        Traceschritte übernehmen die wesentlichen Aufgaben der Signalverarbeitung. 
        Über die reinen Signalbewertungen hinaus können Traceschritte aber auch Signalberechnungen vornehmen.
        Auf diese Weise können anderen Traceschritten, die in der selben Traceanalyse zum Einsatz kommen, 
        zusätzliche Signale zur Verfügung gestellt werden. Dadurch gelingt es, 
        Traceanalysen modular zu gestalten und in Teilen wiederzuverwenden. 
        So kann beispielsweise ausgehend von einem vorhandenen Signal zunächst ein Traceschritt 
        eine geglättete Variante dieses Signals berechnen und ein zweiter Traceschritt kann dann eine 
        Testbewertung dieses geglätteten Signals vornehmen. 
        '''
       
        # get link to paragraph
        #_link = "file:///mnt/Data/Studium/tracetronic/QuaselDoku/data/01_raw/Doku_v1/TRACE-CHECK/Handbuch/Traceanalyse-Entwurf/Signalverarbeitung_mit_Traceschritten.html"
        _link = _base_link + "TRACE-CHECK/Handbuch/Traceanalyse-Entwurf/Signalverarbeitung_mit_Traceschritten.html"

        # get title of paragraph
        _title = "Signalverarbeitung-mit-Traceschritten"

    else:

        # still dummies since only keyword search is tested
        _bert_answer = ''
        _score = ''

        # perform keyword search on ecu test index and retrieve best result
        ecu_search_index = find_project_root(os.getcwd()) + '/data/03_primary/search_indices/ecu_test/'
        key_word_res = keyword_search.query(question, ecu_search_index)
        if len(key_word_res['hits']) < 1:
            st.markdown("*Keine Ergebnisse zu der Suchanfrage gefunden* 😔")
            return
        best_res_hash = key_word_res['hits'][0]
        #hash für die anderen Ergebnisse
        second_res_hash = key_word_res['hits'][1]
        third_res_hash = key_word_res['hits'][2] 
       

        # with retrieved hash look up context, title, etc. in document base
        row = document_base.loc[document_base['Hash'] == best_res_hash].values[0]
        row1 = document_base.loc[document_base['Hash'] == second_res_hash].values[0]
        row2 = document_base.loc[document_base['Hash'] == third_res_hash].values[0]

        # getting all the context from the first 3 result of the key search
        contexts = row[3]
        contexts1 = row1[3]
        contexts2 = row2[3]
   
        # context of best 3 goes into bert to find answer
        output = bert_answer_question(question,contexts )
        output1 = bert_answer_question(question, contexts1)
        output2 = bert_answer_question(question, contexts2)
        
        # output of bert get the hash value
        output["hash"] = best_res_hash
        output1["hash"] = second_res_hash
        output2["hash"] = third_res_hash

        outputs =[output, output1, output2]
        # finding best score in list of the 3 outputs
        max_score = max(outputs, key=lambda x: x['score'])

        fin_row = document_base.loc[document_base['Hash'] == max_score["hash"]].values[0]
        _title = fin_row[1]
        _link = _base_link + fin_row[2]
        _context = max_score['answer'] 
        _text = fin_row[3]
        _score = max_score['score']
        print(_link, _title)


    # append title to link to show correct paragraph
    _link += f'#{_title.lower()}'
    print(_link)

    # format title for display later
    _title_display = _title.replace('-', ' ')

    # manipulate link so answer is also highlighted in doku
    # _link = f'{_link}?highlight={_bert_answer}'
    # _link = _link.replace('\n', ' ')
    # _link = _link.replace(' ', '%20')

    # find answer in context in order to highlight substring
    _answer_start = _text.find(_context)
    _answer_end = _answer_start + len(_context)

    # highlight answer in context
    _c_prfx = _text[:_answer_start] 
    _c_sffx = _text[_answer_end:]

    # show title as header
    # st.markdown(f'#### {_title}')

    if dummy:
        annotated_text(
            _c_prfx,
            (_bert_answer, str(_score), h_color),
            _c_sffx
        )
    else:
        st.markdown(_context)
        annotated_text(
            _c_prfx,
            (_context, str(_score), h_color),
            _c_sffx)

    st.markdown("***")
    st.markdown(f'**🔗 Lies mehr dazu im Kapitel [{_title_display}]({_link})**')


if __name__ == "__main__":

    document_base = load_document_base(find_project_root(os.getcwd()) + '/data/03_primary/doku_paragraphs.csv')
    # st.dataframe(document_base)

    st.markdown('# ECU-Test-Doku Q&A-System')
    text_input = st.text_input(
        "Hier kannst Du eine Frage stellen ...",
        placeholder='Was ist ein Traceschritt?',
        key="text_input",
        on_change=None,
        args=()
    )

    if text_input:
        answer_question(text_input, document_base)
