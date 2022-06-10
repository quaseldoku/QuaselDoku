FROM python:3.9-slim
WORKDIR /app

RUN pip3 install --upgrade pip

COPY ./src/qa_app/webapp/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

COPY ./src/qa_app/webapp/_init_models.py ./_init_models.py
RUN  python _init_models.py

COPY ./src/qa_app/webapp/app.py ./app.py
COPY ./src/quaseldoku/qa_methods ./quaseldoku/qa_methods/
COPY ./data/03_primary/doku_paragraphs.csv ./data/document_base.csv
COPY ./data/03_primary/search_indices/ecu_test ./data/search_index/

CMD streamlit run app.py -- --document-base="./data/document_base.csv" --search-index='./data/search_index/' --doku-url='http://127.0.0.1:5000/'
