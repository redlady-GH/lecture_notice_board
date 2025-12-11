# 배포 가이드 (Deployment Guide)

이 문서는 Docker, Nginx, Gunicorn을 사용하여 Flask 애플리케이션을 배포하는 방법을 설명합니다.

## 사전 요구 사항
- Docker 및 Docker Compose가 설치되어 있어야 합니다.

## 환경 설정 (Configuration)
프로젝트 실행 전, 환경 변수 설정이 필요합니다.

1. **.env 파일 생성**
   제공된 예시 파일을 복사하여 `.env` 파일을 생성합니다.
   ```bash
   cp .env.example .env
   ```

2. **환경 변수 수정 (선택 사항)**
   `.env` 파일을 열어 관리자 비밀번호(`ADMIN_PASSWORD`)와 시크릿 키(`FLASK_SECRET_KEY`)를 변경할 수 있습니다.

## 배포 구조
- **Nginx**: 웹 서버 및 리버스 프록시 (포트 80)
- **Gunicorn**: WSGI 애플리케이션 서버 (Flask 실행)
- **Flask**: 애플리케이션 로직
- **SQLite**: 데이터베이스 (Docker 볼륨 `sqlite_data`에 저장됨)
- **자동 재시작**: 모든 컨테이너는 `restart: always`로 설정되어 있어, 시스템 재부팅 시 자동으로 시작됩니다.

## 실행 방법

1. **컨테이너 빌드 및 실행**
   ```bash
   docker-compose up -d --build
   ```

2. **접속 확인**
   브라우저에서 `http://localhost` 로 접속하여 애플리케이션이 정상적으로 동작하는지 확인합니다.

3. **로그 확인**
   ```bash
   docker-compose logs -f
   ```

4. **중지**
   ```bash
   docker-compose down
   ```

## 데이터베이스 관리
데이터베이스 파일은 Docker 볼륨 `sqlite_data` 내의 `/data/schedule.db`에 저장되므로, 컨테이너를 재시작해도 데이터가 유지됩니다.
초기 실행 시 데이터베이스가 없으면 자동으로 생성되고 기본 데이터가 입력됩니다.
