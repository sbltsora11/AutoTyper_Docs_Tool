"""Giao diện cấp bản quyền dành riêng cho người bán."""
import base64
import json
import uuid
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from cryptography.hazmat.primitives.serialization import load_pem_private_key, Encoding, PublicFormat

BASE = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parent
PUBLIC_KEY = b'''-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEA5Q/2Z9HIqyZlHYWuA78AwmbXbEjQO/f2MJ3IuMKIblE=
-----END PUBLIC KEY-----
'''

def create_license(days, key_path, output):
    days = int(days)
    if not 1 <= days <= 3650:
        raise ValueError('Number of days must be between 1 and 3650.')
    try:
        key = load_pem_private_key(Path(key_path).read_bytes(), password=None)
    except ValueError as exc:
        raise ValueError('File đã chọn không phải khóa riêng hợp lệ. Hãy chọn license_private_key.pem, không chọn license_public_key.pem.') from exc
    if key.public_key().public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo) != PUBLIC_KEY:
        raise ValueError('Khóa riêng không khớp với phiên bản ứng dụng này.')
    payload = json.dumps({'product': 'AutoTyper-Docs-v1', 'id': uuid.uuid4().hex, 'days': days}, separators=(',', ':')).encode()
    data = {'payload': base64.b64encode(payload).decode(), 'signature': base64.b64encode(key.sign(payload)).decode()}
    Path(output).write_text(json.dumps(data), encoding='utf-8')

def main():
    root = tk.Tk()
    root.title('Công cụ tạo bản quyền AutoTyper')
    root.geometry('680x280')
    root.resizable(False, False)
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill='both', expand=True)
    days = tk.StringVar(value='3')
    default_key = BASE / 'license_private_key.pem'
    for folder in (BASE.parent, BASE.parent.parent):
        if default_key.exists():
            break
        if (folder / 'license_private_key.pem').exists():
            default_key = folder / 'license_private_key.pem'
    key = tk.StringVar(value=str(default_key))
    ttk.Label(frame, text='Thời hạn sử dụng (ngày):').pack(anchor='w')
    ttk.Entry(frame, textvariable=days).pack(fill='x', pady=(4, 12))
    ttk.Label(frame, text='File khóa riêng:').pack(anchor='w')
    row = ttk.Frame(frame)
    row.pack(fill='x', pady=(4, 12))
    ttk.Entry(row, textvariable=key).pack(side='left', fill='x', expand=True)
    def choose_key():
        selected = filedialog.askopenfilename(title='Chọn khóa riêng', filetypes=[('Khóa PEM', '*.pem'), ('Tất cả', '*.*')])
        if selected:
            key.set(selected)
    ttk.Button(row, text='Chọn...', command=choose_key).pack(side='left', padx=(8, 0))
    def issue():
        if not days.get().isdigit() or not 1 <= int(days.get()) <= 3650:
            messagebox.showerror('Lỗi', 'Số ngày phải từ 1 đến 3650.', parent=root)
            return
        output = filedialog.asksaveasfilename(title='Lưu file bản quyền', defaultextension='.license', filetypes=[('Bản quyền', '*.license')])
        if not output:
            return
        try:
            create_license(days.get(), key.get(), output)
        except Exception as exc:
            messagebox.showerror('Không tạo được bản quyền', str(exc), parent=root)
            return
        messagebox.showinfo('Thành công', 'Đã tạo file bản quyền. Hãy gửi file này cho khách:\n' + output, parent=root)
    ttk.Button(frame, text='Tạo file bản quyền', command=issue).pack(pady=8)
    ttk.Label(frame, text='Giữ bí mật file khóa riêng. Không gửi khóa riêng cho khách.').pack()
    root.mainloop()

if __name__ == '__main__':
    main()
