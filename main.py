import http.server
import socket
import json
import datetime
import threading
from pathlib import Path
from urllib.parse import parse_qs

PORT_HTTP = 3000
PORT_SOCKET = 5000

STORAGE_DIR = 'storage'
DATA_FILE = 'data.json'

class HTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            with open('index.html', 'rb') as f:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(f.read())
        elif self.path == '/message.html':
            with open('message.html', 'rb') as f:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(f.read())
        elif self.path == '/style.css':
            with open('style.css', 'rb') as f:
                self.send_response(200)
                self.send_header('Content-Type', 'text/css')
                self.end_headers()
                self.wfile.write(f.read())
        elif self.path == '/logo.png':
            with open('logo.png', 'rb') as f:
                self.send_response(200)
                self.send_header('Content-Type', 'image/png')
                self.end_headers()
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            message_data = self.rfile.read(content_length).decode('utf-8')
            message_params = parse_qs(message_data)

            username = message_params['username'][0]
            message_text = message_params['message'][0]

            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            message = {timestamp: {'username': username, 'message': message_text}}

            with open(Path(STORAGE_DIR, DATA_FILE), 'r+') as f:
                data = json.load(f)
                data.update(message)
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()

            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Message received!')

def start_http_server():
    with http.server.HTTPServer(('', PORT_HTTP), HTTPRequestHandler) as httpd:
        print(f'HTTP server listening on port {PORT_HTTP}')
        httpd.serve_forever()

def start_socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('localhost', PORT_SOCKET))
        print(f'Socket server listening on port {PORT_SOCKET}')

        while True:
            data, addr = sock.recvfrom(1024)
            message = json.loads(data.decode('utf-8'))
            print(f'Received message: {message}')

            # Process the message here

if __name__ == '__main__':
    http_thread = threading.Thread(target=start_http_server)
    socket_thread = threading.Thread(target=start_socket_server)

    http_thread.start()
    socket_thread.start()

    http_thread.join()
    socket_thread.join()