# 프로젝트 지침 (Project Instructions)

## 개요
이 프로젝트는 프로젝트 일정과 공지사항을 관리하기 위한 Flask 애플리케이션입니다. 교육용 예제로 시작되었으나, 현재는 **Docker + Nginx + Gunicorn** 기반의 실무 배포 아키텍처를 따르고 있습니다. 데이터 저장소로는 SQLite를 사용하며, Docker Volume을 통해 데이터를 영속화합니다.

## 아키텍처
- **인프라**: Docker & Docker Compose
- **웹 서버**: Nginx (Reverse Proxy, Port 80)
- **WAS**: Gunicorn (Port 8000)
- **애플리케이션**: Flask (Python 3.9)
- **데이터베이스**: SQLite (`schedule.db`, Docker Volume 마운트)

## 프로젝트 구조
- `app.py`: Flask 애플리케이션 로직 (DB 연결, 라우팅).
- `nginx/nginx.conf`: Nginx 리버스 프록시 설정.
- `Dockerfile`: Flask + Gunicorn 이미지 빌드 설정.
- `docker-compose.yml`: 전체 서비스 오케스트레이션 설정.
- `.env`: 환경 변수 (비밀번호, 시크릿 키) 관리. **(Git에 커밋하지 않음)**
- `templates/`: Jinja2 HTML 템플릿.
- `requirements.txt`: Python 의존성 목록.

## 핵심 패턴 및 규칙

### 환경 설정 및 보안
- **환경 변수**: `python-dotenv`를 사용하여 `.env` 파일에서 설정을 로드합니다.
- **민감 정보**: `FLASK_SECRET_KEY`, `ADMIN_PASSWORD` 등은 소스 코드에 하드코딩하지 않고 반드시 환경 변수(`os.environ.get`)를 통해 접근합니다.

### 데이터베이스 접근
- **라이브러리**: Python 내장 `sqlite3` 사용.
- **경로**: `DB_PATH` 환경 변수를 통해 DB 파일 경로를 제어합니다. (Docker 환경: `/data/schedule.db`, 로컬: `schedule.db`)
- **연결**: `get_db_connection()` 함수 사용 (`sqlite3.Row` 팩토리 적용).
- **쿼리**: SQL Injection 방지를 위해 반드시 파라미터화된 쿼리(`?`)를 사용합니다.

### 라우팅 및 뷰
- **카테고리**: `["전체 일정", "일일 일정", "수업 공지", "팀 구성"]` 순서로 그룹화하여 표시합니다.
- **인증**: 세션 기반의 간단한 로그인 체크를 수행하며, 비밀번호는 환경 변수와 대조합니다.

## 개발 워크플로우

### 앱 실행 (Docker 권장)
```bash
docker-compose up -d --build
```
- Nginx는 80번 포트, Flask(Gunicorn)는 내부적으로 8000번 포트를 사용합니다.
- 브라우저에서 `http://localhost`로 접속합니다.

### 로컬 개발 (선택 사항)
```bash
pip install -r requirements.txt
python app.py
```
- `.env` 파일이 있어야 정상 작동합니다.

### 데이터베이스 관리
- **데이터 영속성**: Docker 실행 시 `sqlite_data` 볼륨에 DB 파일이 저장되므로 컨테이너를 재시작해도 데이터가 유지됩니다.
- **초기화**: DB 파일이 없으면 앱 시작 시 `init_db()`가 실행되어 테이블과 기본 데이터를 생성합니다.

## 주요 파일 참조
- `app.py`: 애플리케이션 로직.
- `docker-compose.yml`: 서비스 구성 정의.
- `DEPLOY.md`: 배포 가이드.
