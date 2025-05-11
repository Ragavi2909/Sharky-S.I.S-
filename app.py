from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
db_config = {
    'user': 'root',
    'password': 'Ragavi_31',
    'host': 'localhost',
    'database': 'student_info_system'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        role = request.form['role']
        department = request.form['department']
        year_of_joining = request.form.get('year_of_joining')

        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if email exists
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return render_template('register.html', error='Email already exists')

        # Hash password
        hashed_password = generate_password_hash(password)

        # Insert user
        cursor.execute('''
            INSERT INTO users (email, password, name, role, department, year_of_joining)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (email, hashed_password, name, role, department, year_of_joining if role == 'student' else None))
        
        conn.commit()
        cursor.close()
        conn.close()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM users WHERE email = %s AND role = %s', (email, role))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']
            
            if user['role'] == 'student':
                return redirect(url_for('student_dashboard'))
            else:
                return redirect(url_for('teacher_dashboard'))
        
        return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/student_dashboard')
def student_dashboard():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template('student_dashboard.html', user=user)

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'user_id' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
    user = cursor.fetchone()
    
    cursor.execute('''
        SELECT n.*, u.name as student_name 
        FROM notifications n 
        JOIN users u ON n.student_id = u.id 
        WHERE n.teacher_id = %s
    ''', (session['user_id'],))
    notifications = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('teacher_dashboard.html', user=user, notifications=notifications)

@app.route('/marks_attendance', methods=['GET', 'POST'])
def marks_attendance():
    if 'user_id' not in session or session['role'] != 'teacher':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        student_id = request.form['student_id']
        semester = request.form['semester']
        marks = request.form['marks']
        attendance = request.form['attendance']
        
        cursor.execute('''
            INSERT INTO marks (student_id, semester, marks, attendance)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE marks = %s, attendance = %s
        ''', (student_id, semester, marks, attendance, marks, attendance))
        
        conn.commit()
        flash('Marks and attendance updated successfully!')
    
    cursor.execute('SELECT id, name, department FROM users WHERE role = "student"')
    students = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('marks_attendance.html', students=students)

@app.route('/view_marks', methods=['GET', 'POST'])
def view_marks():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT * FROM marks WHERE student_id = %s', (session['user_id'],))
    records = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('view_marks.html', records=records)

@app.route('/notify_teacher', methods=['POST'])
def notify_teacher():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    semester = request.form['semester']
    message = request.form['message']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Assuming teacher is assigned to department (simplified)
    cursor.execute('''
        INSERT INTO notifications (student_id, teacher_id, semester, message)
        SELECT %s, id, %s, %s 
        FROM users 
        WHERE role = 'teacher' AND department = (
            SELECT department FROM users WHERE id = %s
        ) LIMIT 1
    ''', (session['user_id'], semester, message, session['user_id']))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Notification sent to teacher!')
    return redirect(url_for('view_marks'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)