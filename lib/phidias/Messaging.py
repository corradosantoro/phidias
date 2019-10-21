#
#
#

#from __future__ import print_function
import sys

if sys.implementation.name != "micropython":

    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import urlparse
    from io import BytesIO

    import threading
    import json
    import requests

    class PhidiasHTTPServer_RequestHandler(BaseHTTPRequestHandler):

        engines = None
        _globals = None
        port = 0

        def do_GET(self):
            self.send_response(500)
            #self.send_header('Content-type','text/html')
            #self.end_headers()
            #message = "Hello world!"
            #self.wfile.write(bytes(message, "utf8"))
            return

        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            self.send_response(200)
            self.end_headers()
            payload = json.loads(body.decode())
            # payload = { 'from' : source,
            #             'to': agent_name,
            #             'data' : ['belief', [ belief.name(), belief.string_terms() ] ] }
            response = { 'result' : 'err',
                        'reason' : 'Malformed HTTP payload',
                        'data'   : payload }
            if 'from' in payload.keys():
                if 'net-port' in payload.keys():
                    if 'to' in payload.keys():
                        if 'data' in payload.keys():
                            # format is valid
                            _from = payload['from']
                            _to = payload['to']
                            _data = payload['data']
                            _net_port = payload['net-port']
                            if _net_port == 0:
                                _from = _from + "@<unknown>"
                            else:
                                _from = _from + "@" + self.client_address[0] + ":" + repr(_net_port)
                            if _to in PhidiasHTTPServer_RequestHandler.engines.keys():
                                if _data[0] == 'belief':
                                    [ Name, Terms ] = _data[1]
                                    k = PhidiasHTTPServer_RequestHandler._globals[Name]
                                    b = k()
                                    b.make_terms(Terms)
                                    b.source_agent = _from
                                    e = PhidiasHTTPServer_RequestHandler.engines[_to]
                                    e.add_belief(b)
                                    response = { 'result' : 'ok' }
                                else:
                                    response = { 'result' : 'err',
                                                'reason' : 'Invalid verb',
                                                'data'   : _data }
                            else:
                                response = { 'result' : 'err',
                                            'reason' : 'Destination agent not found',
                                            'data'   : _to }

            body = json.dumps(response)
            response = BytesIO()
            response.write(body.encode())
            self.wfile.write(response.getvalue())

        def log_message(self, format, *args):
            return


    def server_thread(port):
        server_address = ('', port)
        PhidiasHTTPServer_RequestHandler.port = port
        httpd = HTTPServer(server_address, PhidiasHTTPServer_RequestHandler)
        print("")
        print("\tPHIDIAS Messaging Server is running at port ", port)
        print("")
        print("")
        #print(httpd.socket)
        httpd.serve_forever()
        server_thread()

    def start_message_server(port, engines, _globals):
        PhidiasHTTPServer_RequestHandler.engines = engines
        PhidiasHTTPServer_RequestHandler._globals = _globals
        t = threading.Thread(target = server_thread, args = (port, ))
        t.daemon = True
        t.start()
        return t


class Messaging:

    @classmethod
    def local_or_remote(cls, agent_name):
        at_pos = agent_name.find("@")
        if at_pos < 0:
            return (False, None, None)
        else:
            agent_local_name = agent_name[:at_pos]
            site_name = agent_name[at_pos + 1:]
            return (True, agent_local_name, site_name)

    @classmethod
    def send_belief(cls, agent_name, destination, belief, source):
        parsed_url = urlparse("//" + destination)
        if parsed_url.hostname is None:
            raise InvalidDestinationException()
        port = parsed_url.port
        if port is None:
            port = 6565

        payload = { 'from' : source,
                    'net-port': PhidiasHTTPServer_RequestHandler.port,
                    'to': agent_name,
                    'data' : ['belief', [ belief.name(), belief.string_terms() ] ] }

        json_payload = json.dumps(payload)
        #print(json_payload)
        new_url = "http://" + parsed_url.hostname + ":" + str(port)
        r = requests.post(new_url, data=json_payload)
        reply = json.loads(r.text)
        if reply['result'] != "ok":
            print("Messaging Error: ", reply)


