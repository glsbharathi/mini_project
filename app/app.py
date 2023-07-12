from flask import Flask, render_template, request, session, redirect, url_for
import mysql.connector
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Configure MySQL
try:
    db = mysql.connector.connect(
        user= "root",
        password= "root",
        host= "db",
        port= 3306,
        database= "c361",
        auth_plugin="mysql_native_password"
    )
    print ("Connected to MYSQL")
except mysql.connector.Error as error:
    print ("Error connecting to MYSQL:{error}")

@app.route('/')
def index():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM complaints")
    complaints = cursor.fetchall()
    cursor.close()
    return render_template('index.html', complaints=complaints, logged_in=('username' in session))



@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        details = request.form
        name = details['name']
        complaint = details['complaint']
        cursor = db.cursor()
        sql = "INSERT INTO complaints (name, complaint, complaint_time) VALUES (%s, %s, %s)"
        values = (name, complaint, datetime.now())
        cursor.execute(sql, values)
        db.commit()
        cursor.close()
        return 'Complaint submitted successfully'


@app.route('/resolve/<int:complaint_id>', methods=['GET', 'POST'])
def resolve(complaint_id):
    if 'username' in session:
        if request.method == 'POST':
            solution = request.form['solution']
            cursor = db.cursor()
            sql = "UPDATE complaints SET resolved = TRUE, solution = %s, resolved_time = %s WHERE id = %s"
            values = (solution, datetime.now(), complaint_id)
            cursor.execute(sql, values)
            db.commit()
            cursor.close()
            return redirect(url_for('admin'))
        else:
            cursor = db.cursor()
            sql = "SELECT * FROM complaints WHERE id = %s"
            values = (complaint_id,)
            cursor.execute(sql, values)
            complaint = cursor.fetchone()
            cursor.close()
            return render_template('resolve.html', complaint=complaint)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # You can replace this simple authentication with your own logic
        if username == 'admin' and password == 'admin123':
            session['username'] = username
            return redirect(url_for('admin'))
        else:
            return 'Invalid username or password'

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

from datetime import datetime

# ...

@app.route('/admin')
def admin():
    if 'username' in session and session['username'] == 'admin':
        cursor = db.cursor()
        cursor.execute("SELECT * FROM complaints")
        complaints = cursor.fetchall()
        cursor.close()

        # Add the current time to the resolved complaints
        for complaint in complaints:
            if complaint[4]:  # Check if complaint is resolved
                complaint_time = complaint[3]
                resolved_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                complaint += (resolved_time,)  # Add resolved time to the complaint tuple

        return render_template('admin.html', complaints=complaints)
    else:
        return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True, port=5500, host='0.0.0.0')
