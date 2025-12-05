import os
from flask import Flask, render_template, request, redirect, session, url_for
import pymysql
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'secret_key_for_session'  

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

REGIONS = [
    '신부동', '두정동', '쌍용동', '불당동', '성정동', 
    '안서동', '백석동', '신방동', '청당동', '성성동', 
    '차암동', '원성동', '봉명동', '일봉동', '중앙동', 
    '문성동', '부성동', '청룡동', '신안동', '영성동',
    '목천읍', '성환읍', '성거읍', '직산읍', 
    '풍세면', '광덕면', '북면', '성남면', 
    '수신면', '병천면', '동면', '입장면'
]

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='1234',
        db='study_group_db',
        charset='utf8',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if user:
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            return redirect(url_for('dashboard'))
        else:
            return "<script>alert('이메일 또는 비밀번호가 틀렸습니다.');history.back();</script>"
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO users (name, age, gender, email, password, location) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (request.form['name'], request.form['age'], request.form['gender'], 
                  request.form['email'], request.form['password'], request.form['location']))
            
            conn.commit()
            return redirect(url_for('login'))
        except Exception as e:
            return f"<script>alert('오류 발생: {e}');history.back();</script>"
        finally:
            cur.close()
            conn.close()
            
    return render_template('signup.html', regions=REGIONS)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM subjects")
    all_subjects = cur.fetchall()
    
    page = request.args.get('page', 1, type=int)
    limit = 6 
    offset = (page - 1) * limit
    
    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category', '').strip()
    location = request.args.get('location', '').strip()
    sort = request.args.get('sort', 'newest')

    where_clause = "WHERE 1=1"
    params = []

    if keyword:
        where_clause += " AND (gName LIKE %s OR info LIKE %s)"
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    if category and category != '전체':
        where_clause += " AND subject = %s"
        params.append(category)
    if location and location != '전체':
        where_clause += " AND location = %s"
        params.append(location)


    cur.execute(f"SELECT COUNT(*) as count FROM `groups` {where_clause}", params)
    total_count = cur.fetchone()['count']
    total_pages = (total_count + limit - 1) // limit

    order_clause = "ORDER BY gName ASC" if sort == 'name' else "ORDER BY group_id DESC"

    sql = f"SELECT * FROM `groups` {where_clause} {order_clause} LIMIT %s OFFSET %s"
    cur.execute(sql, params + [limit, offset])
    groups = cur.fetchall()
    
    cur.execute("""
        SELECT g.gName, gm.status 
        FROM group_members gm 
        JOIN `groups` g ON gm.group_id = g.group_id 
        WHERE gm.user_id = %s
    """, (session['user_id'],))
    my_status = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('dashboard.html', 
                           groups=groups, my_status=my_status, name=session['name'],
                           all_subjects=all_subjects, regions=REGIONS,
                           page=page, total_pages=total_pages,
                           keyword=keyword, category=category, location=location, sort=sort)

@app.route('/create_group', methods=['GET', 'POST'])
def create_group():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM subjects")
    subjects = cur.fetchall()
    
    if request.method == 'POST':
        try:
            cur.execute("""
                INSERT INTO `groups` (gName, subject, location, info, group_leader_id) 
                VALUES (%s, %s, %s, %s, %s)
            """, (request.form['gName'], request.form['subject'], request.form['location'], request.form['info'], session['user_id']))
            group_id = conn.insert_id()
            
            cur.execute("INSERT INTO group_members (group_id, user_id, status) VALUES (%s, %s, 'approved')", 
                        (group_id, session['user_id']))
            conn.commit()
            return redirect(url_for('dashboard'))
        except Exception as e:
            return f"에러: {e}"
        finally:
            cur.close()
            conn.close()
            
    cur.close()
    conn.close()
    return render_template('create_group.html', subjects=subjects, regions=REGIONS)

