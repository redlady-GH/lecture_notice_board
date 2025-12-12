# [심화] Flask-WTF를 이용한 강력한 CSRF 보호 적용 가이드

이 문서는 기존의 수동 CSRF 토큰 구현 방식에서 나아가, Python Flask 생태계의 표준 라이브러리인 **Flask-WTF**를 사용하여 보다 강력하고 체계적인 보안을 적용하는 방법을 설명합니다.

## 1. 왜 Flask-WTF인가?

기존 `app.py`에서는 `os.urandom`이나 `secrets` 모듈을 사용하여 직접 난수를 생성하고 세션에 저장하여 비교하는 방식을 사용했습니다. 이는 기본적인 방어는 가능하지만, 다음과 같은 한계가 있습니다.

1.  **구현 복잡성**: 모든 POST 요청마다 토큰 검증 로직(`if token != session['token']...`)을 개발자가 직접 작성해야 합니다. 실수로 누락할 가능성이 높습니다.
2.  **표준화 부재**: 프로젝트마다 구현 방식이 다를 수 있어 유지보수가 어렵습니다.
3.  **기능 제한**: 토큰 만료 시간 설정, 특정 라우트 예외 처리 등 고급 기능을 직접 구현해야 합니다.

**Flask-WTF**는 이러한 문제를 해결해줍니다.
- **자동 검증**: 설정만 하면 모든 POST/PUT/DELETE 요청에 대해 자동으로 토큰을 검증합니다.
- **템플릿 통합**: `{{ csrf_token() }}` 함수를 통해 쉽게 토큰을 삽입할 수 있습니다.
- **유연성**: 특정 뷰만 제외하거나(`@csrf.exempt`), 설정을 통해 동작을 제어할 수 있습니다.

---

## 2. 적용 방법 (Step-by-Step)

이 프로젝트에는 이미 Flask-WTF가 적용된 **`app_WTF.py`** 파일과 **`templates_wtf/`** 폴더가 준비되어 있습니다. 이를 통해 단계별로 학습해 봅시다.

### 2.1. 라이브러리 설치

먼저 `Flask-WTF` 라이브러리를 설치해야 합니다.

```bash
pip install Flask-WTF
```

### 2.2. 애플리케이션 코드 변경 (`app_WTF.py`)

기존 `app.py`와 비교하여 변경된 부분입니다.

**1) 초기화 및 설정**

```python
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__, template_folder='templates_wtf') # 템플릿 폴더 변경
app.config['SECRET_KEY'] = 'your-secret-key' # 필수 설정

# CSRF 보호 초기화
csrf = CSRFProtect(app)
```
- `CSRFProtect(app)` 한 줄로 애플리케이션 전역에 CSRF 보호가 활성화됩니다.
- 이제 POST 요청 시 토큰이 없거나 유효하지 않으면 Flask가 자동으로 **400 Bad Request** 에러를 반환합니다.

**2) 수동 검증 로직 제거**

기존의 `delete` 함수 등에 있던 수동 검증 코드는 더 이상 필요하지 않습니다.

```python
# 기존 app.py (수동 검증)
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    token = request.form.get('csrf_token')
    if not token or token != session.get('csrf_token'):
        abort(403)
    # ...

# 변경된 app_WTF.py (자동 검증)
@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    # 별도의 검증 코드 불필요!
    # 여기까지 왔다면 이미 검증이 완료된 상태입니다.
    # ...
```

### 2.3. 템플릿 코드 변경 (`templates_wtf/`)

HTML Form 내부에 CSRF 토큰을 포함시켜야 합니다. Flask-WTF는 이를 위한 `csrf_token()` 함수를 제공합니다.

**예시: `templates_wtf/login.html`**

```html
<form method="POST">
    <!-- 이 한 줄만 추가하면 됩니다 -->
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
    
    <input type="password" name="password" placeholder="비밀번호">
    <button type="submit">로그인</button>
</form>
```

모든 `<form method="POST">` 태그 내부에 위 `input` 태그를 추가해야 합니다.

---

## 3. 실행 및 테스트

Flask-WTF가 적용된 버전을 실행하여 동작을 확인해 봅니다.

### 3.1. 실행

```bash
python app_WTF.py
```

### 3.2. 테스트 시나리오

1.  **정상 동작 확인**:
    - 로그인, 글 작성, 수정, 삭제가 정상적으로 동작하는지 확인합니다.
    - 개발자 도구(F12)를 열어 Form 태그 안에 `<input type="hidden" name="csrf_token" ...>`이 생성되었는지 확인합니다.

2.  **방어 동작 확인**:
    - 개발자 도구에서 강제로 `csrf_token` input 태그를 삭제하거나 value 값을 조작한 후 '삭제' 버튼을 눌러봅니다.
    - **400 Bad Request** 에러 페이지가 뜨는지 확인합니다. (기존에는 403 Forbidden을 수동으로 띄웠으나, Flask-WTF는 기본적으로 400을 반환합니다.)

---

## 4. 결론

Flask-WTF를 도입함으로써 우리는 **더 적은 코드로 더 강력한 보안**을 얻을 수 있었습니다. 실무 프로젝트에서는 보안 관련 기능을 직접 구현하기보다, 검증된 라이브러리를 사용하는 것이 권장됩니다.

이 예제를 통해 프레임워크가 제공하는 보안 기능의 편리함과 중요성을 이해하시기 바랍니다.
