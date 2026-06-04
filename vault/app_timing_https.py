from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import json

class HTTPSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")

        print("Peticion HTTPS normal recibida")
        print(f"Payload: {body}")

        response = {
            "status": "ok",
            "message": "HTTPS normal request successful"
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))

server_address = ("0.0.0.0", 8444)
httpd = HTTPServer(server_address, HTTPSHandler)

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_NONE
context.load_cert_chain(certfile="certs/server.crt", keyfile="certs/server.key")

httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print("Servidor HTTPS normal escuchando en https://0.0.0.0:8444")
httpd.serve_forever()