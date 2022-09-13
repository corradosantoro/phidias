#!/usr/bin/env python3
import argparse
import aiohttp
import asyncio
import collections
import ipaddress
import json
import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

# Convert a string to int and validate as a port number
def port_number(port_argtext):
    port_val = int(port_argtext)
    if 0 < port_val < 65536:
        return port_val
    else:
        raise ValueError('invalid port number: ' + port_str)


# One object of this class exists for each registered embedded device
class EmbeddedDevice:
    def __init__(self, device_argtext):
        # Parse device_argtext (as typed by the user)
        self.device_name, self.local_port = device_argtext.split(':', 1)
        self.local_port = port_number(self.local_port)

        # Current writer for the TCP connection to the embedded device, if
        # currently connected
        self._current_tcp_writer = None

        # Messages that have been sent to the device and are waiting for a response
        self._pending_incoming_messages = collections.deque()  # of Future objects

    # Process a request sent to this device, either from the HTTP server of from another embedded device
    async def process_incoming_request(self, request_dict):
        logging.debug('Forwarding message to {!a} over TCP connection: {}'.format(self.device_name, request_dict))
        if self._current_tcp_writer:
            future = asyncio.get_event_loop().create_future()
            self._pending_incoming_messages.append(future)
            self._current_tcp_writer.write(json.dumps(request_dict).encode('ascii') + b'\n')
            return await future
        else:
            raise RuntimeError('Embedded connection unavailable')

    # Start the HTTP server that can be used by external devices to send messages
    async def start_http_server(self):
        logging.info('Starting HTTP server for device {!a} on port {}'.format(self.device_name, self.local_port))
        return await asyncio.start_server(self._raw_http_handler, port=self.local_port)

    # Called when a connection is received from the embedded device
    async def accept_tcp_connection(self, reader, writer):
        logging.info('TCP connection established with device {!a} at {}'.format(self.device_name, writer.get_extra_info('peername')))

        # Replace previous connection, if any. This is useful if the device has
        # been reset without having the chance to close the previous connection
        if self._current_tcp_writer is not None:
            logging.warning('The newly-established TCP connection {} to device {!a} replaces the existing one at {}'.format(
                writer.get_extra_info('peername'), self.device_name, self._current_tcp_writer.get_extra_info('peername')))
            self._kill_current_tcp_connection()
        self._current_tcp_writer = writer

        exception_occurred = None
        try:
            # This is the main loop that services TCP connections from embedded devices
            while True:
                incoming_line = await reader.readline()
                if incoming_line.endswith(b'\n'):
                    incoming_line = incoming_line.strip().decode('ascii')
                else:  # connection lost/closed
                    break

                logging.debug('Received data from device {!a} over TCP connection: {}'.format(self.device_name, incoming_line))

                incoming_dict = json.loads(incoming_line)
                if not isinstance(incoming_dict, dict):
                    raise RuntimeError('Invalid data received:' + incoming_line)

                # If the dict contains a "result" field, assume it is the outcome
                # of a previously-issued request. Otherwise we process it as an
                # outgoing message
                if 'result' in incoming_dict:
                    self._pending_incoming_messages.popleft().set_result(incoming_dict)
                else:
                    incoming_dict['net-port'] = self.local_port

                    try:
                        response = await dispatch_message(incoming_dict, self)
                        logging.debug('Sending data to device {!a} over TCP connection: {}'.format(self.device_name, response))
                    except Exception as e:
                        response = { 'result': 'err', 'reason': str(e) }
                        logging.error('Sending error reply to device {!a} over TCP connection: {}'.format(self.device_name, response), exc_info=e)

                    writer.write(json.dumps(response).encode('ascii') + b'\n')
        except Exception as e:
            exception_occurred = e
        finally:
            # If this connection was not killed in the meantime, kill it now
            if self._current_tcp_writer == writer:
                self._kill_current_tcp_connection()
            logging.info('TCP connection closed with device {!a} at {}'.format(self.device_name, writer.get_extra_info('peername')), exc_info=exception_occurred)

    # Raw connection handler on HTTP port
    async def _raw_http_handler(self, reader, writer):
        logging.info('Got HTTP connection to {!a} from {}'.format(self.device_name, writer.get_extra_info('peername')))

        try:
            from_address = writer.get_extra_info('peername')[0]

            request_line = await reader.readuntil(b'\n')
            request_verb, request_uri, request_version = request_line.strip().split(b' ')
            if request_verb != b'POST' or request_uri != b'/':
                raise RuntimeError('Invalid request')

            headers = {} # str -> str
            content_length = -1  # default: until EOF
            while True:
                request_header_line = await reader.readuntil(b'\n')
                stripped_request_header_line = request_header_line.strip()
                if len(stripped_request_header_line) == 0:
                    break  # end of headers
                else:
                    field_name, value = stripped_request_header_line.split(b':', 1)
                    if field_name.decode('ascii').lower() == 'content-length':
                        content_length = int(value)

            request_contents = (await reader.read(content_length)).strip().decode('ascii')
            logging.debug('Received data on behalf of device {!a} over HTTP connection: {}'.format(self.device_name, request_contents))

            request_dict = json.loads(request_contents)
            if not isinstance(request_dict, dict):
                raise RuntimeError('Invalid request')

            request_dict['from-address'] = from_address
            response = await self.process_incoming_request(request_dict)
            logging.debug('Forwarding response of device {!a} over HTTP connection: {}'.format(self.device_name, response))
        except Exception as e:
            response = { 'result': 'err', 'reason': str(e) }
            logging.error('Sending error reply on behalf of device {!a} over HTTP connection: {}'.format(self.device_name, response), exc_info=e)
        finally:
            response_data = b'HTTP/1.0 200 OK\r\nServer: PHIDIAS Embedded Gateway\r\nContent-Type: application/json\r\n\r\n' + json.dumps(response).encode('ascii')
            writer.write(response_data)
            writer.close()

    # Close the current TCP connection to the embedded device and fail all pending requests
    def _kill_current_tcp_connection(self):
        self._current_tcp_writer.close()
        self._current_tcp_writer = None

        # Fail all pending delivery tasks
        while self._pending_incoming_messages:
            self._pending_incoming_messages.popleft().set_exception(RuntimeError('Embedded connection lost'))


