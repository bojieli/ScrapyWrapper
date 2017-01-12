import json
import collections
import sys
import simplejson as json
import sqlite3 as lite
conn = lite.connect('app.db')
cursor = conn.cursor()


PORT = int(sys.argv[1])

import BaseHTTPServer
import cgi
import SocketServer


cursor.execute("PRAGMA table_info(be_app_instruct)")

table_fields = []
for id, field, datatype, size, null, extra in cursor:
        table_fields.append(field)

class MyRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    '''
    Factory generated request handler class that contain
    additional class variables.
    '''
    def do_POST(self):
        '''
        Handle POST requests.
        '''
        # Print out logging information about the path and args.
        query_id = self.path.split('/')[-1]
        cursor.execute("SELECT * FROM be_app_instruct WHERE me_uid = ?", (query_id, ))
        row = cursor.fetchone()
        if not row:
            self.send_response(404)
            return
        row_dict = dict(zip(table_fields, row))
        # Tell the browser everything is okay and that there is
        # HTML to display.
        self.send_response(200)  # OK
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Display the POST variables.
        self.wfile.write(json.dumps(row_dict, ensure_ascii=False, encoding="utf-8").encode('utf-8'))
        self.wfile.close()


server_address = ('', PORT)
httpd = BaseHTTPServer.HTTPServer(server_address, MyRequestHandler)
import os
import sys

print "serving at port", PORT
httpd.serve_forever()

