FROM python:3.8-slim
RUN apt-get update && apt-get install -y libsndfile1 ffmpeg
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "app.py"]
