
---

# Giao Tiếp Thiết Bị Y Tế BLE

Dự án này là một ứng dụng Python được xây dựng để giao tiếp với các thiết bị y tế (như máy đo huyết áp, cân điện tử) thông qua Bluetooth Low Energy (BLE). Ứng dụng được thiết kế với kiến trúc linh hoạt, dễ mở rộng và được điều khiển hoàn toàn bằng các tệp cấu hình.

## ✨ Tính Năng Nổi Bật

*   **Điều khiển bằng Cấu hình:** Không cần hardcode địa chỉ MAC hay UUIDs. Mọi thứ được quản lý trong các tệp `.config`.
*   **Dễ Mở Rộng:** Thêm hỗ trợ cho một thiết bị mới chỉ đơn giản bằng cách tạo một class mới và thêm cấu hình, không cần sửa đổi mã nguồn lõi.
*   **Kiến trúc Rõ ràng:** Sử dụng các mẫu thiết kế (Design Patterns) như Factory để quản lý việc tạo đối tượng một cách hiệu quả.
*   **Hỗ trợ Kiểm thử:** Tích hợp sẵn bộ khung kiểm thử (testing framework) sử dụng `pytest` và Mocking để giả lập thiết bị, cho phép phát triển mà không cần phần cứng vật lý.
*   **Tách biệt Logic:** Mỗi thành phần (cấu hình, logic thiết bị, logic nghiệp vụ) được tách biệt trong các module riêng lẻ.

## 📂 Cấu Trúc Dự Án

```
ble_project/
├── .gitignore                # Bỏ qua các tệp không cần thiết
├── README.md                 # Tài liệu hướng dẫn này
├── requirements.txt          # Các thư viện cần thiết cho ứng dụng
├── requirements-dev.txt      # Các thư viện cần thiết cho phát triển và test
├── main.py                   # Điểm khởi chạy chính của ứng dụng
├── devices.config            # Cấu hình chi tiết (UUIDs, commands) cho các loại thiết bị
├── target.config.example     # Tệp mẫu để chỉ định thiết bị mục tiêu
├── config_loader.py          # Module đọc các tệp cấu hình
├── ble_device_manager.py     # Lớp cơ sở và Factory để tạo đối tượng thiết bị
├── devices/                  # Package chứa logic cho từng loại thiết bị cụ thể
│   ├── __init__.py
│   ├── blood_pressure_monitor.py
│   └── ...
└── tests/                    # Package chứa các bài kiểm thử
    ├── test.config
    └── test_blood_pressure.py
```

## 🚀 Hướng Dẫn Cài Đặt

### Yêu cầu tiên quyết
*   Python 3.8 trở lên
*   Git
*   Bluetooth 4.0+ trên máy tính

### Các bước cài đặt

1.  **Clone kho mã nguồn:**
    ```bash
    git clone <URL_REPOSITORY_CUA_BAN>
    cd ble_project
    ```

2.  **Tạo và kích hoạt môi trường ảo (Khuyến khích):**
    *   **Trên macOS/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   **Trên Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```

3.  **Tạo các tệp `requirements`:**
    Tạo hai tệp `requirements.txt` và `requirements-dev.txt` trong thư mục gốc với nội dung sau:

    *   `requirements.txt`:
        ```txt
        bleak
        ```
    *   `requirements-dev.txt`:
        ```txt
        pytest
        pytest-asyncio
        ```

4.  **Cài đặt các thư viện cần thiết:**
    ```bash
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```

## 🏃 Hướng Dẫn Sử Dụng

Ứng dụng này được thiết kế để không cần phải sửa đổi mã nguồn khi sử dụng. Mọi thao tác được thực hiện qua các tệp cấu hình.

### Bước 1: Chuẩn bị tệp Cấu hình Mục tiêu

File `target.config` cho ứng dụng biết cần kết nối tới thiết bị nào.

1.  Tạo một bản sao của `target.config.example` và đổi tên thành `target.config`.
    ```bash
    cp target.config.example target.config
    ```

2.  File `target.config` của bạn ban đầu sẽ trông như thế này:
    ```ini
    [Target]
    type = BloodPressureMonitor
    address = XX:XX:XX:XX:XX:XX
    ```

### Bước 2: Tìm Địa chỉ MAC của Thiết bị

1.  Bật nguồn thiết bị y tế của bạn và đặt nó gần máy tính.
2.  Chạy ứng dụng. Vì địa chỉ trong `target.config` chưa hợp lệ, chương trình sẽ tự động chuyển sang chế độ quét:
    ```bash
    python main.py
    ```
3.  Quan sát terminal, bạn sẽ thấy danh sách các thiết bị BLE được tìm thấy. Hãy tìm thiết bị của bạn và **sao chép địa chỉ MAC** của nó.
    ```
    --- CÁC THIẾT BỊ TÌM THẤY ---
      - Tên: My BPM Device, Địa chỉ: C0:98:76:54:32:10   <-- Sao chép địa chỉ này
    ----------------------------
    ```

### Bước 3: Cập nhật Cấu hình Mục tiêu

1.  Mở tệp `target.config` bằng trình soạn thảo văn bản.
2.  Chỉnh sửa các giá trị:
    *   `type`: Đặt tên loại thiết bị. Tên này phải khớp với một section trong `devices.config` (ví dụ: `BloodPressureMonitor`).
    *   `address`: Dán địa chỉ MAC bạn vừa sao chép vào đây.
3.  Lưu tệp lại. Ví dụ:
    ```ini
    [Target]
    type = BloodPressureMonitor
    address = C0:98:76:54:32:10
    ```

### Bước 4: Chạy Ứng dụng

Chạy lại lệnh ban đầu. Lần này, chương trình sẽ đọc cấu hình và tiến hành kết nối tới thiết bị của bạn.
```bash
python main.py
```
Theo dõi các thông báo log trên terminal để xem quá trình kết nối và nhận dữ liệu.

## 🛠️ Phát triển và Kiểm thử

Dự án có sẵn bộ khung kiểm thử để xác minh logic hoạt động mà không cần thiết bị vật lý.

1.  **Cấu hình dữ liệu test:** Mở tệp `tests/test.config` để xem hoặc chỉnh sửa các gói tin mẫu dùng để giả lập phản hồi từ thiết bị.
2.  **Chạy toàn bộ bài test:** Từ thư mục gốc của dự án, chạy lệnh:
    ```bash
    pytest
    ```

## 🧩 Hướng Dẫn Mở Rộng

Để thêm hỗ trợ cho một loại thiết bị mới (ví dụ: `BodyScale`):

1.  **Thêm Cấu hình:** Mở `devices.config` và thêm một section mới `[BodyScale]` với các UUIDs và commands tương ứng.
2.  **Tạo Lớp Logic:** Trong thư mục `devices/`, tạo một file mới `body_scale.py`. Bên trong, tạo lớp `BodyScale` kế thừa từ `BLEDevice` và triển khai các phương thức `run()` và `_notification_handler()`.
3.  **Đăng ký Thiết bị:** Mở file `devices/__init__.py` và thêm dòng `from . import body_scale` để thiết bị mới được tự động đăng ký với Factory.

