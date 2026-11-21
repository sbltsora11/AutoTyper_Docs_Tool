"""
================================================================================
TOOL TỰ ĐỘNG GÕ GOOGLE DOCS GIẢ LẬP NGƯỜI THẬT (CHIA THEO HEADING)
Tác giả: Hỗ trợ sinh viên học phần Deep Learning (M03)
Không cần cài đặt thư viện ngoài (sử dụng 100% thư viện chuẩn của Python: tkinter + ctypes)
================================================================================
"""

import sys
import os
import re
import time
import json
import hashlib
import random
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import ctypes
from ctypes import wintypes

# ---------------------------------------------------------------------------
# CẤU HÌNH WIN32 SENDINPUT CHO BÀN PHÍM
# ---------------------------------------------------------------------------
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_BACK = 0x08
VK_RETURN = 0x0D
VK_TAB = 0x09
VK_ESCAPE = 0x1B

ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ('wVk', wintypes.WORD),
        ('wScan', wintypes.WORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ULONG_PTR)
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [('uMsg', wintypes.DWORD), ('wParamL', wintypes.WORD), ('wParamH', wintypes.WORD)]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ('dx', wintypes.LONG),
        ('dy', wintypes.LONG),
        ('mouseData', wintypes.DWORD),
        ('dwFlags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ULONG_PTR)
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [('mi', MOUSEINPUT), ('ki', KEYBDINPUT), ('hi', HARDWAREINPUT)]

class INPUT(ctypes.Structure):
    _fields_ = [('type', wintypes.DWORD), ('union', INPUT_UNION)]

user32 = ctypes.windll.user32
SendInput = user32.SendInput
SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
SendInput.restype = wintypes.UINT

def send_unicode_char(char):
    if char in ('\n', '\r'):
        down = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(wVk=VK_RETURN, wScan=0, dwFlags=0, time=0, dwExtraInfo=0)))
        up = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(wVk=VK_RETURN, wScan=0, dwFlags=KEYEVENTF_KEYUP, time=0, dwExtraInfo=0)))
    elif char == '\t':
        down = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(wVk=VK_TAB, wScan=0, dwFlags=0, time=0, dwExtraInfo=0)))
        up = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(wVk=VK_TAB, wScan=0, dwFlags=KEYEVENTF_KEYUP, time=0, dwExtraInfo=0)))
    else:
        code = ord(char)
        down = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(wVk=0, wScan=code, dwFlags=KEYEVENTF_UNICODE, time=0, dwExtraInfo=0)))
        up = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(wVk=0, wScan=code, dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, time=0, dwExtraInfo=0)))
    inputs = (INPUT * 2)(down, up)
    SendInput(2, inputs, ctypes.sizeof(INPUT))

def send_backspace():
    down = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(wVk=VK_BACK, wScan=0, dwFlags=0, time=0, dwExtraInfo=0)))
    up = INPUT(type=INPUT_KEYBOARD, union=INPUT_UNION(ki=KEYBDINPUT(wVk=VK_BACK, wScan=0, dwFlags=KEYEVENTF_KEYUP, time=0, dwExtraInfo=0)))
    inputs = (INPUT * 2)(down, up)
    SendInput(2, inputs, ctypes.sizeof(INPUT))

def is_escape_pressed():
    return bool(user32.GetAsyncKeyState(VK_ESCAPE) & 0x8000)

# ---------------------------------------------------------------------------
# BÓC TÁCH NỘI DUNG THEO HEADING
# ---------------------------------------------------------------------------
HEADING_REGEX = re.compile(
    r'^(?:'
    r'#{1,6}\s+.+|'                           # Markdown #, ##, ###...
    r'(?:Phần|Bài|Câu|Mục|Chương)\s+\d+[:.].+|' # Phần 1: ..., Câu 2. ...
    r'[IVXLCDM]+\.\s+.+'                      # I. ..., 1. ...
    r')$',
    re.MULTILINE
)

