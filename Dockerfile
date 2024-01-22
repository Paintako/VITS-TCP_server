FROM python:3.8.18-slim

WORKDIR /api
COPY ./api .

## Set the same time as the host
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tzdata

RUN TZ=Asia/Taipei \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata 
##

RUN pip install --upgrade pip setuptools==57.5.0

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install opencc-python-reimplemented

EXPOSE 9999

CMD [ "python", "./server.py" ]