@app.route('/join_group/<int:group_id>')
def join_group(group_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM group_members WHERE group_id=%s AND user_id=%s", (group_id, session['user_id']))
    if not cur.fetchone():
        cur.execute("INSERT INTO group_members (group_id, user_id) VALUES (%s, %s)", (group_id, session['user_id']))
        conn.commit()
    
    cur.close()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/manage_group/<int:group_id>')
def manage_group(group_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM `groups` WHERE group_id=%s", (group_id,))
    group = cur.fetchone()

    if group['group_leader_id'] != session['user_id']:
        return "<script>alert('권한이 없습니다.');location.href='/dashboard';</script>"
    
    cur.execute("""
        SELECT u.user_id, u.name, u.email, u.location 
        FROM group_members gm JOIN users u ON gm.user_id = u.user_id
        WHERE gm.group_id = %s AND gm.status = 'pending'
    """, (group_id,))
    pending_users = cur.fetchall()

    cur.execute("""
        SELECT u.user_id, u.name, u.email, u.location
        FROM group_members gm JOIN users u ON gm.user_id = u.user_id
        WHERE gm.group_id = %s AND gm.status = 'approved' AND u.user_id != %s
    """, (group_id, session['user_id']))
    current_members = cur.fetchall()
    
    cur.close()
    conn.close()
    return render_template('manage_group.html', group=group, pending_users=pending_users, current_members=current_members)

@app.route('/approve_member/<int:group_id>/<int:user_id>')
def approve_member(group_id, user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE group_members SET status = 'approved' WHERE group_id = %s AND user_id = %s", (group_id, user_id))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_group', group_id=group_id))

@app.route('/kick_member/<int:group_id>/<int:user_id>')
def kick_member(group_id, user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM group_members WHERE group_id = %s AND user_id = %s", (group_id, user_id))
    conn.commit()
    conn.close()
    return redirect(url_for('manage_group', group_id=group_id))

@app.route('/delegate_leader/<int:group_id>/<int:new_leader_id>')
def delegate_leader(group_id, new_leader_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE `groups` SET group_leader_id = %s WHERE group_id = %s", (new_leader_id, group_id))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete_group/<int:group_id>')
def delete_group(group_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM `groups` WHERE group_id = %s", (group_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('mypage'))

@app.route('/leave_group/<int:group_id>')
def leave_group(group_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM group_members WHERE group_id = %s AND user_id = %s", (group_id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('mypage'))

@app.route('/group/<int:group_id>')
def group_board(group_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM group_members WHERE group_id=%s AND user_id=%s AND status='approved'", (group_id, session['user_id']))
    if not cur.fetchone():
        return "<script>alert('승인된 멤버만 입장 가능합니다.');location.href='/dashboard';</script>"

    cur.execute("SELECT * FROM `groups` WHERE group_id = %s", (group_id,))
    group = cur.fetchone()

    cur.execute("""
        SELECT p.*, u.name as author_name 
        FROM posts p JOIN users u ON p.author_id = u.user_id
        WHERE p.group_id = %s ORDER BY p.post_id DESC
    """, (group_id,))
    posts = cur.fetchall()
    
    cur.close()
    conn.close()
    return render_template('group_board.html', group=group, posts=posts)

@app.route('/write_post/<int:group_id>', methods=['POST'])
def write_post(group_id):
    content = request.form['content']
    file = request.files.get('image')
    filename = None
    
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO posts (content, author_id, group_id, image_path) VALUES (%s, %s, %s, %s)", 
                (content, session['user_id'], group_id, filename))
    conn.commit()
    conn.close()
    return redirect(url_for('group_board', group_id=group_id))

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        cur.execute("INSERT INTO comments (post_id, content, user_id) VALUES (%s, %s, %s)", 
                    (post_id, request.form['comment'], session['user_id']))
        conn.commit()
        return redirect(url_for('post_detail', post_id=post_id))

    cur.execute("""
        SELECT p.*, u.name as author_name 
        FROM posts p
        JOIN users u ON p.author_id = u.user_id
        WHERE p.post_id = %s
    """, (post_id,))
    post = cur.fetchone()
    
    cur.execute("SELECT * FROM `groups` WHERE group_id = %s", (post['group_id'],))
    group = cur.fetchone()

    cur.execute("""
        SELECT c.*, u.name as commenter_name 
        FROM comments c
        JOIN users u ON c.user_id = u.user_id
        WHERE c.post_id = %s
        ORDER BY c.comment_id ASC
    """, (post_id,))
    comments = cur.fetchall()

    cur.close()
    conn.close()
    
    return render_template('post_detail.html', post=post, comments=comments, group=group)
@app.route('/delete_post/<int:post_id>')
def delete_post(post_id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT group_id, author_id FROM posts WHERE post_id = %s", (post_id,))
    post = cur.fetchone()
    
    if post and post['author_id'] == session['user_id']:
        cur.execute("DELETE FROM posts WHERE post_id = %s", (post_id,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('group_board', group_id=post['group_id']))
    else:
        return "<script>alert('권한이 없습니다.');history.back();</script>"

@app.route('/mypage')
def mypage():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()
   
    cur.execute("SELECT * FROM users WHERE user_id = %s", (session['user_id'],))
    my_info = cur.fetchone()
    
    cur.execute("SELECT * FROM `groups` WHERE group_leader_id = %s ORDER BY group_id DESC", (session['user_id'],))
    leader_groups = cur.fetchall()
    
    cur.execute("""
        SELECT g.*, gm.status FROM group_members gm 
        JOIN `groups` g ON gm.group_id = g.group_id 
        WHERE gm.user_id = %s AND g.group_leader_id != %s ORDER BY g.group_id DESC
    """, (session['user_id'], session['user_id']))
    member_groups = cur.fetchall()

    cur.execute("SELECT * FROM study_logs WHERE user_id = %s ORDER BY log_id DESC", (session['user_id'],))
    study_logs = cur.fetchall()

    cur.execute("SELECT * FROM subjects")
    subjects = cur.fetchall()
    
    cur.close()
    conn.close()
    return render_template('mypage.html', my_info=my_info, leader_groups=leader_groups, member_groups=member_groups, study_logs=study_logs, subjects=subjects)

@app.route('/add_log', methods=['POST'])
def add_log():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO study_logs (user_id, subject, minutes, content) VALUES (%s, %s, %s, %s)", 
                (session['user_id'], request.form['subject'], request.form['minutes'], request.form['content']))
    conn.commit()
    conn.close()
    return redirect(url_for('mypage'))

@app.route('/delete_log/<int:log_id>')
def delete_log(log_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM study_logs WHERE log_id = %s AND user_id = %s", (log_id, session['user_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('mypage'))

def is_admin():
    if 'user_id' not in session: return False
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT email FROM users WHERE user_id = %s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user and user['email'] == 'admin@test.com'

@app.route('/admin')
def admin():
    if not is_admin():
        return "<script>alert('관리자만 접근할 수 있습니다!');location.href='/dashboard';</script>"

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users ORDER BY user_id DESC")
    all_users = cur.fetchall()

    cur.execute("SELECT * FROM `groups` ORDER BY group_id DESC")
    all_groups = cur.fetchall()
    
    cur.execute("""
        SELECT l.*, u.name as user_name 
        FROM study_logs l
        JOIN users u ON l.user_id = u.user_id
        ORDER BY l.log_id DESC LIMIT 50
    """)
    all_logs = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template('admin.html', all_users=all_users, all_groups=all_groups, all_logs=all_logs)

@app.route('/admin/delete_user/<int:user_id>')
def admin_delete_user(user_id):
    if not is_admin(): return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

@app.route('/admin/delete_group/<int:group_id>')
def admin_delete_group(group_id):
    if not is_admin(): return redirect(url_for('dashboard'))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM `groups` WHERE group_id = %s", (group_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)