# -*- coding: utf-8 -*-

import ssh_client
import remote_cmd
import time
import logging
import dev_env
import protocol
import json_cmd
import datetime
from config import *

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s - %(funcName)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filemode='w')

logging.getLogger('paramiko').setLevel(logging.ERROR)
logging.getLogger('remote_cmd').setLevel(logging.ERROR)
logging.getLogger('protocol').setLevel(logging.ERROR)
logging.getLogger('tcp_server').setLevel(logging.ERROR)

class TestCase(object):
    """
    test case
    """
    def __init__(self, cmd_ctrl, protocol):
        self.cmd_ctrl = cmd_ctrl
        self.result_header = "test result"
        self.protocol = protocol

    def _case_seprate(self):
        LOG.info("\n---------------------------------------------------------")

    def _case_sample(self):
        try:
            test_result = True
        except Exception as e:
            test_result = False
        finally:
            if test_result == False:
                LOG.error("- {}: - {}".format(self.result_header, "Fail"))
            else:
                LOG.info("- {}: - {}".format(self.result_header, "Pass"))

    def _get_pid_dict(self):
        app_cfg_json = self.cmd_ctrl.read_json(app_dir, app_cfg)
        if app_cfg_json == None:
            LOG.error("read json failed")
            raise Exception("read json failed")

        alg_cfg_json = self.cmd_ctrl.read_json(app_dir, alg_cfg)
        if alg_cfg_json == None:
            LOG.error("read json failed")
            raise Exception("read json failed")

        app_dict = {}
        stat = True
        for app_json in app_cfg_json["local_app"]:
            try:
                if app_json["start_flag"] == 1:
                    result = self.cmd_ctrl.get_pid(app_json["app_name"])
                    if result == -1:
                        stat = False
                        LOG.error("{} launch failed".format(app_json["app_name"]))
                    else:
                        app_dict[app_json["app_name"]] = result
            except Exception as e:
                continue

        for alg_json in alg_cfg_json["alg_config"]:
            try:
                result = self.cmd_ctrl.get_pid(alg_json["alg"]["main_exec_file"])
                if result == -1:
                    stat = False
                    LOG.error("{} launch failed".format(alg_json["alg"]["main_exec_file"]))
                else:
                    app_dict[alg_json["alg"]["main_exec_file"]] = result
            except Exception as e:
                continue

        if stat == False:
            raise Exception("get app pid dict error")

        return app_dict

    def app_stop(self):
        self._case_seprate()
        LOG.info("关闭已运行程序")
        try:
            LOG.info("kill {}".format(app_name))
            self.cmd_ctrl.kill_proc(app_name, sudo=sudo_en)
            time.sleep(6)
            LOG.info("kill {}".format(debug_app_name))
            self.cmd_ctrl.kill_proc(debug_app_name, kill_flag="-9", sudo=sudo_en)

            app_cfg_json = self.cmd_ctrl.read_json(app_dir, app_cfg)
            if app_cfg_json == None:
                LOG.info("read json failed")
                raise Exception("read json failed")

            alg_cfg_json = self.cmd_ctrl.read_json(app_dir, alg_cfg)
            if alg_cfg_json == None:
                LOG.info("read json failed")
                raise Exception("read json failed")

            for app_json in app_cfg_json["local_app"]:
                try:
                    LOG.debug("kill {}".format(app_json["app_name"]))
                    self.cmd_ctrl.kill_proc(app_json["app_name"], kill_flag="-9", sudo=sudo_en)
                except Exception as e:
                    continue

            for alg_json in alg_cfg_json["alg_config"]:
                try:
                    LOG.debug("kill {}".format(alg_json["alg"]["main_exec_file"]))
                    self.cmd_ctrl.kill_proc(alg_json["alg"]["main_exec_file"], kill_flag="-9", sudo=sudo_en)
                except Exception as e:
                    continue

        except Exception as e:
            LOG.error(str(e))
        LOG.info("app exit ok.")

    def _modify_server_addr(self):
        try:
            cmd = "cp " + app_dir + "/" + srv_cfg + " " + app_dir + "/" + "srv_cfg.json.bk"
            self.cmd_ctrl.easy_cmd(cmd)
            my_ip = dev_env.get_computer_ip()
            self.cmd_ctrl.modify_json_cfg(app_dir,
                                            "srv_cfg.json",
                                            cfg_key1="srv_info",
                                            cfg_key2="ip",
                                            cfg_data=my_ip)
        except Exception as e:
            LOG.error(str(e))

    def _recover_server_addr(self):
        cmd = "cp " + app_dir + "/" + "srv_cfg.json.bk" + " " + app_dir + "/" + srv_cfg
        self.cmd_ctrl.easy_cmd(cmd)

    def _clear_debug_file(self):
        pass
        #self.cmd_ctrl.easy_cmd("find /home/camera/app-lby/ -name camera_debug_* | xargs rm -rf")

    def prepare(self):
        self.app_stop()
        self._modify_server_addr()

    def recover(self):
        self.app_stop()
        self._recover_server_addr()

    def grep_erro(self):
        LOG.info("grep erro from log.")
        self.cmd_ctrl.grep_file("erro",
                                  app_dir,
                                  log_file)

    def download_logfile(self):
        dt = datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S')
        local_log_file = local_log_dir + "/" + "log_" + dt + ".txt"
        remote_log_file = app_dir + "/" + log_file
        self.cmd_ctrl.download_file(remote_log_file, local_log_file)
        LOG.info("download {} to {}".format(remote_log_file, local_log_dir))

    def case_server_protocol(self):
        self._case_seprate()
        LOG.info("测试服务器与设备间通信协议，包括设备注册上线、状态上报、算法、模型更新等")
        try:
            LOG.info("wait device connect...")
            time.sleep(8)
            test_result = True
            if self.protocol.connect == False:
                LOG.error("receive no connection from device")
                raise Exception("receive no connection from device")
            else:
                for client in self.protocol.client_list:
                    LOG.info("receive connection from device {}".format(client.client_addr))

            if self.protocol.dev_reg == False:
                LOG.error("receive no device register from device")
                raise Exception("receive no device register from device")
            else:
                LOG.info("receive device register from device {}".format(self.protocol.dev_list))

            if self.protocol.state_report == False:
                LOG.error("receive no device state report from device")
                raise Exception("receive no device state report from device")
            else:
                LOG.info("receive device state report from device {}".format(self.protocol.dev_list))

            alg_update_cmd = json_cmd.alg_update_json()
            LOG.info("send cmd alg_update")
            self.protocol.send_cmd(alg_update_cmd)

            model_update_cmd = json_cmd.model_update_json()
            LOG.info("send cmd mode_update")
            self.protocol.send_cmd(model_update_cmd)

            LOG.info("wait update alg and model cmd to execute...")
            time.sleep(10)

            res = self.cmd_ctrl.grep_file("HTTPGetFileThreadForAlgModel: httpagent HTTP download file ret = 0", app_dir, log_file)
            if res == True:
                LOG.info("update alg and model success")
            else:
                LOG.error("update alg and model failed")
                test_result = False

        except Exception as e:
            test_result = False
        finally:
            if test_result == False:
                LOG.error("- {}: - {}".format(self.result_header, "Fail"))
            else:
                LOG.info("- {}: - {}".format(self.result_header, "Pass"))

    def case_app_launch(self):
        self._case_seprate()
        LOG.info("测试程序能否按启动配置正常启动")
        try:
            test_result = True
            LOG.info("start launch {}".format(app_name))
            result = self.cmd_ctrl.start_proc_nohub(app_dir, app_name, sudo=sudo_en, log_file=log_file)
            if result[0] == False:
                LOG.error("start proc {} failed".format(app_name))
                test_result = False
                raise Exception("proc start failed.")

            app_cfg_json = self.cmd_ctrl.read_json(app_dir, app_cfg)
            if app_cfg_json == None:
                LOG.error("read json failed")
                test_result = False
                raise Exception("read json failed")

            alg_cfg_json = self.cmd_ctrl.read_json(app_dir, alg_cfg)
            if alg_cfg_json == None:
                LOG.error("read json failed")
                test_result = False
                raise Exception("read json failed")

            LOG.info("wait 5s for start....")
            time.sleep(5)

            for app_json in app_cfg_json["local_app"]:
                try:
                    if app_json["start_flag"] == 1:
                        result = self.cmd_ctrl.check_proc_is_exist(app_json["app_name"])
                        if result == False:
                            test_result = False
                            LOG.error("{} launch failed".format(app_json["app_name"]))
                        else:
                            LOG.info("{} launch success".format(app_json["app_name"]))
                except Exception as e:
                    continue

            for alg_json in alg_cfg_json["alg_config"]:
                try:
                    result = self.cmd_ctrl.check_proc_is_exist(alg_json["alg"]["main_exec_file"])
                    if result == False:
                        test_result = False
                        LOG.error("{} launch failed".format(alg_json["alg"]["main_exec_file"]))
                    else:
                        LOG.info("{} launch success".format(alg_json["alg"]["main_exec_file"]))
                except Exception as e:
                    continue

        except Exception as e:
            test_result = False
            LOG.error(str(e))
        finally:
            if test_result == False:
                LOG.error("- {}: - {}".format(self.result_header, "Fail"))
            else:
                LOG.info("- {}: - {}".format(self.result_header, "Pass"))
            #self.cmd_ctrl.kill_proc(app_name, sudo=sudo_en)

    def case_app_stable(self):
        self._case_seprate()
        LOG.info("测试应用程序是否异常重启")
        try:
            test_result = True
            app_dict_orignal = self._get_pid_dict()
            LOG.info(app_dict_orignal)

            test_times = 0
            LOG.info("wait 30s for app proc id check...")
            while test_times < 30:
                app_dict = self._get_pid_dict()
                if app_dict != app_dict_orignal:
                    for key in app_dict_orignal.keys():
                        if app_dict_orignal[key] != app_dict[key]:
                            LOG.error("proc {} pid change from {} to {}"
                                      .format(key, app_dict_orignal[key], app_dict[key]))
                    raise Exception("app maybe restart")
                LOG.debug("app pid stay no change {} times".format(test_times))
                test_times += 1
                time.sleep(1)

        except Exception as e:
            test_result = False
            LOG.error(str(e))
        finally:
            if test_result == False:
                LOG.error("- {}: - {}".format(self.result_header, "Fail"))
            else:
                LOG.info("- {}: - {}".format(self.result_header, "Pass"))

    def case_app_revive(self):
        self._case_seprate()
        LOG.info("测试应用程序异常退出能否重启被管理进程启动")
        try:
            test_result = True
            app_dict = self._get_pid_dict()
            LOG.info(app_dict)

            i = 0
            kill_app_list = []
            for key in app_dict.keys():
                i += 1
                if (i == 2 or i == 5 or i == 7):
                    self.cmd_ctrl.kill_proc(proc_name=key, kill_flag="-9", sudo=sudo_en)
                    LOG.info("kill {}".format(key))
                    kill_app_list.append(key)

            time.sleep(3)
            for app in kill_app_list:
                result = self.cmd_ctrl.check_proc_is_exist(app)
                if result == False:
                    LOG.error("app {} did not restart".format(app))
                    test_result = False

            app_dict = self._get_pid_dict()
            LOG.info(app_dict)

        except Exception as e:
            test_result = False
            LOG.error(str(e))
        finally:
            if test_result == False:
                LOG.error("- {}: - {}".format(self.result_header, "Fail"))
            else:
                LOG.info("- {}: - {}".format(self.result_header, "Pass"))


def init_test_case():
    try:
        client = ssh_client.SshClient(hostname, username, password)
        cmd_ctrl = remote_cmd.CmdCtrl(cmd_sender=client.exec_cmd,
                                      multi_cmd_sender=client.exec_multi_cmd,
                                      file_uploader=client.upload,
                                      file_downloader=client.download)
        proto = protocol.Protocol()
        test_case = TestCase(cmd_ctrl, proto)
        return test_case,client

    except Exception as e:
        LOG.error(e)
        exit()

if __name__ == '__main__':

    #dev_env.env_prepare()

    test, client = init_test_case()
    try:
        test.prepare()
        test.case_app_launch()
        test.case_app_stable()
        test.case_app_revive()
        test.case_server_protocol()

    except Exception as e:
        LOG.error(e)
    finally:
        test.recover()
        test.download_logfile()
        test.grep_erro()
        client.close()

