FROM python:3.10.6-alpine
WORKDIR /
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /
ENTRYPOINT ["python3", "main.py"]