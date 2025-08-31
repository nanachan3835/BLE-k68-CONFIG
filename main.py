# ble_project/main.py

"""
@file main.py
@brief Điểm khởi chạy chính của ứng dụng giao tiếp BLE.
"""

import asyncio
import logging
from bleak import BleakScanner
from config_loader import load_config, load_target_config
from ble_device_manager import DeviceFactory
import devices

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log = logging.getLogger(__name__)

async def scan_for_devices():
    """@brief Quét các thiết bị BLE xung quanh trong 5 giây."""
    log.info("Đang quét các thiết bị BLE...")
    found_devices = await BleakScanner.discover(timeout=5.0)
    print("\n--- CÁC THIẾT BỊ TÌM THẤY ---")
    for d in found_devices:
        print(f"  - Tên: {d.name}, Địa chỉ: {d.address}")
    print("----------------------------\n")

async def main():
    """@brief Hàm chính điều phối việc kết nối và chạy logic thiết bị."""

    # Tải cấu hình chi tiết của các loại thiết bị
    DEVICES_CONFIG = load_config("devices.config")
    if not DEVICES_CONFIG:
        log.error("Không thể tải cấu hình từ 'devices.config'. Chương trình kết thúc.")
        return

    # Tải cấu hình thiết bị mục tiêu
    target_info = load_target_config("target.config")
    if not target_info:
        log.error("Không thể tải cấu hình từ 'target.config'. Chương trình kết thúc.")
        return

    TARGET_DEVICE_TYPE = target_info['type']
    TARGET_ADDRESS = target_info['address']

    # Kiểm tra xem người dùng đã cấu hình địa chỉ chưa
    if TARGET_ADDRESS.upper() == "XX:XX:XX:XX:XX:XX":
        log.warning("Địa chỉ thiết bị chưa được cấu hình trong 'target.config'.")
        log.info("Chương trình sẽ thực hiện quét. Hãy sao chép địa chỉ và điền vào file 'target.config'.")
        await scan_for_devices()
        return

    # Lấy cấu hình cho thiết bị mục tiêu
    device_config = DEVICES_CONFIG.get(TARGET_DEVICE_TYPE)
    if not device_config:
        log.error(f"Không tìm thấy cấu hình cho loại thiết bị '{TARGET_DEVICE_TYPE}' trong 'devices.config'")
        return

    try:
        device_handler = DeviceFactory.create_device(TARGET_DEVICE_TYPE, TARGET_ADDRESS, device_config)
        await device_handler.run()
    except ValueError as e:
        log.error(e)
    except KeyboardInterrupt:
        log.info("Người dùng đã dừng chương trình.")
    except Exception as e:
        log.error(f"Một lỗi không mong muốn đã xảy ra: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    #asyncio.run(scan_for_devices())