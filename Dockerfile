FROM python:3.11-slim
ENV TZ="Europe/Moscow"

LABEL maintainer="Gleb Sergeev <dieplex@mail.ru>"

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./start.sh /start.sh
RUN chmod +x /start.sh

COPY ./start-reload.sh /start-reload.sh
RUN chmod +x /start-reload.sh

COPY . /app
WORKDIR /app

ENV PYTHONPATH=/app

CMD ["/start.sh"]