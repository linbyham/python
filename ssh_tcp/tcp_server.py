# -*- coding: utf-8 -*-

import socketserver
import threading
import logging
import struct
import time

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s - %(funcName)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filemode='w')

PACKET_START = b'\xff\xff'
PACKET_END   = b'\xee\xee'

def _on_connect_dummy(client):
    LOG.info("{} connect".format(client.client_addr))

def _on_disconnect_dummy(client):
    LOG.info("{} disconnect".format(client.client_addr))

on_connect = _on_connect_dummy
on_disconnect = _on_disconnect_dummy

def add_on_connet(handler=_on_connect_dummy ):
    global on_connect
    on_connect = handler

def add_on_disconnet(handler=_on_disconnect_dummy ):
    global on_disconnect
    on_disconnect = handler

def _cmd_handler(client, cmd):
    LOG.info("{} recv cmd: {}".format(client.client_addr, cmd))

class TcpClient(threading.Thread):
    """
    client info
    """
    def __init__(self, socket, client_addr):
        threading.Thread.__init__(self)
        self.socket = socket
        self.recv_buf = ''
        self.recv_bytes = bytes()
        self.send_bytes = bytes()
        self.client_addr = client_addr
        self.encoding = "utf-8"
        self.cmd_list = []
        self.bytes_sent = 0
        self.sent = 0
        self.active = True
        self.cmd_hook = _cmd_handler
        self.start()

    def add_client_cmd_hander(self, cmd_handler):
        self.cmd_hook = cmd_handler

    def send(self, data):
        if data:
            packet_header = struct.pack('>HHHH', 0xffff, 0x0001, len(data), 0)
            packet_tailer = struct.pack('>HH', 0, 0xeeee)
            packet = packet_header + str(data).encode() + packet_tailer
            self.send_bytes += packet
            LOG.info("send bytes {}".format(self.send_bytes))

    def run(self):
        LOG.debug("client {} data handle task start.".format(self.client_addr))
        while self.active == True:
            self._cmd_handler()
            self._socket_send()
            time.sleep(0.3)
        LOG.debug("client {} data handle task start exit.".format(self.client_addr))

    def data_bytes_handle(self, packet_bytes):
        self.recv_bytes += packet_bytes
        p_start = self.recv_bytes.find(PACKET_START)
        p_end   = self.recv_bytes.find(PACKET_END)
        if p_start != -1 and p_end != -1:
            packet_header = struct.unpack('>HHHH', self.recv_bytes[p_start:p_start+8])
            #print(packet_header)
            self.recv_buf = self.recv_bytes[p_start+8:p_end-2].decode()
            self.cmd_list.append(self.recv_buf)
            self.recv_bytes = self.recv_bytes[p_end+2:]

    def _cmd_handler(self):
        if len(self.cmd_list) != 0:
            cmd = self.cmd_list.pop(0)
            if self.cmd_hook != None:
                self.cmd_hook(self, cmd)

    def _socket_send(self):
        if len(self.send_bytes):
            try:
                self.sent = self.socket.send(self.send_bytes)
            except Exception as err:
                LOG.error("SEND error '{}' from {}".format(
                    err, self.client_addr))
                self.active = False
                return
            self.bytes_sent += self.sent
            self.send_bytes = self.send_bytes[self.sent:]

    def close(self):
        self.active = False
        self.socket.close()

class TcpPacketHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        try:
            while True:
                self.data = self.request.recv(2048).strip()
                LOG.debug("{} send: {}".format(self.client_address, str(self.data)))
                if not self.data:
                    LOG.warning("connection lost")
                    break
                self.client.data_bytes_handle(self.data)
                #self.request.sendall(self.data.upper())
        except Exception as e:
            LOG.error('str(Exception):\t', str(e))
            LOG.error(self.client_address,"连接断开")
        finally:
            self.client.close()
            self.client.join()

    def setup(self):
        LOG.info("before handle,连接建立：{}".format(self.client_address))
        self.client = TcpClient(self.request, self.client_address)
        if on_connect:
            on_connect(self.client)

    def finish(self):
        LOG.debug("finish run  after handle")
        if on_disconnect:
            on_disconnect(self.client)

class TcpServer(object):
    """
    tcp server class
    """
    def __init__(self,
                 address='0.0.0.0',
                 port=6000):
        self.server = socketserver.TCPServer((address, port), TcpPacketHandler)

    def run(self):
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        self.server.serve_forever()

if __name__ == '__main__':
    LOG.info("tcp server start")
    tcp_server = TcpServer()
    tcp_server.run()
    LOG.info("tcp server exit")
