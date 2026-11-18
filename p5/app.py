from flask import Flask
import mysql.connector
import os

app = Flask(__name__)

@app.route("/")
def home():
    try:
        db = mysql.connector.connect(
            host="db",
            user="root",
            password=os.environ["MYSQL_ROOT_PASSWORD"],
            database=os.environ["MYSQL_DATABASE"]
        )
        cursor = db.cursor()
        cursor.execute("SELECT id, name, course FROM students")
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        table_rows = "".join(f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td></tr>" for r in rows)
        return f"""
        <html><body style="font-family:Arial;text-align:center;margin-top:60px">
        <h1>Docker Compose: Flask + MySQL</h1>
        <p style="color:green">Connected to MySQL successfully!</p>
        <table border="1" cellpadding="8" style="margin:auto">
        <tr><th>ID</th><th>Name</th><th>Course</th></tr>
        {table_rows}
        </table>
        </body></html>
        """
    except mysql.connector.Error as e:
        return f"Database connection failed: {e}", 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
