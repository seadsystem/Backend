import http.server
from DB.api import url_parser
from DB.api import query_db
from DB.api import insert_db

USAGE = "Usage: http://db.sead.systems:8080/(device id)['?' + '&'.join(.[[start_time=(start time as UTC unix timestamp)],\n" \
        "[end_time=(end time as UTC unix timestamp)], [type=(Sensor type code),[device=(seadplug for SEAD plug,\n" \
        "egauge or channel name for eGauge), granularity=(interval between data points in seconds of an energy list\n" \
        "query, must also include list_format=energy and type=P), [diff=(1 get the data differences instead of the data),\n" \
        "event=(threshold of event detection, must also include device and type=P and list_format=event)]]]],\n" \
        "[subset=(subsample result down to this many rows)], [list_format=(string representing what the json list entries\n" \
        "will look like)], [limit=(truncate result to this many rows)], [json=(1 get the result in pseudo JSON format)]]\n"


class ApiHandler(http.server.CGIHTTPRequestHandler):
    def __init__(self, req, client_addr, server):
        http.server.CGIHTTPRequestHandler.__init__(self, req, client_addr, server)

    def do_GET(self):
        try:
            parsed = url_parser.get_parse(self.path)
        except Exception as inst:
            if self.path == '/':
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(USAGE.encode("utf-8"))
                self.wfile.flush()
            else:
                print(type(inst))
                print(inst.args)
                print(inst)

                self.send_error(404)
            return

        try:
            r = query_db.query(parsed)

            self.send_response(200)
            self.send_header("Content-type",
                             "application/json;charset=utf-8")  # Not actually using JSON format. Causes errors in Chrome when it tries to validate
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            for line in r:
                self.wfile.write(line.encode("utf-8"))
        except Exception as inst:

            self.send_error(500)
            print(type(inst))
            print(inst.args)
            print(str(inst))

            return

        self.wfile.flush()

    def do_POST(self):
        try:
            parsed = url_parser.post_parse(self.path)
        except Exception as e:
            self.send_error(400)
            print(type(e))
            print(e.args)
            print(e)

        try:
            content_len = int(self.headers.get('Content-Length', ''))
            post_body = self.rfile.read(content_len).decode('utf-8')
            result = insert_db.insert(parsed, post_body)
            content = bytes(result, "utf-8")
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500)
            print(type(e))
            print(e.args)
            print(e)



