# -*- coding: utf-8 -*-

import json
import logging
import datetime
from config import *

LOG = logging.getLogger(__name__)

def default_cmd_sender(cmd):
    print("default send: ", cmd)
    return "send success",""

def default_multi_cmd_sender(cmdlist):
    print("default send: ", cmdlist)
    return "send success",""

def default_file_uploader(src_file, dest_file):
    print("default upload : {} to {}".format(src_file, dest_file))
    return "send success",""

def default_file_downloader(src_file, dest_file):
    print("default download from : {} to {}".format(src_file, dest_file))
    return "send success",""

class CmdCtrl(object):
    """
    Cmd control
    """
    def __init__(self,
                 cmd_sender=default_cmd_sender,
                 multi_cmd_sender=default_multi_cmd_sender,
                 file_uploader=default_file_uploader,
                 file_downloader=default_file_downloader):
        self.cmd_sender = cmd_sender
        self.multi_cmd_sender = multi_cmd_sender
        self.file_uploader = file_uploader
        self.file_downloader = file_downloader
        self.cmd = ''
        self.cmd_list = []

    def easy_cmd(self, cmd, sudo=False):
        if sudo == False:
            self.cmd = str(cmd)
        else:
            self.cmd = "sudo " + str(cmd)

        LOG.info(self.cmd)
        result, erro = self.cmd_sender(self.cmd)
        if erro:
            LOG.info(erro)
            return (False, self.cmd, erro)
        else:
            LOG.info(result)
            return (True, self.cmd, result)

    def check_proc_is_exist(self, proc_name, sudo=False):
        self.cmd = "ps -ef | grep " + str(proc_name) + " | grep -v grep"
        result, erro = self.cmd_sender(self.cmd)
        if erro:
            LOG.debug(erro)
            return False
        try:
            LOG.debug(result)
            proc_id = result.split()[1]
            return True
        except Exception as e:
            return False

    def get_pid(self, proc_name, sudo=False):
        self.cmd = "ps -ef | grep " + str(proc_name) + " | grep -v grep"
        result, erro = self.cmd_sender(self.cmd)
        if erro:
            LOG.debug(erro)
            return -1
        try:
            LOG.debug(result)
            proc_id = result.split()[1]
            return proc_id
        except Exception as e:
            return -1

    def kill_proc(self, proc_name, kill_flag="-2", sudo=False):
        self.cmd = "ps -ef | grep " + str(proc_name) + " | grep -v grep"
        result, erro = self.cmd_sender(self.cmd)
        if erro:
            LOG.error(erro)
            return (False, self.cmd, erro)

        if len(result) is 0:
            LOG.info("{} is not exist".format(proc_name))
            return (True, self.cmd, result)

        try:
            proc_id = result.split()[1]
            if sudo == False:
                self.cmd = "kill "+ str(kill_flag) + ' ' + proc_id
            else:
                self.cmd = "sudo kill "+ str(kill_flag) + ' ' + proc_id

            LOG.info(self.cmd)
            result, erro = self.cmd_sender(self.cmd)
            if erro:
                LOG.error(erro)
                return (False, self.cmd, erro)
            else:
                LOG.info(result)
                return (True, self.cmd, result)
        except Exception as e:
            LOG.error(str(e))
            return (False, self.cmd, str(e))

    def start_proc_nohub(self, proc_dir, proc_name, sudo=False, log_file=None):
        self.cmd = "cd " + str(proc_dir) + ";pwd;" + "ls ./" + str(proc_name)
        result, erro = self.cmd_sender(self.cmd)
        if erro:
            return (False, self.cmd, erro)

        if sudo == False:
            if log_file == None:
                self.cmd_list = ["cd " + str(proc_dir),
                                 "nohup ./" + str(proc_name) + " > /dev/null&"]
                #self.cmd = "bash -lc 'cd " + str(proc_dir) + ";pwd;" + "nohup sudo ./" + str(proc_name) + " > /dev/null&'"
            else:
                self.cmd_list = ["cd " + str(proc_dir),
                                 "nohup ./" + str(proc_name) + " > "+ log_file +"&"]

            LOG.info(self.cmd_list)
            result, erro = self.multi_cmd_sender(self.cmd_list)
            if erro:
                LOG.info(erro)
                return (False, self.cmd_list, erro)
            else:
                LOG.info(result)
                return (True, self.cmd_list, result)
        else:
            if log_file == None:
                self.cmd_list = ["sudo -s",
                                 str(password),
                                 "cd " + str(proc_dir),
                                 "nohup ./" + str(proc_name) + " > /dev/null&"]
                #self.cmd = "bash -lc 'cd " + str(proc_dir) + ";pwd;" + "nohup sudo ./" + str(proc_name) + " > /dev/null&'"
            else:
                self.cmd_list = ["sudo -s",
                                 str(password),
                                 "cd " + str(proc_dir),
                                 "nohup ./" + str(proc_name) + " > " + log_file + "&"]
                #self.cmd = "bash -lc 'cd " + str(proc_dir) + ";pwd;" + "nohup sudo ./" + str(proc_name) + " > /dev/null&'"
            LOG.info(self.cmd_list)
            result, erro = self.multi_cmd_sender(self.cmd_list)
            if erro:
                LOG.info(erro)
                return (False, self.cmd_list, erro)
            else:
                LOG.info(result)
                return (True, self.cmd_list, result)

    def start_proc(self, proc_dir, proc_name, sudo=False):
        self.cmd = "cd " + str(proc_dir) + ";pwd;" + "ls ./" + str(proc_name)
        result, erro = self.cmd_sender(self.cmd)
        if erro:
            return (False, self.cmd, erro)

        if sudo == False:
            self.cmd = "bash -lc 'cd " + str(proc_dir) + ";pwd;" + "./" + str(proc_name) + "'"
        else:
            self.cmd = "bash -lc 'cd " + str(proc_dir) + ";pwd;" + "sudo ./" + str(proc_name) + "'"

        LOG.info(self.cmd)
        result, erro = self.cmd_sender(self.cmd)
        if erro:
            LOG.info(erro)
            return (False, self.cmd, erro)
        else:
            LOG.info(result)
            return (True, self.cmd, result)

    def grep_file(self, data, file_dir, file_name, sudo=False, write_file=True):
        self.cmd = "cd " + str(file_dir) + \
                   ";cat " +"./" + str(file_name) + "| grep " + "\""+ str(data) + "\""
        LOG.info(self.cmd)

        result, erro = self.cmd_sender(self.cmd)
        if erro:
            LOG.info(erro)
            LOG.error("grep {} from {}/{} failed.".format(str(data), file_dir, file_name))
            return False

        try:
            dt = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
            file_name = local_grep_dir + "/grep_" + dt + ".txt"
            if write_file == True:
                with open(file_name, "w+", encoding='utf-8') as f:
                    f.write("[grep {}]\n\n".format(data))
                    result = result.replace("\r\n","\n")
                    f.write(result)
                    f.close()
            else:
                print(result)

            res = result.find(data)
            LOG.info("find {} and return {}".format(data, res))
            if res < 0:
                return False
            else:
                return True
        except Exception as e:
            LOG.error(e)
            return False

    def read_file(self, file_dir, file_name, sudo=False):
        self.cmd = "cd " + str(file_dir) + ";cat " + "./" + str(file_name)
        LOG.info(self.cmd)

        result, erro = self.cmd_sender(self.cmd)
        if erro:
            LOG.info(erro)
            return (False, self.cmd, erro)
        else:
            #LOG.info(result)
            return (True, self.cmd, result)

    def upload_file(self, src_file, dest_file, sudo=False):
        self.file_uploader(src_file, dest_file)

    def download_file(self, src_file, dest_file, sudo=False):
        self.file_downloader(src_file, dest_file)

    def read_json(self, file_dir, file_name, sudo=False):
        result = self.read_file(file_dir, file_name)
        if result[0] == False:
            return None
        try:
            json_ob = json.loads(result[2])
            return json_ob
        except Exception as e:
            print(e)
            return None

    def modify_json_cfg(self,
                        cfg_dir,
                        cfg_file,
                        cfg_data,
                        cfg_key1,
                        cfg_key2=None,
                        sudo=False):
        result = self.read_file(cfg_dir, cfg_file)
        if result[0] == False:
            return result
        try:
            json_ob = json.loads(result[2])
            if cfg_key2 is None:
                json_ob[cfg_key1] = cfg_data
            else:
                json_ob[cfg_key1][cfg_key2] = cfg_data

            with open('./cfg.json', "w+", encoding='utf-8') as f:
                json.dump(json_ob, f, ensure_ascii=False, sort_keys=True, indent=4)
                f.close()

            dest_file = cfg_dir + "/" + cfg_file
            self.upload_file("./cfg.json", dest_file)
            self.cmd = "modify " + cfg_dir + "/" + cfg_file + " key :" + cfg_key1 + " " + cfg_key2
            return (True, self.cmd, "")
        except Exception as e:
            print(e)
            return (False, self.cmd, str(e))


if __name__ == '__main__':
    cmd_ctrl = CmdCtrl()
    cmd_ctrl.kill_proc("hahah")
    cmd_ctrl.easy_cmd("ls -l")
    cmd_ctrl.start_proc_nohub("/home/camera/app-lby", "rootmgt")
    cmd_ctrl.start_proc("/home/camera/app-lby", "rootmgt")
    cmd_ctrl.read_file("/home/camera/app-lby", "rootmgt")
    cmd_ctrl.modify_json_cfg("/home/camera/app-lby",
                             "srv_cfg.json",
                             "Jetson-Xavier323",
                             "terminal_model")
    cmd_ctrl.start_proc_nohub("/home/camera/app-lby", "rootmgt", True)