def parse_text_to_sections(raw_text):
    text = raw_text.replace('\r\n', '\n').strip()
    if not text:
        return []

    matches = list(HEADING_REGEX.finditer(text))
    if not matches:
        # Nếu không có heading nào, gom toàn bộ file thành 1 mục duy nhất để gõ một lèo
        return [("[01] Toàn bộ nội dung file", text)]

    sections = []
    # Đoạn văn trước heading đầu tiên (trang bìa / info)
    first_match = matches[0]
    if first_match.start() > 0:
        pre_text = text[:first_match.start()].strip()
        if pre_text:
            sections.append(("[00] Trang bìa / Thông tin mở đầu", pre_text))

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        full_chunk = text[start:end].strip()
        lines = full_chunk.split('\n')
        heading_title = lines[0].strip()
        sections.append((heading_title, full_chunk))

    return sections

# ---------------------------------------------------------------------------
# GIAO DIỆN CHÍNH (TKINTER)
# ---------------------------------------------------------------------------
class HumanTyperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AutoTyper Docs - Trợ thủ gõ mô phỏng người thật")
        self.geometry("880x680")
        self.minsize(780, 560)

        # Trạng thái
        self.sections = []          # List of (heading, content)
        self.completed_indices = set()
        self.is_typing = False
        self.stop_requested = False
        self.resume_state = None
        self.progress_file = "typer_progress.json"

        self._init_style()
        self._build_ui()
        self._load_saved_progress()

    def _init_style(self):
        style = ttk.Style(self)
        style.theme_use('vista' if 'vista' in style.theme_names() else 'default')
        style.configure('Heading.TLabel', font=('Segoe UI', 11, 'bold'), foreground='#1a73e8')
        style.configure('Success.TLabel', font=('Segoe UI', 10, 'bold'), foreground='#1e8e3e')
        style.configure('Danger.TButton', font=('Segoe UI', 10, 'bold'))

    def _build_ui(self):
        # 1. Khung hướng dẫn / cảnh báo
        banner = tk.Frame(self, bg='#e8f0fe', padx=10, pady=8)
        banner.pack(fill=tk.X, padx=10, pady=6)
        lbl_info = tk.Label(
            banner,
            text="💡 MẸO QUAN TRỌNG: Chuyển Unikey/EVKey sang chế độ [E] (Tiếng Anh) trước khi gõ để tránh xung đột phím!\n"
                 "Nhấn phím ESC bất kỳ lúc nào để DỪNG KHẨN CẤP.",
            bg='#e8f0fe', fg='#174ea6', font=('Segoe UI', 9), justify=tk.LEFT
        )
        lbl_info.pack(anchor=tk.W)

        # 2. Khung nạp file
        file_frame = ttk.LabelFrame(self, text=" 1. Nạp file bài làm ", padding=8)
        file_frame.pack(fill=tk.X, padx=10, pady=4)

        btn_browse = ttk.Button(file_frame, text="📁 Chọn file bài giải (.md / .txt)", command=self._on_browse_file)
        btn_browse.pack(side=tk.LEFT, padx=4)

        btn_clipboard = ttk.Button(file_frame, text="📋 Dán từ Clipboard", command=self._on_paste_clipboard)
        btn_clipboard.pack(side=tk.LEFT, padx=4)

        self.lbl_file_status = ttk.Label(file_frame, text="Chưa nạp file nào", foreground='#5f6368')
        self.lbl_file_status.pack(side=tk.LEFT, padx=10)

        # 3. Khung danh sách Section & Preview
        content_frame = ttk.Frame(self, padding=4)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        # Bên trái: Listbox danh sách các Section
        left_sub = ttk.LabelFrame(content_frame, text=" 2. Danh sách các phần phát hiện được ", padding=6)
        left_sub.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 4))

        self.listbox_sections = tk.Listbox(left_sub, font=('Segoe UI', 9), selectmode=tk.SINGLE)
        scroll_y = ttk.Scrollbar(left_sub, orient=tk.VERTICAL, command=self.listbox_sections.yview)
        self.listbox_sections.config(yscrollcommand=scroll_y.set)
        self.listbox_sections.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_sections.bind('<<ListboxSelect>>', self._on_select_section)

        # Bên phải: Xem trước nội dung
        right_sub = ttk.LabelFrame(content_frame, text=" Xem trước nội dung mục đã chọn ", padding=6)
        right_sub.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(4, 0))

        self.txt_preview = tk.Text(right_sub, wrap=tk.WORD, font=('Consolas', 9), height=10)
        scroll_prev = ttk.Scrollbar(right_sub, orient=tk.VERTICAL, command=self.txt_preview.yview)
        self.txt_preview.config(yscrollcommand=scroll_prev.set)
        self.txt_preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_prev.pack(side=tk.RIGHT, fill=tk.Y)

        # 4. Cấu hình tốc độ & hành vi người thật
        cfg_frame = ttk.LabelFrame(self, text=" 3. Cấu hình tốc độ & Mô phỏng người thật ", padding=8)
        cfg_frame.pack(fill=tk.X, padx=10, pady=4)

        # Slider WPM
        ttk.Label(cfg_frame, text="Tốc độ gõ:").grid(row=0, column=0, sticky=tk.W, padx=4)
        self.scale_wpm = ttk.Scale(cfg_frame, from_=30, to=260, value=260, orient=tk.HORIZONTAL, command=self._update_cfg_labels)
        self.scale_wpm.grid(row=0, column=1, sticky=tk.EW, padx=4)
        self.lbl_wpm_val = ttk.Label(cfg_frame, text="260 WPM")
        self.lbl_wpm_val.grid(row=0, column=2, padx=4)

        # Slider Typo (tỉ lệ gõ sai và xoá sửa)
        ttk.Label(cfg_frame, text="Tỉ lệ gõ sai (Typo):").grid(row=0, column=3, sticky=tk.W, padx=12)
        self.scale_typo = ttk.Scale(cfg_frame, from_=0.0, to=4.0, value=1.8, orient=tk.HORIZONTAL, command=self._update_cfg_labels)
        self.scale_typo.grid(row=0, column=4, sticky=tk.EW, padx=4)
        self.lbl_typo_val = ttk.Label(cfg_frame, text="1.8 %")
        self.lbl_typo_val.grid(row=0, column=5, padx=4)

        # Độ trễ đếm ngược
        ttk.Label(cfg_frame, text="Thời gian đếm ngược:").grid(row=1, column=0, sticky=tk.W, padx=4, pady=4)
        self.spn_delay = ttk.Spinbox(cfg_frame, from_=3, to=15, width=6)
        self.spn_delay.set(5)
        self.spn_delay.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
        ttk.Label(cfg_frame, text="giây (đủ để chuyển sang tab Google Docs)").grid(row=1, column=2, columnspan=3, sticky=tk.W)

        # Tuỳ chọn bỏ qua dòng tiêu đề
        self.chk_skip_heading_var = tk.BooleanVar(value=False)
        self.chk_skip_heading = ttk.Checkbutton(
            cfg_frame,
            text="☑ Chỉ gõ phần bài giải (Bỏ qua dòng tiêu đề vì trên Docs đã gõ sẵn)",
            variable=self.chk_skip_heading_var,
            command=self._on_select_section
        )
        self.chk_skip_heading.grid(row=2, column=0, columnspan=6, sticky=tk.W, padx=4, pady=2)

        # Tuỳ chọn tự động ngắt nghỉ để chốt mốc Version History
        self.chk_snapshot_mode_var = tk.BooleanVar(value=True)
        self.chk_snapshot_mode = ttk.Checkbutton(
            cfg_frame,
            text="🕒 Tự động tách mốc Version History (Random 1–5 phút/mốc để Google Docs lưu mốc con)",
            variable=self.chk_snapshot_mode_var
        )
        self.chk_snapshot_mode.grid(row=3, column=0, columnspan=6, sticky=tk.W, padx=4, pady=2)

        # Gõ liên tục: bỏ các khoảng nghỉ và lỗi gõ mô phỏng
        self.chk_continuous_var = tk.BooleanVar(value=False)
        self.chk_continuous = ttk.Checkbutton(
            cfg_frame,
            text="Gõ liên tục (bỏ nghỉ và lỗi gõ mô phỏng)",
            variable=self.chk_continuous_var
        )
        self.chk_continuous.grid(row=4, column=0, columnspan=6, sticky=tk.W, padx=4, pady=2)

        cfg_frame.columnconfigure(1, weight=1)
        cfg_frame.columnconfigure(4, weight=1)

        # 5. Thanh điều khiển & Tiến trình
        ctrl_frame = ttk.Frame(self, padding=8)
        ctrl_frame.pack(fill=tk.X, padx=10, pady=4)

        self.btn_start = tk.Button(
            ctrl_frame, text="▶ BẮT ĐẦU GÕ MỤC ĐÃ CHỌN", bg='#1a73e8', fg='white',
            font=('Segoe UI', 10, 'bold'), relief=tk.RAISED, padx=14, pady=6,
            command=self._start_typing_thread
        )
        self.btn_start.pack(side=tk.LEFT, padx=4)

        self.btn_start_all = tk.Button(
            ctrl_frame, text="GÕ TẤT CẢ", bg='#188038', fg='white',
            font=('Segoe UI', 10, 'bold'), relief=tk.RAISED, padx=10, pady=6,
            command=lambda: self._start_typing_thread(all_sections=True)
        )
        self.btn_start_all.pack(side=tk.LEFT, padx=4)

        self.btn_stop = tk.Button(
            ctrl_frame, text="⏹ DỪNG (ESC)", bg='#d93025', fg='white',
            font=('Segoe UI', 10, 'bold'), relief=tk.RAISED, padx=12, pady=6,
            command=self._stop_typing
        )
        self.btn_stop.pack(side=tk.LEFT, padx=4)

        self.lbl_status = ttk.Label(ctrl_frame, text="Sẵn sàng.", font=('Segoe UI', 10))
        self.lbl_status.pack(side=tk.LEFT, padx=14)

        extra_frame = ttk.Frame(self, padding=(8, 0, 8, 4))
        extra_frame.pack(fill=tk.X, padx=10)
        self.btn_resume = ttk.Button(extra_frame, text="TI\u1ebeP T\u1ee4C T\u1eea CH\u1ed6 D\u1eeaNG", command=lambda: self._start_typing_thread(resume=True))
        self.btn_resume.pack(side=tk.LEFT, padx=4)
        self.btn_continuous_all = ttk.Button(extra_frame, text="G\u00d5 T\u1ea4T C\u1ea2 LI\u00caN T\u1ee4C", command=self._start_continuous_all)
        self.btn_continuous_all.pack(side=tk.LEFT, padx=4)

        # Progress bar
        self.prog_bar = ttk.Progressbar(self, orient=tk.HORIZONTAL, mode='determinate')
        self.prog_bar.pack(fill=tk.X, padx=10, pady=(0, 10))

    def _update_cfg_labels(self, _=None):
        wpm = int(self.scale_wpm.get())
        typo = round(self.scale_typo.get(), 1)
        self.lbl_wpm_val.config(text=f"{wpm} WPM")
        self.lbl_typo_val.config(text=f"{typo} %")

    def _on_browse_file(self):
        filepath = filedialog.askopenfilename(
            title="Chọn file bài giải",
            filetypes=[("Markdown / Text files", "*.md *.txt"), ("All files", "*.*")]
        )
        if not filepath:
            return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self._load_content(content, os.path.basename(filepath))
        except Exception as e:
            messagebox.showerror("Lỗi đọc file", f"Không thể đọc file: {e}")

    def _on_paste_clipboard(self):
        try:
            content = self.clipboard_get()
            if not content.strip():
                messagebox.showwarning("Thông báo", "Clipboard đang trống!")
                return
            self._load_content(content, "Nội dung từ Clipboard")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lấy nội dung từ Clipboard: {e}")

    def _load_content(self, text, source_name):
        self.sections = parse_text_to_sections(text)
        if not self.sections:
            messagebox.showwarning("Cảnh báo", "Không tìm thấy nội dung hợp lệ!")
            return

        self.lbl_file_status.config(
            text=f"Đã nạp: {source_name} | Tìm thấy {len(self.sections)} phần",
            foreground='#1e8e3e'
        )
        self._refresh_listbox()
        self.listbox_sections.selection_set(0)
        self._on_select_section(None)

    def _refresh_listbox(self):
        self.listbox_sections.delete(0, tk.END)
        wpm = int(self.scale_wpm.get())
        for idx, (title, chunk) in enumerate(self.sections):
            word_count = len(chunk.split())
            est_minutes = round(word_count / wpm, 1) if wpm > 0 else 0
            check = "✓ " if idx in self.completed_indices else "  "
            display_text = f"{check}[{idx+1:02d}] {title[:40]} ({word_count} từ ~{est_minutes}p)"
            self.listbox_sections.insert(tk.END, display_text)

    def _get_chunk_to_type(self, full_chunk):
        if self.chk_skip_heading_var.get():
            lines = full_chunk.split('\n')
            if len(lines) > 1:
                return '\n'.join(lines[1:]).strip()
        return full_chunk

    def _on_select_section(self, _=None):
        sel = self.listbox_sections.curselection()
        if not sel:
            return
        idx = sel[0]
        _, chunk = self.sections[idx]
        display_chunk = self._get_chunk_to_type(chunk)
        self.txt_preview.delete("1.0", tk.END)
        self.txt_preview.insert(tk.END, display_chunk)

    def _load_saved_progress(self):
        if os.path.exists(self.progress_file):
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.completed_indices = set(data.get("completed_indices", []))
                    self.resume_state = data.get("resume_state")
            except Exception:
                pass

    def _save_progress(self):
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump({"completed_indices": list(self.completed_indices), "resume_state": self.resume_state}, f)
        except Exception:
            pass

    def _stop_typing(self):
        if self.is_typing:
            self.stop_requested = True
            self.lbl_status.config(text="Đã gửi lệnh dừng. Đang dừng...", foreground='#d93025')

    def _start_continuous_all(self):
        self.chk_continuous_var.set(True)
        self._start_typing_thread(all_sections=True)

    def _start_typing_thread(self, all_sections=False, resume=False):
        if self.is_typing:
            return
        if resume:
            if not self.resume_state or not self.sections:
                messagebox.showwarning("Ti\u1ebfp t\u1ee5c", "H\u00e3y n\u1ea1p l\u1ea1i file v\u00e0 d\u1eebng m\u1ed9t l\u1ea7n tr\u01b0\u1edbc khi ti\u1ebfp t\u1ee5c.")
                return
            indices = self.resume_state.get("indices", [])
            if any(not isinstance(idx, int) or idx < 0 or idx >= len(self.sections) for idx in indices):
                messagebox.showwarning("Ti\u1ebfp t\u1ee5c", "N\u1ed9i dung kh\u00f4ng kh\u1edbp v\u1edbi l\u1ea7n g\u00f5 tr\u01b0\u1edbc.")
                return
        elif all_sections:
            if not self.sections:
                messagebox.showwarning("Chưa nạp file", "Vui lòng nạp nội dung trước khi gõ!")
                return
            indices = list(range(len(self.sections)))
        else:
            sel = self.listbox_sections.curselection()
            if not sel:
                messagebox.showwarning("Chưa chọn mục", "Vui lòng chọn 1 mục trong danh sách để gõ!")
                return
            indices = [sel[0]]

        chunks = [(idx, self._get_chunk_to_type(self.sections[idx][1])) for idx in indices]
        chunks = [(idx, chunk) for idx, chunk in chunks if chunk]
        if not chunks:
            messagebox.showwarning("Không có nội dung", "Không có nội dung để gõ!")
            return
        text_to_type = "\n\n".join(chunk for _, chunk in chunks)
        section_ends = {}
        position = 0
        for idx, chunk in chunks:
            position += len(chunk)
            section_ends[position] = idx
            position += 2

        text_hash = hashlib.sha256(text_to_type.encode('utf-8')).hexdigest()
        start_offset = 0
        if resume:
            if text_hash != self.resume_state.get("text_hash"):
                messagebox.showwarning("Ti\u1ebfp t\u1ee5c", "N\u1ed9i dung ho\u1eb7c t\u00f9y ch\u1ecdn b\u1ecf ti\u00eau \u0111\u1ec1 \u0111\u00e3 thay \u0111\u1ed5i. H\u00e3y n\u1ea1p \u0111\u00fang n\u1ed9i dung v\u00e0 kh\u00f4i ph\u1ee5c t\u00f9y ch\u1ecdn c\u0169.")
                return
            start_offset = self.resume_state.get("offset", 0)
            if not isinstance(start_offset, int) or not 0 <= start_offset < len(text_to_type):
                messagebox.showwarning("Ti\u1ebfp t\u1ee5c", "Kh\u00f4ng c\u00f3 v\u1ecb tr\u00ed h\u1ee3p l\u1ec7 \u0111\u1ec3 ti\u1ebfp t\u1ee5c.")
                return
        self.resume_state = {"indices": indices, "text_hash": text_hash, "offset": start_offset}
        self._save_progress()

        try:
            delay_sec = int(self.spn_delay.get())
        except ValueError:
            delay_sec = 5

        wpm = int(self.scale_wpm.get())
        typo_rate = self.scale_typo.get() / 100.0
        snapshot_mode = self.chk_snapshot_mode_var.get()
        continuous_mode = self.chk_continuous_var.get()

        self.is_typing = True
        self.stop_requested = False
        self.btn_start.config(state=tk.DISABLED)
        self.btn_start_all.config(state=tk.DISABLED)
        self.btn_resume.config(state=tk.DISABLED)
        self.btn_continuous_all.config(state=tk.DISABLED)

        t = threading.Thread(
            target=self._typing_worker,
            args=(section_ends, text_to_type, delay_sec, wpm, typo_rate, snapshot_mode, continuous_mode, start_offset),
            daemon=True
        )
        t.start()

    def _typing_worker(self, section_ends, text, delay_sec, wpm, typo_rate, snapshot_mode, continuous_mode, start_offset):
        # 1. Đếm ngược
        for s in range(delay_sec, 0, -1):
            if self.stop_requested or is_escape_pressed():
                self._finish_worker("Đã hủy trước khi bắt đầu.", False)
                return
            self.lbl_status.config(
                text=f"⏳ CHUYỂN SANG TAB GOOGLE DOCS VÀ CLICK CHUỘT: {s}s...",
                foreground='#d93025'
            )
            time.sleep(1.0)

        self.lbl_status.config(text="✍️ Đang gõ... Nhấn ESC để dừng!", foreground='#1a73e8')

        total_chars = len(text)
        self.prog_bar['maximum'] = total_chars
        self.prog_bar['value'] = start_offset

        # Tính toán delay cơ bản theo WPM (1 từ ~ 5 ký tự)
        base_char_delay = 60.0 / (wpm * 5.0)

        def get_random_chunk_words():
            # Random lượng từ gõ cho mỗi chặng để tạo khoảng cách ngẫu nhiên 1 - 5 phút:
            # - Chặng ngắn (~20-35 từ): gõ ~30-40s + nghỉ ~55-70s  => Tổng ~1.5 - 2 phút
            # - Chặng vừa  (~45-75 từ): gõ ~1-1.5m + nghỉ ~60-80s  => Tổng ~2.5 - 3.5 phút
            # - Chặng dài  (~85-130 từ): gõ ~2-2.5m + nghỉ ~65-90s => Tổng ~4 - 5 phút
            roll = random.random()
            if roll < 0.35:
                return random.randint(20, 35)
            elif roll < 0.75:
                return random.randint(45, 75)
            else:
                return random.randint(85, 130)

        word_counter = 0
        target_chunk_words = get_random_chunk_words()

        for i in range(start_offset, len(text)):
            char = text[i]
            # Kiểm tra phím dừng khẩn cấp
            if self.stop_requested or is_escape_pressed():
                self._finish_worker("Đã dừng khẩn cấp bởi người dùng (ESC).", False)
                return

            # Giả lập gõ sai ngẫu nhiên (Typo)
            if not continuous_mode and char.isalpha() and random.random() < typo_rate:
                # Gõ 1 ký tự sai ngẫu nhiên
                wrong_char = chr(random.randint(97, 122))
                send_unicode_char(wrong_char)
                time.sleep(random.uniform(0.15, 0.40))  # Giật mình nhận ra gõ sai
                send_backspace()
                time.sleep(random.uniform(0.08, 0.22))

            # Gõ ký tự thật
            send_unicode_char(char)
            self.resume_state["offset"] = i + 1

            if i + 1 in section_ends:
                self.completed_indices.add(section_ends[i + 1])
                self._save_progress()

            # Đếm từ
            if char == ' ':
                word_counter += 1

            # Cập nhật tiến độ
            if i % 5 == 0 or i == total_chars - 1:
                self.prog_bar['value'] = i + 1
                percent = int(((i + 1) / total_chars) * 100)
                self.lbl_status.config(
                    text=f"\u0110ang g\u00f5: {i+1}/{total_chars} k\u00fd t\u1ef1 ({percent}%)"
                )

            # Tính toán độ trễ nhịp điệu người thật
            delay = max(0.02, random.gauss(base_char_delay, base_char_delay * 0.35))

            if not continuous_mode and char in ('.', '!', '?'):
                # Nghỉ sau khi hết câu để nghĩ câu tiếp theo
                delay = random.uniform(1.2, 3.2)
            elif not continuous_mode and char in (',', ';', ':'):
                # Nghỉ nhẹ sau dấu phẩy
                delay = random.uniform(0.4, 0.9)
            elif not continuous_mode and char == '\n':
                # Xuống dòng / ngắt đoạn
                delay = random.uniform(2.5, 5.5)

            # NGHỈ CHỐT MỐC VERSION HISTORY (Nếu bật snapshot_mode)
            # Điểm dừng tự nhiên: xuống dòng (\n) hoặc hết câu ('. ', '? ', '! ')
            is_sentence_end = (char in ('.', '!', '?')) and (i + 1 < total_chars and text[i+1] in (' ', '\n', '\r'))
            is_pause_point = (char == '\n') or is_sentence_end

            if not continuous_mode and snapshot_mode and is_pause_point and word_counter >= target_chunk_words and i < total_chars - 30:
                word_counter = 0
                target_chunk_words = get_random_chunk_words()
                pause_duration = random.randint(55, 90)

                for remaining in range(pause_duration, 0, -1):
                    if self.stop_requested or is_escape_pressed():
                        self._finish_worker("Đã dừng khẩn cấp bởi người dùng (ESC).", False)
                        return
                    self.lbl_status.config(
                        text=f"☕ Đang nghỉ {remaining}s để Docs chốt mốc lịch sử... (Đã gõ {i+1}/{total_chars} ký tự)",
                        foreground='#e37400'
                    )
                    time.sleep(1.0)

                self.lbl_status.config(text="✍️ Hết giờ nghỉ! Đang gõ tiếp...", foreground='#1a73e8')
                continue

            # Đôi khi nghỉ tay đọc lại tài liệu (chỉ khi tắt snapshot_mode)
            if not continuous_mode and not snapshot_mode and char == ' ':
                if word_counter > random.randint(40, 70):
                    word_counter = 0
                    if random.random() < 0.6:
                        time.sleep(random.uniform(4.0, 9.0))

            time.sleep(delay)

        # Hoàn thành mục này
        self._finish_worker("\u0110\u00e3 g\u00f5 xong n\u1ed9i dung \u0111\u00e3 ch\u1ecdn!", True)

    def _finish_worker(self, message, is_success):
        self.is_typing = False
        self.stop_requested = False
        if is_success:
            self.resume_state = None
        self._save_progress()
        self.btn_start.config(state=tk.NORMAL)
        self.btn_start_all.config(state=tk.NORMAL)
        self.btn_resume.config(state=tk.NORMAL)
        self.btn_continuous_all.config(state=tk.NORMAL)
        self.lbl_status.config(
            text=message,
            foreground='#1e8e3e' if is_success else '#d93025'
        )
        self._refresh_listbox()
        if is_success:
            try:
                # Kêu tiếng Bíp hệ thống báo xong
                user32.MessageBeep(0xFFFFFFFF)
            except Exception:
                pass


if __name__ == '__main__':
    app = HumanTyperApp()
    app.mainloop()
