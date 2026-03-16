FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.runtime.txt ./
RUN pip install --no-cache-dir -r requirements.runtime.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "main_v2:app", "--host", "0.0.0.0", "--port", "8001"]
