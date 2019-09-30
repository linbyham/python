# -*- coding: utf-8 -*-

import json

sender = "server_test"
receiver = "device_2222"

def alg_update_json():
    json_data = {
        "command_type": "alg_update",
        "command_id": 123,
        "sender": sender,
        "receiver": receiver,
        "msg_body": {
            "alg": {
                "id": 2,
                "alg_desc": "混合车流量检测",
                "alg_file_name": "driver_alg.tar.gz",
                "update_time": "2019-04-10T17:08:00",
                "alg_file_url": "http://minio.pcl-ai.ml:9000/public-bucket/driver.tar.gz",
                "main_exec_file": "xxxxxx"
            }
        }
    }
    json_str = json.dumps(json_data)
    return json_str

def model_update_json():
    json_data = {
        "command_type": "model_update",
        "command_id": 123,
        "sender": sender,
        "receiver": receiver,
        "msg_body": {
            "alg_model": {
                "id": 1,
                "model_desc": "车辆检测pascal_voc预训练模型",
                "model_file_name": "driver_model.tar.gz",
                "version": "1.0",
                "add_time": "2019-04-10T17:03:00",
                "model_url": "http://minio.pcl-ai.ml:9000/public-bucket/driver.tar.gz",
                "update_type": 0,
                "compress_type": 0
                }
            }
        }
    json_str = json.dumps(json_data)
    return json_str