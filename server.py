import postgresql
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

class MyHandler(BaseHTTPRequestHandler):
    def _get_db(self):
        # use environment variables but defaults to local if not set
        dbHost = os.getenv('POSTGRES_PORT_5432_TCP_ADDR', 'localhost')
        dbPort = os.getenv('POSTGRES_PORT_5432_TCP_PORT', '5432')
        return postgresql.open('pq://dockerworkshop:dockerworkshop@{0}:{1}/dockerworkshop'.format(dbHost, dbPort))

    def _send_response(self, content):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write((content+'\n').encode("utf-8"))

    def _serialize(self, rows):
        return json.dumps({
            'count': len(rows),
            'rows': [{'id': row[0], 'created_at': str(row[1]), 'payload': row[2]} for row in rows]
        })

    def do_GET(self):
        print ("Received GET request")
        rows = self._get_db().query("SELECT id, created_at, payload FROM call")
        self._send_response(self._serialize(rows))

    def do_POST(self):
        print ("Received POST request")
        post_body = self.rfile.read(int(self.headers.get('content-length', 0))).decode("utf-8")
        rows = self._get_db().query("INSERT INTO call (payload) VALUES ($1) RETURNING *", post_body)
        self._send_response(self._serialize(rows))

print("Server is running on port 8080")
server = HTTPServer(('', 8080), MyHandler)
server.serve_forever()
