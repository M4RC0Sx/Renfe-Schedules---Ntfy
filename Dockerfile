FROM python:3.12.0-alpine

COPY . /app
WORKDIR /app

RUN pip install pipenv
RUN pipenv install --system --deploy --ignore-pipfile

CMD ["python", "-m", "rsn"]