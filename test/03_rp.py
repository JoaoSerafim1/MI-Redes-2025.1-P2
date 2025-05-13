import http.server
import socket
import json


port = 8025


class CustomHTTPServer(http.server.HTTPServer):

    def server_bind(self):

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()

class RequestHandler(http.server.BaseHTTPRequestHandler):

    def do_POST(self):
         
        if self.path == '/submit':
            
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                
                data = json.loads(post_data)
            
            except json.JSONDecodeError:
                
                self.send_response(400)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b"Invalid JSON")
                return
            
            self.send_response(201)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response_data = {"message": "Data received", "received_data": data}
            self.wfile.write(json.dumps(response_data).encode())
        
        else:
            
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not found")

server_address = ('', port)
httpd = CustomHTTPServer(server_address, RequestHandler)
print(f"Server listening on port {port}")
httpd.serve_forever()