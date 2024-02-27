FROM python:alpine

WORKDIR /todo

COPY . .

RUN apk add npm && \
npm install typescript -g && \
apk add poetry && \
poetry install

ENTRYPOINT ["poetry", "run", "scripts/entrypoint.sh"]
CMD ["python", "manage.py", "runserver"]
