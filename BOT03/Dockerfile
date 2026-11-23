FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY BOT03/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY BOT03/ ./
EXPOSE 10000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:'+os.getenv('PORT','10000')+'/_stcore/health')"
CMD ["sh","-c","streamlit run app.py --server.address=0.0.0.0 --server.port=${PORT:-10000} --server.headless=true"]
