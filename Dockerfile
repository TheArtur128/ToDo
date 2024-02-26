FROM python:alpine

WORKDIR /todo

COPY . .

RUN apk add npm && \
npm install typescript -g && \
tsc && \
apk add poetry && \
poetry install --without dev

ENTRYPOINT ["poetry", "run"]
CMD ["python", "manage.py", "runserver"]
