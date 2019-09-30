# -*- coding: utf-8 -*-

import tcp_server
import logging
import threading
import time
import json

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s - %(funcName)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filemode='w')

class Protocol(object):
    """
    protocol
    """
    def __init__(self):
        tcp_server.add_on_connet(self.client_on_connect)
        tcp_server.add_on_disconnet(self.client_on_disconnect)
        self.client_list = []
        self.dev_list = []
        self.dev_reg = False
        self.dev_logout = False
        self.state_report = False
        self.connect = True

        self.tcp_server = tcp_server.TcpServer()
        self.server_thread = threading.Thread(target=self.tcp_server.run)
        self.server_thread.daemon = True
        self.server_thread.start()

    def proto_handler(self, client, cmd):
        LOG.debug("{} recv cmd: {}".format(client.client_addr, cmd))
        try:
            cmd_json = json.loads(cmd)
            cmd_type = cmd_json["command_type"]
            if cmd_type == "dev_login":
                self.dev_reg = True
                dev = cmd_json["msg_body"]["device_uuid"]
                self.dev_list.append(dev)
            elif cmd_type == "state_report":
                self.state_report = True
            elif cmd_type == "dev_logout":
                self.dev_logout = True
                dev = cmd_json["msg_body"]["device_uuid"]
                self.dev_list.remove(dev)
        except Exception as e:
            LOG.error(e)

    def send_cmd(self, cmd):
        for client in self.client_list:
            LOG.info("send {} cmd {}".format(client.client_addr, cmd))
            client.send(cmd)

    def client_on_connect(self, client):
        LOG.info("{} connect".format(client.client_addr))
        client.add_client_cmd_hander(self.proto_handler)
        self.connect = True
        self.client_list.append(client)

    def client_on_disconnect(self, client):
        LOG.info("{} disconnect".format(client.client_addr))
        self.connect = False
        self.client_list.remove(client)

import json_cmd

if __name__ == '__main__':
    proto = Protocol()
    i = 0
    while True:
        print("sleep here")
        time.sleep(1)
        i+=1
        if i == 10:
            proto.send_cmd(json_cmd.alg_update_json())
