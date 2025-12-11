FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# schedule.db가 없으면 app.py가 생성하지만, 
# 볼륨 마운트를 위해 미리 빈 파일을 생성하거나 권한을 설정할 수도 있음.
# 여기서는 런타임에 생성되도록 둠.

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
