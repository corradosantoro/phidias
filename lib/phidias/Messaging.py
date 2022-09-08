#
#
#

#from __future__ import print_function
import json
import sys
import threading
import socket

# Depending on the selected protocol, beliefs will be sent using different functions
send_belief_impl = None


### "http" protocol

if sys.implementation.name == "micropython":
    def start_message_server_http(engines, _globals, port):
        raise NotImplementedError("'http' protocol is not supported on the micropython platform")
else:
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import urlparse
    from io import BytesIO

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
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            payload = json.loads(body.decode())
            # payload = { 'from' : source,
            #             'to': agent_name,
            #             'data' : ['belief', [ belief.name(), belief.string_terms() ] ] }
            response = process_incoming_request(
                PhidiasHTTPServer_RequestHandler.engines,
                PhidiasHTTPServer_RequestHandler._globals,
                self.client_address[0],
                payload)

            body = json.dumps(response)
            response = BytesIO()
            response.write(body.encode())
            self.wfile.write(response.getvalue())

        def log_message(self, format, *args):
            return


    def send_belief_http(agent_name, destination, belief, source):
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

    def server_thread_http(port):
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

    def start_message_server_http(engines, _globals, port = 6565):
        global send_belief_impl
        send_belief_impl = send_belief_http

        PhidiasHTTPServer_RequestHandler.engines = engines
        PhidiasHTTPServer_RequestHandler._globals = _globals
        t = threading.Thread(target = server_thread_http, args = (port, ))
        t.daemon = True
        t.start()
        return t


### "gateway" protocol

class GatewayConnectionSentRequest:  # Future-like object
    def __init__(self):
        self._result = None
        self._cond = threading.Condition()

    def set_result(self, result):
        with self._cond:
            self._result = result
            self._cond.notify_all()

    def result(self):
        with self._cond:
            while self._result is None:
                self._cond.wait()

        return self._result

class GatewayConnectionHandler:
    def __init__(self, engines, _globals, sock):
        self.engines = engines
        self._globals = _globals
        self.sock = sock

        self.lock = threading.Lock()
        self.sent_requests_queue = []

    def send_belief(self, agent_name, destination, belief, source):
        colon_pos = destination.find(":")
        if colon_pos < 0:
            to_address = destination
            to_port = 6565
        else:
            to_address = destination[:colon_pos]
            to_port = int(destination[colon_pos + 1:])

        # Prepare payload
        payload = { 'from' : source,
                    'to': agent_name,
                    'data' : ['belief', [ belief.name(), belief.string_terms() ] ],
                    'to-address': to_address,
                    'to-port': to_port }
        json_payload = json.dumps(payload).encode('ascii') + b'\n'
        #print('PAYLOAD:', payload)

        # Send request
        req = GatewayConnectionSentRequest()
        with self.lock:
            self.sent_requests_queue.append(req)
            self.sock.sendall(json_payload)

        # Wait for result
        reply = req.result()
        if reply['result'] != "ok":
            print("Messaging Error: ", reply)

    def server_thread(self):
        incoming_buffer = b''
        while True:
            new_data = self.sock.recv(64)
            if len(new_data) == 0:
                raise RuntimeError('Lost connection to gateway')
            incoming_buffer += new_data

            while True:
                nl_pos = incoming_buffer.find(b"\n")
                if nl_pos < 0:
                    break  # no full message yet, keep on waiting

                response_payload = json.loads(incoming_buffer[:nl_pos])
                incoming_buffer = incoming_buffer[nl_pos + 1:]

                # Process the message
                with self.lock:
                    if 'result' in response_payload:  # response to our past request
                        self.sent_requests_queue.pop(0).set_result(response_payload)
                    else:  # incoming request
                        from_address = response_payload.pop('from-address')
                        response = process_incoming_request(self.engines, self._globals, from_address, response_payload)

                        json_response = json.dumps(response).encode('ascii') + b'\n'
                        self.sock.sendall(json_response)

def start_message_server_gateway(engines, _globals, gateway_sock):
    global send_belief_impl

    h = GatewayConnectionHandler(engines, _globals, gateway_sock)
    send_belief_impl = h.send_belief
    t = threading.Thread(target = h.server_thread)
    t.daemon = True
    t.start()
    return t


### protocol-independent

def process_incoming_request(engines, _globals, from_address, payload):
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
                        _from = _from + "@" + from_address + ":" + repr(_net_port)
                    if _to in engines.keys():
                        if _data[0] == 'belief':
                            [ Name, Terms ] = _data[1]
                            k = _globals[Name]
                            b = k()
                            b.make_terms(Terms)
                            b.source_agent = _from
                            e = engines[_to]
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
    return response

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
        send_belief_impl(agent_name, destination, belief, source)
