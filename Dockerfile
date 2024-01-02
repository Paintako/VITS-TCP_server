FROM python:3.8.18-slim

WORKDIR /api
COPY ./api .

RUN pip install --upgrade pip setuptools==57.5.0

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install opencc-python-reimplemented

EXPOSE 9999

CMD [ "python", "./server.py" ]