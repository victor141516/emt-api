FROM python:3-alpine

ENV PORT=8000
ENV GUNICORN_CMD_ARGS="-w4 -b :${PORT}"
WORKDIR /app
RUN pip install beautifulsoup4 requests Flask gunicorn
COPY . /app
CMD 'exec gunicorn main:app'
