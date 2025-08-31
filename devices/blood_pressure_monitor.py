# ble_project/devices/blood_pressure_monitor.py

import asyncio
import logging
from enum import Enum, auto
from ble_device_manager import BLEDevice, DeviceFactory

log = logging.getLogger(__name__)

# Thêm Enum trạng thái để dễ kiểm tra
class DeviceState(Enum):
    IDLE = auto()
    CONNECTING = auto()
    CONNECTED = auto()
    HANDSHAKING = auto()
    MEASURING = auto()
    RESULT_RECEIVED = auto()
    ERROR = auto()

class BloodPressureMonitor(BLEDevice):
    def __init__(self, address: str, config: dict):
        super().__init__(address, config)
        self.state = DeviceState.IDLE # Khởi tạo trạng thái ban đầu

    async def run(self):
        self.state = DeviceState.CONNECTING
        if not await self.connect():
            self.state = DeviceState.ERROR
            return
        
        self.state = DeviceState.CONNECTED
        
        try:
            indicate_char_uuid = self.config["chars"]["indicate"]
            await self.client.start_notify(indicate_char_uuid, self._notification_handler)
            await self._start_measurement()

            # Trong môi trường test, chúng ta không cần vòng lặp vô hạn
            # Ở đây ta có thể đợi một sự kiện hoặc một trạng thái cuối cùng
            while self.state not in [DeviceState.RESULT_RECEIVED, DeviceState.ERROR]:
                 await asyncio.sleep(0.1) # Chờ một cách không chặn

        except Exception as e:
            log.error(f"Đã xảy ra lỗi trong quá trình chạy: {e}")
            self.state = DeviceState.ERROR
        finally:
            log.info(f"Kết thúc phiên làm việc với trạng thái: {self.state.name}")
            await self.disconnect()

    def _notification_handler(self, sender, data: bytearray):
        log.info(f"[BPM] Nhận được dữ liệu: {data.hex().upper()}")
        
        # Logic xử lý state machine đơn giản
        if self.state == DeviceState.HANDSHAKING and data == bytearray.fromhex("06"):
            log.info("Handshake thành công. Chuyển sang trạng thái đo.")
            self.state = DeviceState.MEASURING
        
        elif self.state == DeviceState.MEASURING and data.startswith(b'\xfc'):
            log.info("Nhận được kết quả cuối cùng.")
            self.state = DeviceState.RESULT_RECEIVED

    async def _start_measurement(self):
        write_char_uuid = self.config["chars"]["write"]
        handshake_cmd = self.config["commands"]["handshake"]
        log.info(f"Gửi lệnh Handshake {handshake_cmd.hex().upper()} tới {write_char_uuid}")
        self.state = DeviceState.HANDSHAKING
        await self.client.write_gatt_char(write_char_uuid, handshake_cmd)

DeviceFactory.register_device("BloodPressureMonitor", BloodPressureMonitor)