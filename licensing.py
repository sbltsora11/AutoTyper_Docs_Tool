"""Xác minh bản quyền ký bằng Ed25519 và gắn với MachineGuid của Windows."""
import base64
import hashlib
import json
import os
from pathlib import Path
import winreg
from cryptography.hazmat.primitives.serialization import load_pem_public_key

PUBLIC_KEY = Path(__file__).with_name('license_public_key.pem').read_bytes()

def machine_id():
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Cryptography', 0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
        guid = winreg.QueryValueEx(key, 'MachineGuid')[0]
    return hashlib.sha256(('AutoTyper-Docs-v1:' + guid.strip().lower()).encode()).hexdigest()

def parse_license(data):
    try:
        obj = json.loads(data)
        payload = base64.b64decode(obj['payload'], validate=True)
        signature = base64.b64decode(obj['signature'], validate=True)
        load_pem_public_key(PUBLIC_KEY).verify(signature, payload)
        content = json.loads(payload)
        if (content.get('product') != 'AutoTyper-Docs-v1' or
            not isinstance(content.get('id'), str) or len(content['id']) != 32 or
            type(content.get('days')) is not int or not 1 <= content['days'] <= 3650):
            raise ValueError()
        return content
    except Exception as exc:
        raise ValueError('File b?n quy?n kh?ng h?p l?.') from exc

def license_path():
    return Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'AutoTyperDocs' / 'activation.dat'

def protect(data, decrypt=False):
    import ctypes
    from ctypes import wintypes
    class Blob(ctypes.Structure):
        _fields_ = [('size', wintypes.DWORD), ('data', ctypes.POINTER(ctypes.c_ubyte))]
    buf = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
    source = Blob(len(data), buf)
    target = Blob()
    crypt = ctypes.windll.crypt32
    func = crypt.CryptUnprotectData if decrypt else crypt.CryptProtectData
    if not func(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(target)):
        raise ctypes.WinError()
    try:
        return ctypes.string_at(target.data, target.size)
    finally:
        local_free = ctypes.windll.kernel32.LocalFree
        local_free.argtypes = [ctypes.c_void_p]
        local_free.restype = ctypes.c_void_p
        local_free(ctypes.cast(target.data, ctypes.c_void_p))

def load_state():
    path = license_path()
    if not path.exists():
        return {'records': {}, 'active': None, 'machine': machine_id()}
    state = json.loads(protect(path.read_bytes(), True))
    if state['machine'] != machine_id():
        raise ValueError('D? li?u k?ch ho?t kh?ng thu?c m?y n?y.')
    return state

def save_state(state):
    path = license_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_bytes(protect(json.dumps(state).encode()))
    os.replace(temp, path)

def check_active(state, now=None):
    import time
    now = time.time() if now is None else now
    record = state['records'].get(state.get('active'))
    if not record:
        return False
    if now < record['last'] - 300:
        raise ValueError('??ng h? h? th?ng ?? b? l?i. H?y ch?nh l?i gi?.')
    record['last'] = max(now, record['last'])
    save_state(state)
    return now < record['expires']

def activate(data, state, now=None):
    import time
    now = time.time() if now is None else now
    content = parse_license(data)
    ident = content['id']
    if ident not in state['records']:
        state['records'][ident] = {'expires': now + content['days'] * 86400, 'last': now}
    state['active'] = ident
    if not check_active(state, now):
        raise ValueError('B?n quy?n n?y ?? h?t h?n tr?n m?y n?y.')
    return content
