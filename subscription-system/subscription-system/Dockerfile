FROM python:3.12-slim

# Не пишем .pyc, выводим логи без буфера
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /code

# Сначала зависимости — для кеширования слоёв Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app
COPY ./frontend ./frontend

EXPOSE 8000

# Прод-запуск без --reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
