# mDNS 상황 분석 보고서

## 1. 개요
본 문서는 Ubuntu Server 환경에서 mDNS(`n100.local`)를 통한 웹 서비스(HTTPS) 접속 실패 원인을 분석하고 해결 방안을 제시합니다.

## 2. 현상 (Symptoms)
*   **SSH 접속 성공**: `ssh user@n100.local` 접속은 정상적으로 이루어짐.
*   **IP 접속 성공**: 브라우저에서 `https://192.168.x.x` 접속 시 정상 동작 (인증서 경고 제외).
*   **mDNS 웹 접속 실패**: 브라우저에서 `https://n100.local` 접속 시 "사이트에 연결할 수 없음" 또는 "연결 거부됨" 오류 발생.

## 3. 원인 분석 (Root Cause Analysis)

### 3.1. IPv6 우선순위와 Docker 바인딩 문제
가장 핵심적인 원인은 **OS와 브라우저의 IPv6 선호 정책**과 **Docker의 IPv4 중심 네트워킹** 간의 불일치입니다.

1.  **Avahi의 IPv6 광고**:
    *   현재 서버의 `/etc/avahi/avahi-daemon.conf` 설정에 `use-ipv6=yes`가 되어 있습니다.
    *   클라이언트(Mac/Windows)가 `n100.local`을 조회하면, Avahi는 **IPv4 주소**와 **IPv6 주소**를 모두 응답합니다.
2.  **브라우저의 IPv6 선호**:
    *   현대적인 브라우저(Chrome, Safari 등)는 DNS 응답에 IPv6가 포함되어 있으면 **IPv6로 먼저 연결을 시도**합니다.
3.  **Docker의 바인딩 제한**:
    *   Docker 컨테이너는 기본적으로 IPv4(`0.0.0.0`)에 포트를 바인딩합니다.
    *   별도의 설정 없이는 IPv6(`::`) 트래픽을 컨테이너로 라우팅하지 못하거나, 호스트 방화벽에서 차단될 수 있습니다.
4.  **SSH가 되는 이유**:
    *   SSH 데몬(`sshd`)은 호스트 OS에서 직접 실행되며, 기본적으로 IPv4와 IPv6 모두를 리스닝(`ListenAddress ::`)하기 때문에 접속이 가능합니다.

### 3.2. 설정 파일 확인 결과
`/etc/avahi/avahi-daemon.conf` 파일 확인 결과:
```ini
[server]
use-ipv4=yes
use-ipv6=yes  <-- IPv6가 활성화되어 있음
allow-interfaces=enp1s0
```

## 4. 해결 방안 (Solution)

서버 환경이 IPv6를 필수적으로 사용하지 않는다면, **Avahi에서 IPv6 광고를 비활성화**하여 클라이언트가 강제로 IPv4를 사용하도록 만드는 것이 가장 확실하고 간단한 해결책입니다.

### 4.1. 조치 단계

1.  **설정 파일 편집**:
    터미널에서 다음 명령어로 설정 파일을 엽니다.
    ```bash
    sudo nano /etc/avahi/avahi-daemon.conf
    ```

2.  **IPv6 비활성화**:
    `[server]` 섹션의 `use-ipv6` 값을 `no`로 변경합니다.
    ```ini
    [server]
    use-ipv4=yes
    use-ipv6=no
    ```

3.  **서비스 재시작**:
    변경 사항을 적용하기 위해 Avahi 데몬을 재시작합니다.
    ```bash
    sudo systemctl restart avahi-daemon
    ```

4.  **클라이언트 캐시 초기화 및 테스트**:
    *   클라이언트 PC(Mac/Windows)의 DNS 캐시를 초기화하거나 잠시 기다립니다.
    *   브라우저를 완전히 종료 후 다시 시작하여 `https://n100.local` 접속을 시도합니다.

## 5. 결론
이 문제는 웹 서버 설정의 오류가 아니라, **네트워크 프로토콜 우선순위(IPv6 > IPv4)**에 따른 연결 실패입니다. Avahi 설정을 통해 mDNS가 IPv4 주소만 반환하도록 제한함으로써 문제를 해결할 수 있습니다.
