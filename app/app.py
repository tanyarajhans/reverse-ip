# A simple Flask application to reverse IP addresses and store them in a PostgreSQL database.

from flask import Flask, request
import os
import psycopg2

app = Flask(__name__)

DB_PARAMS = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS")
}

def store_ip(reverse_ip):
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute("INSERT INTO reverse_ips (ip) VALUES (%s);", (reverse_ip,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"DB error: {e}")

@app.route("/")
def reverse_ip():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    reversed_ip = '.'.join(reversed(ip.split('.')))
    store_ip(reversed_ip)
    return f"Reversed IP: {reversed_ip}\n"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
