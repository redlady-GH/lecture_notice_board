# [교육용 프로젝트] Lecture Notice Board: 웹 보안과 실무 배포

이 프로젝트는 4개월 차 초급 개발자 양성과정 학생들을 위한 **[Flask 웹 보안 및 실무 배포 실습]** 교안입니다.
단순히 "돌아가는 코드"를 넘어, "**안전하고 배포 가능한 아키텍처**"를 설계하고 구현하는 과정을 단계별로 학습합니다.

---

## 1. 학습 로드맵 (Curriculum)

이 프로젝트는 총 4개의 모듈로 구성되어 있으며, 각 단계마다 **이론 학습**(Docs)과 **코드 실습**(Code)이 병행됩니다.

### Module 1: 기획 및 아키텍처 설계
개발을 시작하기 전, 무엇을 만들고 어떻게 구성할지 정의합니다.
*   📄 **[기획]** [제품 요구사항 정의서 (PRD)](docs/prd.md): "무엇을 만들 것인가?" (기능/비기능 요구사항)
*   📄 **[설계]** [기술 요구사항 정의서 (TRD)](docs/trd.md): "어떻게 구현할 것인가?" (기술 스택, DB 스키마)
*   📄 **[이론]** [Flask 실무 배포 아키텍처 이해하기](docs/리서치_Flask_배포_아키텍처.md): 왜 `Docker + Nginx + Gunicorn` 조합을 사용하는가?

### Module 2: 웹 보안 기초 (Level 1)
가장 기본적인 보안 취약점을 분석하고, 라이브러리 없이 수동으로 방어 코드를 작성하며 원리를 이해합니다.
*   📄 **[보안]** [웹 보안 기초: CSRF 공격과 방어](docs/보안점검_게시글_삭제.md): GET/POST의 차이와 CSRF 토큰의 원리.
*   📄 **[보안]** [웹 보안 기초: 세션 탈취와 방어](docs/보안점검_세션_탈취.md): HTTPS와 쿠키 보안 설정(`HttpOnly`, `Secure`).
*   💻 **[Code]** `app.py`: 수동으로 CSRF 토큰을 생성하고 검증하는 코드가 포함되어 있습니다.

### Module 3: 웹 보안 심화 (Level 2)
실무에서 사용하는 표준 라이브러리를 적용하여 보안성과 생산성을 높입니다.
*   📄 **[심화]** [Flask-WTF로 CSRF 방어하기](docs/가이드_Flask_WTF_CSRF_적용.md): `Flask-WTF` 라이브러리 적용 가이드.
*   💻 **[Code]** `app_WTF.py`: 라이브러리를 통해 자동화된 CSRF 방어가 적용된 코드입니다.

### Module 4: 인프라 및 배포
개발한 애플리케이션을 실제 운영 환경과 유사하게 배포합니다.
*   📄 **[실습]** [실무 배포 가이드: Docker와 Nginx](docs/Deployment_Guide.md): Docker Compose를 이용한 원클릭 배포.
*   📄 **[심화]** [네트워크 기초: mDNS와 .local 도메인](docs/네트워크_mdns_.local_도메인.md): IP 대신 도메인 이름으로 접속하기.

---

## 2. 프로젝트 구조

```text
lecture_notice/
├── docs/               # [학습자료] 위에서 소개한 모든 강의 자료가 들어있습니다.
├── nginx/              # [인프라] Nginx 설정 및 SSL 인증서
├── templates/          # [Level 1] 기본 HTML (수동 CSRF 토큰)
├── templates_wtf/      # [Level 2] 심화 HTML (Flask-WTF 매크로)
├── app.py              # [Level 1] 기본 Flask 앱 (수동 보안 구현)
├── app_WTF.py          # [Level 2] 심화 Flask 앱 (라이브러리 활용)
├── docker-compose.yml  # [배포] 전체 서비스 오케스트레이션
├── Dockerfile          # [배포] Flask 이미지 빌드 설정
└── .env.example        # [설정] 환경 변수 예시
```

---

## 3. 빠른 시작 (Quick Start)

이 프로젝트는 **Docker** 환경에서 실행하는 것을 권장합니다.

### 3.1. 사전 준비
1.  **환경 변수 설정**: `.env.example`을 복사하여 `.env` 파일을 만듭니다.
    ```bash
    cp .env.example .env
    ```
2.  **SSL 인증서 생성**: HTTPS 구동을 위해 자가 서명 인증서를 생성합니다.
    ```bash
    mkdir -p nginx/ssl
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout nginx/ssl/server.key \
      -out nginx/ssl/server.crt \
      -subj "/CN=myserver.local" \
      -addext "subjectAltName=DNS:myserver.local,DNS:*.local,IP:127.0.0.1"
    ```

### 3.2. 실행 (Docker Compose)
```bash
docker-compose up -d --build
```
*   기본적으로 `app.py` (Level 1)가 실행됩니다.
*   `app_WTF.py` (Level 2)를 실행하려면 `Dockerfile`의 마지막 줄(`CMD`)을 수정하세요.

### 3.3. 접속
브라우저를 열고 `https://myserver.local` (또는 `https://localhost`)로 접속합니다.
*   **관리자 로그인**: `.env` 파일에 설정한 비밀번호를 사용하세요.

---

## 4. 마치며
이 프로젝트를 통해 여러분은 단순한 코더(Coder)에서 **시스템 전체를 이해하는 엔지니어**(Engineer)로 성장하게 될 것입니다.
각 단계의 문서를 꼼꼼히 읽고, 코드를 직접 수정해보며 학습하시기 바랍니다.
