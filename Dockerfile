FROM python

LABEL description="Start app Flask"

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . .

ENV PORT 5000

EXPOSE $PORT

VOLUME ["/app/instance/"]

CMD ["flask", "run", "--host=0.0.0.0"]