# 배포 가이드 (Deployment Guide)

이 문서는 Docker, Nginx, Gunicorn을 사용하여 Flask 애플리케이션을 배포하는 방법을 설명합니다.

## 사전 요구 사항
- Docker 및 Docker Compose가 설치되어 있어야 합니다.
- OpenSSL (SSL 인증서 생성용)이 설치되어 있어야 합니다.
- (선택) Avahi Daemon (mDNS 사용 시)

## 환경 설정 (Configuration)
프로젝트 실행 전, 환경 변수 설정과 SSL 인증서 생성이 필요합니다.

1. **.env 파일 생성**
   제공된 예시 파일을 복사하여 `.env` 파일을 생성합니다.
   ```bash
   cp .env.example .env
   ```

2. **환경 변수 수정 (선택 사항)**
   `.env` 파일을 열어 관리자 비밀번호(`ADMIN_PASSWORD`)와 시크릿 키(`FLASK_SECRET_KEY`)를 변경할 수 있습니다.

3. **SSL 인증서 생성 (필수)**
   Nginx의 HTTPS 구동을 위해 자가 서명 인증서를 생성합니다.
   ```bash
   mkdir -p nginx/ssl
   # 'myserver'를 실제 호스트 이름으로 변경하세요.
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
     -keyout nginx/ssl/server.key \
     -out nginx/ssl/server.crt \
     -subj "/CN=myserver.local" \
     -addext "subjectAltName=DNS:myserver.local,DNS:*.local,IP:127.0.0.1"
   ```

## 배포 구조
- **Nginx**: 웹 서버 및 리버스 프록시 (포트 80 -> 443 리다이렉트, 443 SSL 처리)
- **Gunicorn**: WSGI 애플리케이션 서버 (Flask 실행)
- **Flask**: 애플리케이션 로직 (CSRF 보호 적용)
- **SQLite**: 데이터베이스 (Docker 볼륨 `sqlite_data`에 저장됨)
- **자동 재시작**: 모든 컨테이너는 `restart: always`로 설정되어 있어, 시스템 재부팅 시 자동으로 시작됩니다.

## 실행 방법

1. **컨테이너 빌드 및 실행**
   ```bash
   docker-compose up -d --build
   ```

2. **접속 확인**
   브라우저에서 `https://myserver.local` (또는 `https://localhost`) 로 접속합니다.
   *   자가 서명 인증서이므로 "안전하지 않음" 경고가 뜰 수 있습니다.

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

## 트러블슈팅 (Troubleshooting)

### 1. mDNS 접속 불가 (n100.local 등)
*   **증상**: `ping myserver.local`이 실패하거나 브라우저 접속이 안 됨.
*   **원인**: mDNS 전파 지연 또는 클라이언트 캐시.
*   **해결**:
    *   서버에서 `systemctl status avahi-daemon` 확인.
    *   클라이언트에서 1~2분 대기 후 재시도.
    *   IP 주소로 직접 접속 시도.

### 2. HTTPS 경고창
*   **증상**: "연결이 비공개로 설정되어 있지 않습니다" 경고.
*   **원인**: 공인된 CA가 아닌 자가 서명 인증서를 사용했기 때문.
*   **해결**: 브라우저의 고급 설정에서 "이동(안전하지 않음)"을 선택하여 진행. (내부망 암호화는 정상 작동함)
