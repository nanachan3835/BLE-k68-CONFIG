# ble_project/config_loader.py

"""
@file config_loader.py
@brief Module chịu trách nhiệm đọc và phân tích cú pháp tệp cấu hình .config.
"""

import configparser
import logging
from pathlib import Path

log = logging.getLogger(__name__)

def load_config(config_path: str = "devices.config") -> dict:
    """
    @brief Đọc tệp cấu hình INI và chuyển đổi nó thành một dictionary lồng nhau.
    
    Hàm này sẽ phân tích các khóa có dấu chấm (ví dụ: 'chars.indicate')
    để tạo ra các dictionary con. Các giá trị trong section [commands]
    sẽ được chuyển đổi thành bytearray.
    
    @param config_path: Đường dẫn đến tệp .config.
    @return: Một dictionary chứa cấu hình của tất cả các thiết bị.
    """
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
            # Xử lý các khóa lồng nhau (nested keys)
            if '.' in key:
                main_key, sub_key = key.split('.', 1)
                if main_key not in devices_config[section]:
                    devices_config[section][main_key] = {}
                
                # Chuyển đổi các lệnh (commands) từ chuỗi hex sang bytearray
                if main_key == "commands":
                    devices_config[section][main_key][sub_key] = bytearray.fromhex(value)
                else:
                    devices_config[section][main_key][sub_key] = value
            else:
                # Các khóa không lồng nhau
                devices_config[section][key] = value

    log.info(f"Đã tải thành công cấu hình cho {len(devices_config)} thiết bị từ '{config_path}'.")
    return devices_config



def load_target_config(config_path: str = "target.config") -> dict | None:
    """
    @brief Đọc tệp cấu hình thiết bị mục tiêu.
    
    Tệp này chỉ định loại và địa chỉ của thiết bị cần kết nối.
    
    @param config_path: Đường dẫn đến tệp target.config.
    @return: Một dictionary chứa 'type' và 'address', hoặc None nếu có lỗi.
    """
    parser = configparser.ConfigParser()
    config_file = Path(config_path)

    if not config_file.exists():
        log.error(f"Tệp cấu hình mục tiêu '{config_path}' không tồn tại. Vui lòng tạo file này.")
        return None

    parser.read(config_file)

    if 'Target' not in parser:
        log.error(f"Section [Target] không được tìm thấy trong '{config_path}'.")
        return None

    target_section = parser['Target']
    target_type = target_section.get('type')
    target_address = target_section.get('address')

    if not target_type or not target_address:
        log.error("Cấu hình 'type' hoặc 'address' bị thiếu trong section [Target] của file cấu hình.")
        return None

    return {'type': target_type.strip(), 'address': target_address.strip()}