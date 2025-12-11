# Flask 배포 아키텍처 리서치 (2025년 기준)

> **참고**: 본 리서치 내용을 바탕으로 현재 프로젝트에 **Docker + Nginx + Gunicorn** 아키텍처가 적용되었습니다. (2025-12-11 업데이트)

## 1. 결론
**"Nginx(웹 서버) + Gunicorn(WAS) + Flask(애플리케이션)"** 조합이 여전히 **가장 표준적이고 강력한 권장 사항**입니다.

`python app.py`로 실행하는 Flask 내장 서버(Werkzeug)는 개발용이므로, 보안 및 성능 이슈로 인해 실제 서비스에서는 절대 사용하지 않습니다.

## 2. 최신 배포 트렌드

최근 배포 환경은 **"컨테이너화"**(Docker)와 "**클라우드 네이티브**"가 핵심입니다.

1.  **Standard (표준)**: **Docker + Gunicorn + Nginx**
    *   가장 널리 쓰이는 방식입니다. Flask와 Gunicorn을 하나의 컨테이너로 묶고, 앞단에 Nginx를 두어 리버스 프록시로 사용합니다.
2.  **Serverless Containers (Cloud Run, Fargate)**:
    *   AWS Fargate나 Google Cloud Run 같은 관리형 서비스에 배포할 때는 **Gunicorn만 포함된 컨테이너**를 올리면, 클라우드 벤더의 로드밸런서가 Nginx 역할을 대신해주기도 합니다. (하지만 정적 파일 처리를 위해 Nginx를 같이 패키징하기도 함)
3.  **Async (비동기) 고려 시**:
    *   Flask 2.0부터 비동기(`async`) 라우트를 지원합니다. 만약 비동기 처리가 핵심이라면 `Gunicorn` 대신 `Hypercorn`이나 `Uvicorn`을 고려할 수 있지만, 일반적인 동기식 Flask 앱이라면 **Gunicorn**이 가장 안정적입니다.

## 3. 각 컴포넌트의 역할 (Why?)

왜 3단계로 나누어 쓰는지 이해하는 것이 중요합니다.

*   **Nginx (Web Server)**
    *   **역할**: 문지기. 사용자의 요청을 가장 먼저 받습니다.
    *   **기능**: SSL(HTTPS) 처리, 정적 파일(이미지, CSS, JS) 직접 전송, 슬로우 클라이언트 공격 방어, 로드 밸런싱.
    *   **이유**: Python은 정적 파일을 서빙하거나 수많은 연결을 유지하는 데 비효율적입니다. Nginx가 이 무거운 짐을 덜어줍니다.

*   **Gunicorn (WSGI Server / WAS)**
    *   **역할**: 번역가. Nginx(HTTP 요청)와 Flask(Python 코드) 사이를 연결합니다.
    *   **기능**: 여러 개의 프로세스(Worker)를 생성하여 동시에 여러 요청을 처리하게 해줍니다.
    *   **이유**: Flask 앱 자체는 한 번에 하나의 요청만 처리하거나 동시성 처리가 약합니다. Gunicorn이 멀티 프로세싱을 관리해 줍니다.

*   **Flask (Web App)**
    *   **역할**: 요리사. 실제 비즈니스 로직(DB 조회, 데이터 가공)을 수행합니다.

## 4. 추천 구성 및 실행 방법

### A. Gunicorn 설치 및 실행 (필수)
먼저 `gunicorn`을 설치하고 실행 스크립트를 만듭니다.

```bash
# 설치
pip install gunicorn

# 실행 (기본)
# -w 4: 워커 프로세스 4개 (보통 CPU 코어 수 * 2 + 1 권장)
# -b 0.0.0.0:8000: 8000번 포트로 바인딩
# app:app : app.py 파일의 app 객체를 실행
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### B. Nginx 설정 (리버스 프록시)
Nginx 설정 파일(`nginx.conf` 또는 `sites-available/default`)에 다음 내용을 추가하여 80번 포트 요청을 Gunicorn(8000)으로 넘깁니다.

```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000; # Gunicorn 주소
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 정적 파일은 Nginx가 직접 처리 (성능 향상)
    location /static {
        alias /path/to/your/project/static;
    }
}
```

## 5. 요약
1.  **엔진**: **Gunicorn**을 사용하세요. (가장 안정적이고 레퍼런스가 많음)
2.  **웹 서버**: **Nginx**를 앞단에 두세요. (보안 및 정적 파일 처리)
3.  **배포 방식**: 가능하다면 **Docker**로 말아서 배포하는 것이 관리하기 가장 편합니다.
