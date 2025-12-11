# 제품 요구사항 정의서 (PRD) - 프로젝트 일정 관리 보드

## 1. 프로젝트 개요
*   **프로젝트명**: Lecture Notice Board (프로젝트 일정 관리 보드)
*   **목적**: 개발자 양성과정 학생들과 강사가 프로젝트 일정, 공지사항, 팀 구성을 효율적으로 공유하고 관리하기 위함.
*   **대상 사용자**:
    *   **학생 (User)**: 공지사항 및 일정 조회.
    *   **관리자 (Admin)**: 공지사항 등록, 수정, 삭제 (CRUD).

## 2. 시스템 아키텍처
본 프로젝트는 안정성과 배포 편의성을 위해 컨테이너 기반 아키텍처를 채택합니다.

```mermaid
graph LR
    User[사용자] -->|HTTP:80| Nginx[Nginx (Reverse Proxy)]
    Nginx -->|Proxy Pass:8000| Gunicorn[Gunicorn (WSGI)]
    Gunicorn -->|WSGI| Flask[Flask App]
    Flask -->|Read/Write| SQLite[(SQLite DB)]
    SQLite -.->|Mount| Volume[Docker Volume (/data)]
```

*   **Web Server (Nginx)**: 정적 파일 처리 및 리버스 프록시 역할.
*   **WAS (Gunicorn + Flask)**: 애플리케이션 로직 수행.
*   **Database (SQLite)**: 경량 파일 데이터베이스 사용, Docker Volume을 통한 데이터 영속성 보장.

## 3. 기술 스택
| 구분 | 기술 | 비고 |
| :--- | :--- | :--- |
| **Language** | Python 3.9 | |
| **Framework** | Flask | 경량 웹 프레임워크 |
| **Database** | SQLite3 | Serverless RDBMS |
| **Server** | Nginx, Gunicorn | Production Level 배포 환경 |
| **Infra** | Docker, Docker Compose | 컨테이너 오케스트레이션 |
| **Template** | Jinja2 | Server-side Rendering |

## 4. 기능 요구사항 (Functional Requirements)

### 4.1. 사용자 (Front-office)
*   **메인 대시보드 (`/`)**
    *   모든 게시글을 카테고리별로 그룹화하여 조회할 수 있어야 한다.
    *   카테고리 표시 순서: `전체 일정` -> `일일 일정` -> `수업 공지` -> `팀 구성`
    *   게시글의 내용은 줄바꿈이 유지되어야 한다 (`<pre>` 태그 활용).

### 4.2. 관리자 (Back-office)
*   **관리자 로그인 (`/login`)**
    *   관리자 페이지 접근 시 비밀번호 인증을 거쳐야 한다.
    *   비밀번호는 환경 변수(`ADMIN_PASSWORD`)로 관리되어야 한다.
    *   세션(`session`)을 통해 로그인 상태를 유지한다.
*   **게시글 관리 (`/admin`)**
    *   **작성 (Create)**: 카테고리, 제목, 내용을 입력하여 새 글을 등록한다.
    *   **수정 (Update)**: 기존 글의 내용을 수정한다.
    *   **삭제 (Delete)**: 더 이상 필요 없는 글을 삭제한다.

### 4.3. 시스템 초기화
*   앱 실행 시 데이터베이스 테이블(`posts`)이 없으면 자동 생성해야 한다.
*   데이터가 하나도 없을 경우, 초기 샘플 데이터를 자동으로 주입해야 한다.

## 5. 데이터베이스 스키마 (Database Schema)

### Table: `posts`
| 컬럼명 | 타입 | 제약조건 | 설명 |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PK, AUTOINCREMENT | 게시글 고유 ID |
| `category` | TEXT | NOT NULL | 게시글 카테고리 (예: 전체 일정) |
| `title` | TEXT | NOT NULL | 게시글 제목 |
| `content` | TEXT | NOT NULL | 게시글 본문 |

## 6. API 및 라우트 정의

| Method | URI | 기능 설명 | 권한 |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | 메인 페이지 (게시글 목록 조회) | 전체 |
| `GET` | `/admin` | 관리자 대시보드 / 로그인 페이지 | 전체 (로그인 체크) |
| `POST` | `/login` | 관리자 로그인 처리 | 전체 |
| `POST` | `/create` | 게시글 생성 | 관리자 |
| `GET` | `/edit/<id>` | 게시글 수정 폼 조회 | 관리자 |
| `POST` | `/edit/<id>` | 게시글 수정 처리 | 관리자 |
| `POST` | `/delete/<id>` | 게시글 삭제 처리 | 관리자 |
| `GET` | `/logout` | 관리자 로그아웃 | 관리자 |

## 7. 환경 변수 및 보안 설정 (.env)
보안상 민감한 정보는 소스 코드가 아닌 환경 변수로 관리합니다.

*   `FLASK_SECRET_KEY`: Flask 세션 암호화 키
*   `ADMIN_PASSWORD`: 관리자 페이지 접속 비밀번호
*   `DB_PATH`: SQLite 데이터베이스 파일 경로 (Docker: `/data/schedule.db`)

## 8. 배포 및 운영 (Deployment)
*   **Docker Compose**를 사용하여 `web`(Flask)과 `nginx` 컨테이너를 한 번에 실행한다.
*   `restart: always` 정책을 적용하여 서버 재부팅 시 자동 실행되도록 한다.
*   데이터베이스 파일은 `sqlite_data` 볼륨에 저장하여 컨테이너 재배포 시에도 데이터가 유실되지 않도록 한다.
