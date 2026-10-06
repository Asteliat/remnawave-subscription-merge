FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir "fastapi>=0.115" "httpx>=0.27" "PyYAML>=6.0" "uvicorn[standard]>=0.30"
RUN useradd --system --uid 10001 --create-home --shell /usr/sbin/nologin merge
RUN mkdir -p /var/lib/remnawave-subscription-merge && chown -R merge:merge /app /var/lib/remnawave-subscription-merge
USER merge
EXPOSE 18080
VOLUME ["/var/lib/remnawave-subscription-merge"]
CMD ["python","-m","uvicorn","src.http_endpoint:app","--host","0.0.0.0","--port","18080"]
