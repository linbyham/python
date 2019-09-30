# -*- coding: utf-8 -*-

FPGA    = False
Nvidia  = True

assert not (FPGA == False and Nvidia == False)
assert not (FPGA == True and Nvidia == True)

if FPGA == True:
    hostname = "192.168.112.38"
    username = "root"
    password = "root"
    app_dir = "/home/camera/app-lby"
    sudo_en = False
    log_file = "debug.txt"

if Nvidia == True:
    hostname = "192.168.112.219"
    username = "nvidia"
    password = "nvidia"
    app_dir = "/home/camera/app"
    sudo_en = True
    log_file = "debug.txt"

app_name = "rootmgt"
debug_app_name = "debugout"
srv_cfg = "srv_cfg.json"
alg_cfg = "alg_cfg.json"
app_cfg = "local_app.json"

local_log_dir = "./log"
local_grep_dir = "./grep"
