# ble_project/ble_device_manager.py

"""
@file ble_device_manager.py
@brief Định nghĩa lớp cơ sở cho thiết bị BLE và một Factory để tạo các thể hiện thiết bị.
"""

import logging
from abc import ABC, abstractmethod
from bleak import BleakClient
from bleak.exc import BleakError

log = logging.getLogger(__name__)

class DeviceFactory:
    """
    @class DeviceFactory
    @brief Lớp Factory sử dụng mẫu thiết kế Singleton để tạo các đối tượng thiết bị.
    
    Lớp này duy trì một "registry" (danh sách đăng ký) các lớp thiết bị có sẵn.
    """
    _creators = {}

    @classmethod
    def register_device(cls, device_type: str, creator):
        """
        @brief Đăng ký một loại thiết bị mới với Factory.
        @param device_type: Tên định danh cho loại thiết bị (ví dụ: "BloodPressureMonitor").
        @param creator: Lớp (class) của thiết bị cần đăng ký.
        """
        cls._creators[device_type] = creator

    @classmethod
    def create_device(cls, device_type: str, address: str, config: dict):
        """
        @brief Tạo một thể hiện (instance) của một thiết bị dựa trên loại của nó.
        @param device_type: Tên của loại thiết bị cần tạo.
        @param address: Địa chỉ MAC của thiết bị.
        @param config: Đối tượng cấu hình cho loại thiết bị này.
        @return: Một thể hiện của lớp thiết bị tương ứng, hoặc None nếu loại không tồn tại.
        """
        creator = cls._creators.get(device_type)
        if not creator:
            raise ValueError(f"Loại thiết bị '{device_type}' chưa được đăng ký.")
        return creator(address, config)


class BLEDevice(ABC):
    """
    @class BLEDevice
    @brief Lớp cơ sở trừu tượng cho tất cả các loại thiết bị BLE.
    
    Cung cấp các chức năng chung như kết nối, ngắt kết nối và giao diện
    cho các phương thức phải được triển khai bởi các lớp con.
    """
    def __init__(self, address: str, config: dict):
        """
        @brief Khởi tạo một đối tượng BLEDevice.
        @param address: Địa chỉ MAC của thiết bị vật lý.
        @param config: Một dictionary chứa cấu hình (UUIDs, commands) cho thiết bị.
        """
        self.address = address
        self.config = config
        self.client = BleakClient(address)
        self.is_connected = False

    async def connect(self) -> bool:
        """
        @brief Thiết lập kết nối BLE tới thiết bị.
        @return: True nếu kết nối thành công, False nếu ngược lại.
        """
        try:
            log.info(f"Đang cố gắng kết nối tới {self.address}...")
            await self.client.connect()
            self.is_connected = self.client.is_connected
            if self.is_connected:
                log.info(f"Đã kết nối thành công tới {self.address}")
            return self.is_connected
        except BleakError as e:
            log.error(f"Không thể kết nối tới {self.address}: {e}")
            self.is_connected = False
            return False

    async def disconnect(self):
        """@brief Ngắt kết nối khỏi thiết bị."""
        if self.client and self.is_connected:
            log.info(f"Đang ngắt kết nối khỏi {self.address}")
            await self.client.disconnect()
            self.is_connected = False

    @abstractmethod
    def _notification_handler(self, sender, data: bytearray):
        """
        @brief Xử lý callback khi nhận được dữ liệu từ thiết bị.
        
        Đây là một phương thức trừu tượng và phải được ghi đè ở lớp con.
        
        @param sender: Handle của characteristic gửi dữ liệu.
        @param data: Dữ liệu thô (raw data) dưới dạng bytearray.
        """
        pass

    @abstractmethod
    async def run(self):
        """
        @brief Bắt đầu luồng giao tiếp chính với thiết bị.
        
        Đây là một phương thức trừu tượng và phải được ghi đè ở lớp con.
        """
        pass