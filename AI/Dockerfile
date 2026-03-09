FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY api_requirements.txt ./
RUN pip install --no-cache-dir -r api_requirements.txt

COPY . .

ENV PORT=8005
EXPOSE 8005

CMD ["uvicorn", "rooftop_fastapi:app", "--host", "0.0.0.0", "--port", "8005"]