parser = argparse.ArgumentParser(description='PHIDIAS Embedded Gateway')
parser.add_argument('-a', '--gateway-address', type=ipaddress.IPv4Address, help="gateway's well-known IP address (i.e. this computer's local address)", required=True)
parser.add_argument('-p', '--tcp-port', type=port_number, help='port to listen for TCP connections from embedded devices', default=9999)
parser.add_argument('device', metavar='DEVICE_NAME:DEVICE_PORT', type=EmbeddedDevice, help='register embedded device (format: name and well-known TCP port to listen on, separated by a colon); can be repeated one or more times', nargs='+')
args = parser.parse_args()

# Create index of devices by name and port
DEVICES = args.device
GATEWAY_ADDRESS = str(args.gateway_address)
TCP_PORT = args.tcp_port
DEVICES_BY_NAME = {d.device_name: d for d in DEVICES}
DEVICES_BY_PORT = {'{}:{}'.format(GATEWAY_ADDRESS, d.local_port): d for d in DEVICES}


async def dispatch_message(request_dict, sender_device):
    target_key = '{}:{}'.format(request_dict.pop('to-address'), request_dict.pop('to-port'))
    target_device = DEVICES_BY_PORT.get(target_key)

    if target_device is None:  # Not one of our embedded devices, use HTTP client method
        target_url = 'http://{}/'.format(target_key)
        logging.debug('Sending request from device {!a} to {}: {}'.format(sender_device.device_name, target_url, request_dict))

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(target_url, json=request_dict) as resp:
                    response = await resp.json()
                    logging.debug('HTTP response for device {!a} received from {}: {}'.format(sender_device.device_name, target_url, response))
        except aiohttp.ClientError as e:
            response = { 'result': 'err', 'reason': str(e) }
            logging.error('Sending error reply to device {!a} because of HTTP error at {}: {}'.format(sender_device.device_name, target_url, response), exc_info=e)
        return response
    else:
        request_dict['from-address'] = GATEWAY_ADDRESS
        logging.debug('Forwarding request from device {!a} to device {!a}: {}'.format(sender_device.device_name, target_device.device_name, request_dict))

        return await target_device.process_incoming_request(request_dict)


async def _embedded_conn_handler(reader, writer):
    logging.info('Accepted TCP connection from {}'.format(writer.get_extra_info('peername')))

    device_name = (await reader.readline()).strip().decode('ascii')
    device = DEVICES_BY_NAME.get(device_name, None)

    if device is None:
        logging.error('Failed to identify device {!a} connecting from {}'.format(device_name, writer.get_extra_info('peername')))
        writer.close()
    else:
        return await device.accept_tcp_connection(reader, writer)


loop = asyncio.get_event_loop()
logging.info('Starting TCP server for embedded connections on port {}'.format(TCP_PORT))
loop.create_task(asyncio.start_server(_embedded_conn_handler, port=TCP_PORT))
for d in DEVICES:
    loop.create_task(d.start_http_server())
loop.run_forever()
