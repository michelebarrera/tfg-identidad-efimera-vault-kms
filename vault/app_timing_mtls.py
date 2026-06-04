from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl
import json

AUTHORIZED_CLIENTS = [
    "lambda-client.tfg.local"
]

class MTLSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        cert = self.connection.getpeercert()

        if not cert:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Client certificate required")
            return

        subject = dict(x[0] for x in cert.get("subject", []))
        client_cn = subject.get("commonName", "unknown")

        if client_cn not in AUTHORIZED_CLIENTS:
            self.send_response(403)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            response = {
                "status": "forbidden",
                "message": "Client identity is not authorized",
                "client_identity": client_cn
            }

            self.wfile.write(json.dumps(response).encode("utf-8"))
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")

        print(f"Peticion mTLS recibida de: {client_cn}")
        print(f"Payload: {body}")

        response = {
            "status": "ok",
            "message": "mTLS verification successful",
            "client_identity": client_cn
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))

server_address = ("0.0.0.0", 8443)
httpd = HTTPServer(server_address, MTLSHandler)

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile="certs/server.crt", keyfile="certs/server.key")
context.load_verify_locations(cafile="certs/ca.crt")

httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print("Servidor mTLS escuchando en https://0.0.0.0:8443")
httpd.serve_forever()