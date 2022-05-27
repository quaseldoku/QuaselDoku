import streamlit as st
from annotated_text import annotated_text

def answer_question(question):

    # define color of highlighted answer text within context
    h_color = "#8ef"

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

    # get title of paragraph
    _title = "Signalverarbeitung mit Traceschritten"

    # get link to paragraph
    #_link = "file:///mnt/Data/Studium/tracetronic/QuaselDoku/data/01_raw/Doku_v1/TRACE-CHECK/Handbuch/Traceanalyse-Entwurf/Signalverarbeitung_mit_Traceschritten.html"
    _link = " http://127.0.0.1:5000/TRACE-CHECK/Handbuch/Traceanalyse-Entwurf/Signalverarbeitung_mit_Traceschritten.html"

    # manipulate link so answer is also highlighted in doku
    # _link = f'{_link}?highlight={_bert_answer}'
    # _link = _link.replace('\n', ' ')
    # _link = _link.replace(' ', '%20')

    print(_link)

    # find answer in context in order to highlight substring
    _answer_start = _context.find(_bert_answer)
    _answer_end = _answer_start + len(_bert_answer)

    # highlight answer in context
    _c_prfx = _context[:_answer_start] 
    _c_sffx = _context[_answer_end:]

    # show title as header
    # st.markdown(f'#### {_title}')

    annotated_text(
        _c_prfx,
        (_bert_answer, str(_score), h_color),
        _c_sffx
    )

    return _bert_answer, _title, _link

if __name__ == "__main__":

    st.markdown('# ECU-Test-Doku Q&A-System')
    text_input = st.text_input(
        "Hier kannst Du eine Frage stellen ...",
        placeholder='Was ist ein Traceschritt?',
        key="text_input",
        on_change=None,
        args=()
    )

    if text_input:
        answer, title, link = answer_question('test')
        st.markdown("***")
        st.markdown(f'**🔗 Lies mehr dazu im Kapitel [{title}]({link})**')