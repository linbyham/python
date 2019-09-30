# -*- coding: utf-8 -*-

import paramiko
import time

class SshClient(object):
    """
    ssh client
    """
    def __init__(self, hostname, username, password, port=22):
        # 实例化SSHClient
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port     = port
        self.__transport = paramiko.Transport((self.hostname, self.port))
        self.__transport.connect(username=self.username, password=self.password)
        self.client = paramiko.SSHClient()
        # 自动添加策略，保存服务器的主机名和密钥信息，如果不添加，那么不再本地know_hosts文件中记录的主机将无法连接
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client._transport = self.__transport
        self.shell = None

    def close(self):
        self.__transport.close()

    def exec_cmd(self, cmd):
        if str(cmd).find("sudo") == -1:
            stdin, stdout, stderr = self.client.exec_command(cmd)  # stdout 为正确输出，stderr为错误输出，同时是有1个变量有值
        else:
            stdin, stdout, stderr = self.client.exec_command(cmd, get_pty=True)  # stdout 为正确输出，stderr为错误输出，同时是有1个变量有值
            stdin.write(self.password + '\n')  # 执行输入命令，输入sudo命令的密码，会自动执行

        exec_out = stdout.read().decode('utf-8').strip("\n")
        exec_err = stderr.read().decode('utf-8').strip("\n")
        return exec_out, exec_err

    def exec_multi_cmd(self, cmdlist):
        try:
            if self.shell is None:
                self.shell = self.client.invoke_shell()

            for cmd in cmdlist:
                #print("send cmd: {}".format(cmd))
                self.shell.send(cmd+"\n")
                time.sleep(0.5)
                recv_buf = self.shell.recv(1024)
                #print("get cmd return: {}".format(recv_buf.decode()))
            exec_out, exec_err = "excute cmdlist success",""
        except Exception as e:
            print(str(e))
            exec_out, exec_err = "","excute cmdlist fail."
        finally:
            if self.shell is not None:
                time.sleep(1)
                self.shell.close()
                self.shell = None
            return exec_out, exec_err

    def upload(self, src_file, dest_file):
        sftp = paramiko.SFTPClient.from_transport(self.__transport)
        #print("upload {} to {}".format(src_file, dest_file))
        sftp.put(src_file, dest_file)

    def download(self, src_file, dest_file):
        sftp = paramiko.SFTPClient.from_transport(self.__transport)
        #print("download from {} to {}".format(src_file, dest_file))
        sftp.get(src_file, dest_file)

if __name__ == '__main__':
    try:
        ssh_client = SshClient("192.168.112.52", "root", "root")
        result, erro = ssh_client.exec_cmd(
            "ps -ef | grep sftp-server | grep -v grep")

        print(result.split()[1])
        ssh_client.upload("./test.py", "test.py")
        ssh_client.download("/home/camera/app-lby/test.py", "./tst.py")
        ssh_client.close()
    except Exception as e:
        print(e)
