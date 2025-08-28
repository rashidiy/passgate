FROM python:3.12-slim

WORKDIR /app

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# bug: redis got downloaded for python 2
RUN pip uninstall -y redis || true
RUN rm -rf /usr/local/lib/python3.12/site-packages/redis*
RUN pip install --no-cache-dir redis==5.2.1

COPY . .
