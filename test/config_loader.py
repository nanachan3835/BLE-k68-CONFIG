# ble_project/config_loader.py

"""
@file config_loader.py
@brief Module chịu trách nhiệm đọc và phân tích cú pháp các tệp cấu hình.
"""

import configparser
import logging
from pathlib import Path

log = logging.getLogger(__name__)

def load_config(config_path: str = "devices.config") -> dict:
    """
    @brief Đọc tệp cấu hình thiết bị và chuyển đổi thành dictionary.
    
    Hàm này được tối ưu để đọc cấu hình thiết bị, xử lý các khóa lồng nhau
    và chuyển đổi các giá trị trong section [commands] thành bytearray.
    
    @param config_path: Đường dẫn đến tệp .config.
    @return: Một dictionary chứa cấu hình của tất cả các thiết bị.
    """
    # ... (giữ nguyên code của hàm này)
    parser = configparser.ConfigParser()
    config_file = Path(config_path)

    if not config_file.exists():
        log.error(f"Tệp cấu hình '{config_path}' không tồn tại.")
        return {}

    parser.read(config_file)
    
    devices_config = {}
    for section in parser.sections():
        devices_config[section] = {}
        for key, value in parser.items(section):
            if '.' in key:
                main_key, sub_key = key.split('.', 1)
                if main_key not in devices_config[section]:
                    devices_config[section][main_key] = {}
                
                if main_key == "commands":
                    devices_config[section][main_key][sub_key] = bytearray.fromhex(value)
                else:
                    devices_config[section][main_key][sub_key] = value
            else:
                devices_config[section][key] = value

    log.info(f"Đã tải thành công cấu hình cho {len(devices_config)} thiết bị từ '{config_path}'.")
    return devices_config


def load_test_data_config(config_path: str) -> dict:
    """
    @brief Đọc tệp cấu hình dữ liệu test.
    
    Hàm này giả định tất cả các giá trị trong tệp là các chuỗi hex
    và chuyển đổi chúng thành bytearray.
    
    @param config_path: Đường dẫn đến tệp test.config.
    @return: Một dictionary chứa dữ liệu test.
    """
    parser = configparser.ConfigParser()
    config_file = Path(config_path)

    if not config_file.exists():
        log.error(f"Tệp cấu hình test '{config_path}' không tồn tại.")
        return {}
    
    parser.read(config_file)

    test_data = {}
    for section in parser.sections():
        test_data[section] = {}
        for key, value in parser.items(section):
            try:
                test_data[section][key] = bytearray.fromhex(value)
            except ValueError:
                log.warning(f"Giá trị '{value}' cho khóa '{key}' trong section '{section}' không phải là chuỗi hex hợp lệ. Bỏ qua.")

    log.info(f"Đã tải thành công dữ liệu test từ '{config_path}'.")
    return test_data