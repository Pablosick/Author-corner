FROM python

LABEL description="Start app Flask"

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]