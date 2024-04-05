FROM python:3.12.2
WORKDIR /app
ENV FLASK_APP=api.py
ENV FLASK_ENV=development
COPY ./api/requirements.txt .
COPY ./.env .
RUN pip install -r requirements.txt
COPY . .
CMD [ "python", "api.py" ]
