import postgresql
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        db = postgresql.open('pq://dockerworkshop:dockerworkshop@localhost:5432/dockerworkshop')
        proc = db.proc("version()")
        res = proc()

        self.send_response(200)
        self.send_header('Content-type', 'text/text')
        self.end_headers()

        print("Hey I'm doing stuff")
        self.wfile.write((res+'\n').encode("utf-8"))

server = HTTPServer(('', 8080), MyHandler)
server.serve_forever()
