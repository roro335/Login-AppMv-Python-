import _mysql_connector
import bcrypt
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import os

db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'login_db'
}
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.path = '/login.html'
        try:
            file_path = 'templates' + self.path
            with open(file_path, 'r') as file:
                file_to_open = file.read()
                self.send_response(200)
        except:
            file_to_open = "File not found"
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_data = urllib.parse.parse_qs(post_data.decode('utf-8'))

        if self.path == '/register':
            username = post_data['usuario'][0]
            password = post_data['contraseña'][0]
            self.register_user(username, password)
            self.path = '/login.html'
        elif self.path == '/login':
            username = post_data['usuario'][0]
            password = post_data['contraseña'][0]
            if self.authenticate_user(username, password):
                self.path = '/home.html'
            else:
                self.path = '/login.html'
        self.do_GET()

    def register_user(self, username, password):
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
        finally:
            cursor.close()
            conn.close()

    def authenticate_user(self, username, password):
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM users WHERE username = %s', (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            hashed = result[0]
            if bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8')):
                return True
        return False

httpd = HTTPServer(('localhost', 8000), SimpleHTTPRequestHandler)
print("Serving on port 8000...")
httpd.serve_forever()