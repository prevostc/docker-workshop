import postgresql
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

class MyHandler(BaseHTTPRequestHandler):
    def _get_db(self):
        // use environment variables but defaults to local if not set
        dbHost = os.getenv('POSTGRES_PORT_5432_TCP_ADDR', 'localhost')
        dbPort = os.getenv('POSTGRES_PORT_5432_TCP_PORT', '5432')
        return postgresql.open('pq://dockerworkshop:dockerworkshop@{0}:{1}/dockerworkshop'.format(dbHost, dbPort))

    def do_GET(self):
        db = self._get_db()
        proc = db.proc("version()")
        res = proc()

        self.send_response(200)
        self.send_header('Content-type', 'text/text')
        self.end_headers()

        print("Hey I'm doing stuff")
        self.wfile.write((res+'\n').encode("utf-8"))

server = HTTPServer(('', 8080), MyHandler)
server.serve_forever()
