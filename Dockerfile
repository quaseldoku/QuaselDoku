FROM python:3.9-slim
WORKDIR /app

COPY ./src/qa_app/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

COPY ./data/01_raw/Doku_v1 ./doku/
COPY ./src/qa_app/doku_server.py ./doku/
# RUN python ./doku/doku_server.py

EXPOSE 5000
COPY app.py ./webapp/app.py
CMD streamlit run ./webapp/app.py
