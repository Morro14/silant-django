FROM python:3.12-slim as builder
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


WORKDIR /app

RUN pip install --upgrade pip
COPY ./requirements.txt .
# RUN pip install -r requirements.txt
RUN mkdir wheels
RUN pip wheel --no-cache-dir --no-deps --wheel-dir ./wheels -r requirements.txt
# COPY . .
# RUN mkdir /app/staticfiles
# COPY ./entrypoint.sh .
FROM python:3.12-slim
WORKDIR /app
RUN mkdir wheels
COPY --from=builder /app/wheels /app/wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /app/wheels/*
RUN mkdir /app/staticfiles
COPY entrypoint.sh .
COPY . .
EXPOSE 8080
ENTRYPOINT [ "/app/entrypoint.sh" ]