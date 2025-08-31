# ble_project/devices/__init__.py

"""
@file __init__.py
@brief Tự động import tất cả các module thiết bị trong package này
       để chúng có thể tự đăng ký với DeviceFactory.
"""
from . import blood_pressure_monitor
from . import weighing_scale

# Khi bạn thêm một thiết bị mới, ví dụ `body_scale.py`,
# hãy thêm dòng sau:
# from . import body_scale