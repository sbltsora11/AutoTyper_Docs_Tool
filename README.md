# ⚡ AutoTyper Docs Tool (Giả Lập Gõ Google Docs Như Người Thật)

Tool hỗ trợ tự động gõ nội dung bài làm trực tiếp vào Google Docs với tốc độ, nhịp nghỉ và lỗi gõ sai (typo) ngẫu nhiên như người thật. Giúp bài làm hiển thị lịch sử phiên bản tự nhiên và vượt qua kiểm tra **Lịch sử phiên bản (Version History)** cũng như công cụ tua lại **Draftback**.

---

## 🌟 Tính Năng Nổi Bật

- **Gõ chuẩn Win32 Unicode SendInput**: Tương thích hoàn toàn với tiếng Việt, không bị lỗi nhảy chữ, lag chữ.
- **Tốc độ gõ tùy biến (WPM)**: Mô phỏng nhịp gõ 42 - 62 từ/phút linh hoạt theo từng người dùng.
- **Tỉ lệ gõ sai ngẫu nhiên (Typo Simulation)**: Tự động gõ nhầm ký tự liền kề trên bàn phím, dừng lại một nhịp và bấm `Backspace` để sửa như người thật thao tác.
- **Tự động ngắt mốc Version History**: Cứ sau khoảng 70 - 95 từ, tool tự động nghỉ 60 - 80 giây để Google Docs chốt một mốc lịch sử riêng biệt.
- **Phím tắt dừng khẩn cấp**: Bấm `ESC` bất kỳ lúc nào để dừng gõ ngay lập tức.
- **Không cần cài đặt Python**: Có sẵn file thực thi `AutoTyper_Docs.exe` chạy ngay trên Windows.

---

## 📦 Cấu Trúc Thư Mục

```text
AutoTyper_Docs_Tool/
├── AutoTyper_Docs.exe       # Bản đóng gói chạy trực tiếp (Windows)
├── tool_human_typer.py      # Mã nguồn Python (giao diện Tkinter + Win32 API)
├── run_tool.bat             # File khởi động nhanh mã nguồn Python
├── HUONG_DAN_SU_DUNG.md     # Hướng dẫn chi tiết từng bước bằng tiếng Việt
├── update.md                # Nhật ký cập nhật phiên bản
├── README.md                # Tài liệu giới thiệu dự án
└── .gitignore               # Cấu hình bỏ qua file rác
```

---

## 🚀 Hướng Dẫn Sử Dụng Nhanh

Xem chi tiết tại: [HUONG_DAN_SU_DUNG.md](HUONG_DAN_SU_DUNG.md)

1. **Khởi động**:
   - Cách 1: Nhấp đúp vào file `AutoTyper_Docs.exe`.
   - Cách 2: Chạy file `run_tool.bat` (yêu cầu máy có Python 3.x).
2. **Lưu ý bàn phím**: Chuyển Unikey / EVKey sang chế độ tiếng Anh **`[E]`** trước khi bấm bắt đầu.
3. **Thao tác**:
   - Chọn file nội dung bài (`.md` hoặc `.txt`).
   - Tinh chỉnh tốc độ WPM và tỉ lệ Typo.
   - Bấm **"▶ BẮT ĐẦU GÕ MỤC ĐÃ CHỌN"**.
   - Trong 5 giây đếm ngược, bấm chuột vào tài liệu Google Docs cần gõ.
   - Nhấn `ESC` nếu muốn dừng khẩn cấp.

## chỉ sử dụng github phụ cho repo này

---

## 🛠️ Công Nghệ Sử Dụng
- **Ngôn ngữ**: Python 3 (100% standard libraries: `tkinter`, `ctypes`, `threading`, `json`).
- **Nền tảng**: Windows 10 / 11.
