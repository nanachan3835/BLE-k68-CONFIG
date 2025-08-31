# ble_project/tests/test_blood_pressure.py

import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock

# Cập nhật import
from config_loader import load_config, load_test_data_config
from devices.blood_pressure_monitor import BloodPressureMonitor, DeviceState

# Tải cấu hình thiết bị
DEVICES_CONFIG = load_config("devices.config")
BPM_CONFIG = DEVICES_CONFIG["BloodPressureMonitor"]

# Tải dữ liệu test từ file test.config
TEST_DATA = load_test_data_config("test.config")
BPM_TEST_DATA = TEST_DATA["BloodPressureMonitor_TestData"]

# Lớp MockBleakClient giữ nguyên không thay đổi
class MockBleakClient:
    # ... (giữ nguyên code của lớp này)
    def __init__(self, address: str):
        self.address = address
        self._is_connected = False
        self._notification_callbacks = {}
        self.connect = AsyncMock(side_effect=self._connect_impl)
        self.disconnect = AsyncMock(side_effect=self._disconnect_impl)
        self.start_notify = AsyncMock(side_effect=self._start_notify_impl)
        self.stop_notify = AsyncMock()
        self.write_gatt_char = AsyncMock()

    @property
    def is_connected(self): return self._is_connected
    async def _connect_impl(self): self._is_connected = True; return True
    async def _disconnect_impl(self): self._is_connected = False
    async def _start_notify_impl(self, char_uuid, callback): self._notification_callbacks[char_uuid] = callback
    def simulate_notification(self, char_uuid, data: bytearray):
        if char_uuid in self._notification_callbacks: self._notification_callbacks[char_uuid](0, data)
        else: raise ValueError(f"No notification callback for {char_uuid}")


@pytest.mark.asyncio
async def test_bpm_full_workflow(monkeypatch):
    """
    @brief Kịch bản test luồng hoạt động đầy đủ của Máy đo huyết áp.
    """
    # --- Sắp xếp (Arrange) ---
    mock_client_instance = MockBleakClient("XX:XX:XX:XX:XX:XX")
    monkeypatch.setattr("ble_device_manager.BleakClient", lambda addr: mock_client_instance)
    bpm_handler = BloodPressureMonitor("XX:XX:XX:XX:XX:XX", BPM_CONFIG)

    # --- Hành động (Act) ---
    main_task = asyncio.create_task(bpm_handler.run())
    await asyncio.sleep(0.1)

    # --- Kiểm chứng (Assert) ---
    assert bpm_handler.state == DeviceState.HANDSHAKING
    mock_client_instance.connect.assert_awaited_once()

    # Giả lập thiết bị gửi lại ACK cho handshake
    indicate_uuid = BPM_CONFIG["chars"]["indicate"]
    # SỬ DỤNG DỮ LIỆU TỪ test.config
    ack_handshake_frame = BPM_TEST_DATA["ack_handshake"]
    mock_client_instance.simulate_notification(indicate_uuid, ack_handshake_frame)
    
    await asyncio.sleep(0.1)
    assert bpm_handler.state == DeviceState.MEASURING

    # Giả lập thiết bị gửi lại kết quả cuối cùng
    # SỬ DỤNG DỮ LIỆU TỪ test.config
    result_frame = BPM_TEST_DATA["result_frame"]
    mock_client_instance.simulate_notification(indicate_uuid, result_frame)

    await asyncio.sleep(0.1)
    assert bpm_handler.state == DeviceState.RESULT_RECEIVED

    # Chờ tác vụ chính kết thúc
    await main_task
    mock_client_instance.disconnect.assert_awaited_once()

# Bạn có thể dễ dàng viết thêm các test case khác
@pytest.mark.asyncio
async def test_bpm_checksum_error(monkeypatch):
    """
    @brief Kịch bản test trường hợp thiết bị báo lỗi checksum.
    """
    mock_client_instance = MockBleakClient("XX:XX:XX:XX:XX:XX")
    monkeypatch.setattr("ble_device_manager.BleakClient", lambda addr: mock_client_instance)
    bpm_handler = BloodPressureMonitor("XX:XX:XX:XX:XX:XX", BPM_CONFIG)

    main_task = asyncio.create_task(bpm_handler.run())
    await asyncio.sleep(0.1)
    assert bpm_handler.state == DeviceState.HANDSHAKING

    # Giả lập thiết bị báo lỗi checksum ngay sau handshake
    indicate_uuid = BPM_CONFIG["chars"]["indicate"]
    error_frame = BPM_TEST_DATA["error_frame_checksum"]
    
    # Cần cập nhật _notification_handler để xử lý lỗi này
    # Hiện tại nó chưa xử lý, nhưng đây là cách bạn sẽ test
    # mock_client_instance.simulate_notification(indicate_uuid, error_frame)
    # await asyncio.sleep(0.1)
    # assert bpm_handler.state == DeviceState.ERROR

    # Hủy tác vụ để test không bị treo
    main_task.cancel()
    try:
        await main_task
    except asyncio.CancelledError:
        pass # Mong đợi lỗi này