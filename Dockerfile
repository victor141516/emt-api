FROM python:3-alpine

WORKDIR /app
RUN pip install beautifulsoup4 requests Flask gunicorn
COPY . /app
CMD [ "gunicorn", "-w4", "-b", ":8000", "main:app" ]
