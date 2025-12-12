import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

load_dotenv()

# 템플릿 폴더를 templates_wtf로 변경하여 Flask-WTF 적용 템플릿 사용
app = Flask(__name__, template_folder='templates_wtf')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'super_secret_key')  # 세션 관리를 위한 비밀키

# 보안 설정 (HTTPS 적용 시 필수)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS에서만 쿠키 전송
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Flask-WTF CSRF 보호 초기화
csrf = CSRFProtect(app)

DB_PATH = os.environ.get('DB_PATH', 'schedule.db')

# --- 데이터베이스 관리 함수 ---

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # 결과를 딕셔너리처럼 사용 가능하게 함
    return conn

def init_db():
    """DB 초기화 및 테이블 생성"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    
    # 데이터가 비어있으면 초기 데이터 삽입
    cur = conn.execute('SELECT count(*) FROM posts')
    if cur.fetchone()[0] == 0:
        insert_default_data(conn)
        print("기본 데이터가 입력되었습니다.")
    
    conn.commit()
    conn.close()

def insert_default_data(conn):
    """요청하신 초기 내용을 DB에 삽입"""
    default_data = [
        ("전체 일정", "실습 프로젝트 기간", "12월 10일 ~ 1월 5일"),
        
        ("일일 일정", "12월 2일 화요일 업무", 
"""- 프로젝트 세부 주제 결정을 위한 자료 탐색
- 세부 주제 선정
  - 주제 선정 제안서 : 공유폴더에 제출
- 팀 프로젝트 일정 계획 수립

- 오전 9시 : 시작 팀 회의 / 금일 작업 내용 계획
- 오후 5시 : 마감 팀 회의
  - 작업 완료 내용 공유
  - 코드 리뷰 등 정보 공유
  - 문제 발생시 대책 방안 회의"""),
        
        ("수업 공지", "금주 수업 시간표", 
"""- 수 10시 ~ 1시 : 리눅스 기초
- 목 10시 ~ 1시 : ssh로 리눅스 서버에 원격 접속하기
- 금 10시 ~ 1시 : crontab을 이용한 배치작업"""),
        
        ("팀 구성", "A team", 
"""- 주제: 사용자 리뷰를 활용한 스마트 상권 감성 분석 서비스
- 팀원: 팀원 명단 작성하기 """),
        
        ("팀 구성", "B team", 
"""- 주제: AI기반 뉴스 분석을 이용한 주식 투자 어드바이저 서비스
- 팀원: 팀원 명단 작성하기""")
    ]
    
    conn.executemany('INSERT INTO posts (category, title, content) VALUES (?, ?, ?)', default_data)

# 앱 시작 시 DB 초기화 실행
with app.app_context():
    init_db()

# --- 라우트 (URL 연결) ---

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    
    # 데이터를 카테고리별로 그룹화
    grouped_posts = {}
    # 순서를 유지하기 위해 카테고리 순서 리스트 정의
    category_order = ["전체 일정", "일일 일정", "수업 공지", "팀 구성"]
    
    for post in posts:
        cat = post['category']
        if cat not in grouped_posts:
            grouped_posts[cat] = []
        grouped_posts[cat].append(post)
            
    return render_template('index.html', grouped_posts=grouped_posts, order=category_order)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # 간단한 로그인 체크 (실제 서비스에선 더 강력한 보안 필요)
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    
    if request.method == 'POST':
        category = request.form['category']
        title = request.form['title']
        content = request.form['content']
        
        if category and title and content:
            conn.execute('INSERT INTO posts (category, title, content) VALUES (?, ?, ?)',
                         (category, title, content))
            conn.commit()
            flash('새로운 내용이 추가되었습니다.')
            return redirect(url_for('admin'))

    posts = conn.execute('SELECT * FROM posts ORDER BY category, id').fetchall()
    conn.close()
    return render_template('admin.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 비밀번호는 환경변수에서 가져옴
        if request.form['password'] == os.environ.get('ADMIN_PASSWORD', 'admin'):
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            flash('비밀번호가 틀렸습니다.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    # Flask-WTF가 자동으로 CSRF 토큰을 검증하므로 수동 검증 로직 제거
        
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('삭제되었습니다.')
    return redirect(url_for('admin'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    # 로그인 확인
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        category = request.form['category']
        title = request.form['title']
        content = request.form['content']

        if category and title and content:
            # DB 업데이트 쿼리 실행
            conn.execute('UPDATE posts SET category = ?, title = ?, content = ? WHERE id = ?',
                         (category, title, content, id))
            conn.commit()
            conn.close()
            flash('내용이 성공적으로 수정되었습니다.')
            return redirect(url_for('admin'))

    conn.close()
    # 게시물이 없으면 관리자 페이지로 리턴 (예외처리)
    if post is None:
        flash('존재하지 않는 게시물입니다.')
        return redirect(url_for('admin'))

    return render_template('edit.html', post=post)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
