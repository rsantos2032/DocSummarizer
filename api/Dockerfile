FROM python:3.12.2
WORKDIR /app
ENV FLASK_APP=api.py
ENV FLASK_ENV=development
COPY ./api/requirements.txt .
RUN pip install -r requirements.txt
COPY ./api .
COPY ./.env .
CMD [ "python", "api.py" ]