FROM python:alpine

WORKDIR /todo

COPY . .

RUN apk add npm && \
npm install typescript -g && \
npm install sass -g && \
apk add poetry && \
poetry install

CMD ["poetry", "run", "python", "manage.py", "runserver"]
