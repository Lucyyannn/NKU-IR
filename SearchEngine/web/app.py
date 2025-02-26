from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib
import os
import time
from  spider.query import personalized_search,recommend_search,get_history_to_display,get_history_to_compute,snapshot

app = Flask(__name__)
app.secret_key = '123456'  # 设置session密钥

# 密码加密
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 数据库连接
def get_db_connection():
    conn = sqlite3.connect('history.db')
    conn.row_factory = sqlite3.Row
    return conn

# 注册页面
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] or '000000'
        interest1 = request.form['interest1']
        interest2 = request.form['interest2']
        interest3 = request.form['interest3']
        hashed_password = hash_password(password)

        conn = get_db_connection()
        try:
            #插入用户信息
            conn.execute('''INSERT INTO users (username, password, interest1, interest2, interest3) 
                VALUES (?, ?, ?, ?, ?)
            ''', (username, hashed_password, interest1, interest2, interest3))

            conn.commit()
            flash('注册成功！', 'success')
            #return redirect(url_for('search'))#回到主页面
        except sqlite3.IntegrityError:
            flash('用户名已存在！', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

# 登录页面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()

        if user:
            # 用户名正确，检查密码
            if hash_password(password) == user['password']:
                session['user_id'] = user['id']
                session['username'] = username
                flash('登录成功，回到主页面...', 'success')
                #return redirect(url_for('search'))  # 登录成功后跳转到搜索页面
                return render_template('login.html')
            else:
                flash('密码错误！', 'danger')  # 密码错误
        else:
            flash('用户名错误！', 'danger')  # 用户名错误

    return render_template('login.html')

# 搜索页面
@app.route('/', methods=['GET', 'POST'])
def search():
    # 检查用户是否登录
    if 'user_id' not in session:
        # 未登录，显示空的搜索框，不显示历史记录
        return render_template('search.html', username=None, history=[])

    # 已登录，加载搜索历史
    conn = get_db_connection()
    query = ""
    results = []
    search_time = 0  

    # 获取历史记录（去重后保留最新记录）
    history = get_history_to_display(conn, session['user_id'])#去重的
    history_forcom=get_history_to_compute(conn, session['user_id'])#未去重的

    #查询搜索
    if request.method == 'POST':
        if request.form.get('clear_history')=='1':
            # 清空历史记录
            conn.execute("DELETE FROM search_history WHERE user_id = ?", (session['user_id'],))
            conn.commit()
            flash('历史记录已清空！', 'success')  
        else:
            query = request.form['query']  # 获取查询语句
            # 记录搜索历史
            conn.execute("INSERT INTO search_history (user_id, query, timestamp) VALUES (?, ?, ?)",
                            (session['user_id'], query, time.time()))
            conn.commit()
            
            # 执行搜索，记录时间
            start_time = time.time()
            results = personalized_search(conn,query,session['user_id'])  
            recommendations = recommend_search(history_forcom)
            results = snapshot(results) #添加快照
            search_time = round(time.time() - start_time, 4)
            return render_template('results.html', query=query, results=results,username=session['username'], history=history, search_time=search_time,recommendations=recommendations)

    
    conn.close()

    return render_template('search.html', query=query, username=session['username'], history=history)

# 退出登录
@app.route('/logout')
def logout():
    session.clear()  # 清除session，退出登录
    flash('已退出登录！', 'info')
    return redirect(url_for('search'))  # 退出后重定向到未登录状态的搜索页面

if __name__ == '__main__':
    if not os.path.exists('history.db'):
        os.system('python init_db.py')  # 初始化数据库
    app.run(debug=True)
