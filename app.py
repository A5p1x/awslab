from flask import Flask, Response
import mysql.connector

app = Flask(__name__)

def query_database():
    db = mysql.connector.connect(
        host="",  # Replace with your MySQL host
        user="",  # Replace with your MySQL username
        password="",  # Replace with your MySQL password
        database="mydb"  # Replace with your MySQL database
    )
    cursor = db.cursor()
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result[0] if result else "No data"

@app.route('/')
def query():
    result = query_database()
    return Response(str(result), mimetype='text/plain')

if __name__ == '__main__':
    # Provide the path to your certificate and private key
    context = ('cert.pem', 'key.pem')
    app.run(debug=True, port=443, host='0.0.0.0', ssl_context=context)

