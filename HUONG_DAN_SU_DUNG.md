# HƯỚNG DẪN SỬ DỤNG TOOL TỰ ĐỘNG GÕ GOOGLE DOCS (MÔ PHỎNG NGƯỜI THẬT)

Tool hỗ trợ tự động gõ nội dung bài làm trực tiếp vào Google Docs với tốc độ, nhịp nghỉ và lỗi gõ sai ngẫu nhiên như người thật, giúp vượt qua kiểm tra **Lịch sử phiên bản (Version History)** và công cụ tua lại **Draftback**.

---

## 📦 Bộ file gồm có:
1. **`AutoTyper_Docs.exe`**: **File chạy trực tiếp (KHÔNG CẦN CÀI PYTHON)**, chỉ việc nhấp đúp là dùng ngay trên mọi máy tính Windows!
2. **`run_tool.bat`** & **`tool_human_typer.py`**: Bản chạy bằng mã nguồn Python (nếu máy có sẵn Python).
3. Các file bài giải mẫu `.md`:
   * `assignment_cau1_MLP_lien_tuc.md`: Câu 1 (MLP) gộp sẵn 1 mục gõ một lèo.
   * `assignment_cau2_RNN_lien_tuc.md`: Câu 2 (RNN) gộp sẵn 1 mục gõ một lèo.
   * `phan_A_den_A5.md`: Bài tập SGD Phần A gộp sẵn.
   * `phan_B_va_C_lien_tuc.md`: Bài tập SGD Phần B & C gộp sẵn.
4. **`HUONG_DAN_SU_DUNG.md`**: Bản hướng dẫn này.

---

## ⚙️ Yêu cầu trước khi chạy:
1. **Dùng file `.exe`:** Không cần cài đặt bất cứ phần mềm gì thêm!
2. **Chuyển bộ gõ Unikey / EVKey sang `[E]` (Tiếng Anh):**  
   * Bấm vào biểu tượng Unikey dưới góc phải thanh Taskbar để chuyển sang chữ **`[E]`**.
   * *(Tool đã tự động gửi mã Unicode tiếng Việt, nếu để `[V]` thì Unikey sẽ can thiệp làm nhảy chữ).*

---

## 🚀 Các bước thực hiện:

### Bước 1: Sửa lại thông tin cá nhân trong file bài giải
Mở file `.md` (bằng Notepad hoặc VS Code), sửa lại các dòng đầu tiên thành thông tin của chính bạn:
* Tên học phần: Học sâu
* Lớp môn học: [...]
* Họ và tên sinh viên: [...]
* Mã số sinh viên: [...]
* Link Google Docs của bạn: [Link Docs đã mở quyền Editor]

### Bước 2: Khởi động Tool
Nhấp đúp chuột vào file **`run_tool.bat`** để mở giao diện chương trình.

### Bước 3: Nạp bài và tinh chỉnh thông số
1. Bấm nút **"📁 Chọn file bài giải (.md / .txt)"** -> Chọn file bài giải bạn vừa lưu.
2. **Cá nhân hóa thông số (Tránh trùng nhau):**
   * **Tốc độ gõ (WPM):** Kéo trong khoảng **42 – 62 WPM** (mỗi người nên để một số khác nhau).
   * **Tỉ lệ gõ sai (Typo):** Kéo từ **1.5% đến 2.8%**.
3. **Tùy chọn nâng cao:**
   * **Tự động tách mốc Version History:** (Mặc định ĐÃ BẬT). Cứ sau mỗi đoạn (~70–95 từ), tool sẽ tự động nghỉ 60–80s để Google Docs chốt một mốc lịch sử riêng. Giúp lịch sử phiên bản của bạn hiển thị rải đều từng vài phút một lượng chữ vừa phải, cực kỳ tự nhiên.
   * **Chỉ gõ phần bài giải:** Tích chọn nếu trên Docs bạn đã có sẵn tiêu đề câu hỏi.

### Bước 4: Bắt đầu gõ
1. Chọn mục bạn muốn gõ trong danh sách bên trái.
2. Bấm nút **▶ BẮT ĐẦU GÕ MỤC ĐÃ CHỌN**.
3. Trong **5 giây đếm ngược**, chuyển nhanh sang tab Google Docs và click con trỏ chuột vào vị trí cần gõ.
4. Ngồi chờ máy tự động gõ. Khi xong, tool sẽ phát tiếng chuông báo hoàn thành.

> 🛑 **DỪNG KHẨN CẤP:** Nhấn phím **`ESC`** trên bàn phím bất kỳ lúc nào nếu bạn muốn tool dừng gõ ngay lập tức.

---

## ⚠️ LƯU Ý BẮT BUỘC SAU KHI GÕ XONG:
Sau khi tool đã gõ xong toàn bộ văn bản thô, hãy dành **2 – 3 phút tự tay chỉnh lại**:
1. **Bảng số liệu:** Xóa các dòng ký tự `|---|---|` thô đi, vào menu **Chèn > Bảng (Insert > Table)** và chép số vào bảng thật cho chuẩn form báo cáo.
2. **Tắt danh sách đánh số tự động:** Nếu Google Docs tự động thụt lề thành `1. 2. 3. ... 11.` ở Câu A5, hãy bôi đen và bấm tắt biểu tượng đánh số trên thanh công cụ Docs.
3. **In đậm tiêu đề:** Bôi đen các dòng `Câu A1`, `Câu A2`... và bấm `Ctrl + B`.
4. **Xuất PDF:** Xuất ra file PDF đúng tên `M03 - SGD_MLP_RNN_HoTen_MaSV.pdf` và nộp lên Classroom trước deadline.

## Update.md là file cập nhật khi agent code xong cập nhật vô

ví dụ: vx.x: cải thiện y.