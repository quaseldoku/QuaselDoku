FROM python:3.9-slim
WORKDIR /app

COPY ./src/qa_app/doku_server/requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

COPY ./data/01_raw/Doku_v1 ./data/
COPY ./src/qa_app/doku_server/app.py .

CMD python app.py ./data/
