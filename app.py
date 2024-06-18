# app.py

from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3
import smtplib
import random
import string
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Database setup
def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY,
                        email TEXT UNIQUE,
                        username TEXT,
                        password TEXT,
                        verified INTEGER DEFAULT 0)''')
    conn.close()

init_db()

#Function to check if email is registered

def registered(email):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

print(registered('felix@gmail.com'))

# Function to send email
def send_verification_email(email, code):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        subject = 'Your Verification Code'
        body = f'Your verification code is: {code}'
        msg = f'Subject: {subject}\n\n{body}'
        smtp.sendmail(EMAIL_ADDRESS, email, msg)

# Route to handle user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        session['verification_code'] = verification_code
        session['email'] = email
        session['username'] = username
        session['password'] = password
        if registered(email) == False:
            send_verification_email(email, verification_code)
            return redirect(url_for('verify'))
        else:
            return render_template('error.html')
    return render_template('register.html')

# Route to handle verification
@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        user_code = request.form['code']
        if user_code == session['verification_code']:
            with sqlite3.connect('database.db') as conn:
                conn.execute('INSERT INTO users (email, username, password, verified) VALUES (?, ?, ?, ?)',
                             (session['email'], session['username'], session['password'], 1))
            return 'Verification successful and user registered!'
        else:
            return 'Verification failed. Incorrect code.'
    return render_template('verify.html')

if __name__ == '__main__':
    app.run(debug=True)
