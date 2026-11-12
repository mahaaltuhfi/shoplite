   # ---- Stage 1: install dependencies ----
   FROM python:3.12-slim AS builder
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

   # ---- Stage 2: small runtime image ----
   FROM python:3.12-slim
   # Security: create and use a non-root user
   RUN useradd --create-home --uid 1001 appuser
   WORKDIR /app
   COPY --from=builder /install /usr/local
   COPY app.py .
   USER appuser
   ENV PORT=5001
   EXPOSE 5001
   CMD ["gunicorn", "--bind", "0.0.0.0:5001", "--workers", "2", "app:create_app()"]