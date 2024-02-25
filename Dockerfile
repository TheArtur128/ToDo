FROM python:alpine

WORKDIR /code/todo

COPY . .

RUN apk add npm
RUN npm install typescript -g
RUN tsc

RUN pip install poetry
RUN poetry install

RUN poetry run python manage.py migrate

ENTRYPOINT ["poetry", "run"]
CMD ["python", "manage.py", "runserver"]

