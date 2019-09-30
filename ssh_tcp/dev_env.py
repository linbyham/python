import ssh_client
import time
import os
import logging
from config import *
import socket

LOG = logging.getLogger(__name__)

def get_computer_ip():
    #获取本机电脑名
    myname = socket.getfqdn(socket.gethostname(  ))
    #获取本机ip
    myaddr = socket.gethostbyname(myname)
    return myaddr

def reboot_device():
    return 0
    client = ssh_client.SshClient(hostname, username, password)
    client.exec_cmd("sudo reboot now")
    time.sleep(1)
    client.close()

def ping_device():
    ping = "ping " + hostname
    result = os.system(ping)
    if result == 0:
        LOG.debug("ping {} success".format(hostname))
        return True
    else:
        LOG.debug("ping {} failed".format(hostname))
        return False

def env_prepare():
    LOG.info("reboot device start....")
    try:
        reboot_device()
    except Exception as e:
        LOG.error(str(e))
        exit()

    t = 0
    result = False
    while result == False:
        time.sleep(1)
        t += 1
        LOG.info("wait {} times for rebooting".format(t))
        result = ping_device()
        if t > 3:
            LOG.error("reboot device failed")
            exit()
    LOG.info("reboot device success..")