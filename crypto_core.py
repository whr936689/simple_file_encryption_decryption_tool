"""
加密核心模块 - 支持多种加密算法

文件格式头（新格式 JMD1）：
  偏移  长度  说明
  0     4     魔数 "JMD1"
  4     2     算法编号 (1=offset, 2=xor, 3=aes256)
  6     4     原始扩展名长度 N
  10    N     原始扩展名（如 ".txt"）
  10+N  ...   加密后的数据体

旧格式（兼容读取，无魔数）：
  前 4 字节 = 扩展名长度（uint32）
  接着 N 字节 = 扩展名
  剩余 = offset 算法加密的数据体
"""

import struct
import hashlib
import os

# 算法常量
ALGO_OFFSET = 1
ALGO_XOR = 2
ALGO_AES256 = 3

ALGO_NAMES = {
    ALGO_OFFSET: "字节偏移 (简单/兼容旧版)",
    ALGO_XOR: "XOR (循环异或)",
    ALGO_AES256: "AES-256-CBC (安全)",
}

MAGIC = b"JMD1"
HEADER_FIXED_SIZE = 10  # 4 (magic) + 2 (algo) + 4 (ext_len)


def _key_to_int(key_str, legacy=False):
    """
    把密码字符串转成整数 key（用于 offset 和 xor 算法）
    :param legacy: True 时使用旧版逻辑（直接 int 取模，兼容旧文件）
    """
    if legacy:
        # 旧版：直接 int(key) % 256；如果密码不是纯数字就 fallback 到 md5
        try:
            return int(key_str) % 256
        except ValueError:
            pass
    h = hashlib.md5(key_str.encode('utf-8')).hexdigest()
    return int(h, 16)


def _derive_aes_key(key_str):
    """用 SHA-256 把密码转成 32 字节 AES key"""
    return hashlib.sha256(key_str.encode('utf-8')).digest()


def detect_format(data):
    """检测加密文件的格式，返回 (algorithm, is_new_format)"""
    if data[:4] == MAGIC:
        algo = struct.unpack('<H', data[4:6])[0]
        return algo, True
    # 旧格式：前4字节是扩展名长度
    return ALGO_OFFSET, False


def _read_header_new(data):
    """读取新格式头，返回 (algo, ext, body)"""
    algo = struct.unpack('<H', data[4:6])[0]
    ext_len = struct.unpack('<I', data[6:10])[0]
    ext = data[10:10 + ext_len].decode('utf-8')
    body = data[10 + ext_len:]
    return algo, ext, body


def _read_header_old(data):
    """读取旧格式头，返回 (ext, body)"""
    ext_len = struct.unpack('<I', data[:4])[0]
    ext = data[4:4 + ext_len].decode('utf-8')
    body = data[4 + ext_len:]
    return ext, body


def _build_header_new(algo, ext):
    """构建新格式头"""
    ext_bytes = ext.encode('utf-8')
    ext_len = struct.pack('<I', len(ext_bytes))
    algo_bytes = struct.pack('<H', algo)
    return MAGIC + algo_bytes + ext_len + ext_bytes


# ========= 各算法实现 =========

def _encrypt_offset(data, key_int, progress_cb=None):
    """原始字节偏移加密"""
    k = key_int % 256
    result = bytearray()
    total = len(data)
    step = max(1, total // 100) if total > 0 else 1
    for i, b in enumerate(data):
        result.append((b + k) % 256)
        if progress_cb and (i % step == 0):
            progress_cb(i / total * 100)
    return bytes(result)


def _decrypt_offset(data, key_int, progress_cb=None):
    k = key_int % 256
    result = bytearray()
    total = len(data)
    step = max(1, total // 100) if total > 0 else 1
    for i, b in enumerate(data):
        result.append((b - k) % 256)
        if progress_cb and (i % step == 0):
            progress_cb(i / total * 100)
    return bytes(result)


def _encrypt_xor(data, key_int, progress_cb=None):
    """循环 XOR 加密"""
    # 把 key_int 转成字节流
    key_bytes = str(key_int).encode('utf-8') or b'\x00'
    result = bytearray()
    total = len(data)
    step = max(1, total // 100) if total > 0 else 1
    for i, b in enumerate(data):
        result.append(b ^ key_bytes[i % len(key_bytes)])
        if progress_cb and (i % step == 0):
            progress_cb(i / total * 100)
    return bytes(result)


def _decrypt_xor(data, key_int, progress_cb=None):
    # XOR 的解密和加密完全一样
    return _encrypt_xor(data, key_int, progress_cb)


def _encrypt_aes(data, key_str, progress_cb=None):
    """AES-256-CBC 加密"""
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad

    key = _derive_aes_key(key_str)
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    if progress_cb:
        progress_cb(20)

    padded = pad(data, AES.block_size)
    encrypted = cipher.encrypt(padded)

    if progress_cb:
        progress_cb(100)

    # 返回 IV + 密文（IV 明文存储，解密时需要）
    return iv + encrypted


def _decrypt_aes(data, key_str, progress_cb=None):
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad

    key = _derive_aes_key(key_str)
    iv = data[:16]
    ciphertext = data[16:]

    if progress_cb:
        progress_cb(20)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)

    if progress_cb:
        progress_cb(100)

    return decrypted


# ========= 对外统一接口 =========

def encrypt_file_content(data, key_str, algo, orig_ext, progress_cb=None):
    """
    加密文件内容（纯字节），返回带新格式头的完整加密数据
    :param data: 原始文件字节
    :param key_str: 用户密码
    :param algo: ALGO_OFFSET / ALGO_XOR / ALGO_AES256
    :param orig_ext: 原始文件扩展名，如 '.txt'
    :param progress_cb: 进度回调 (0-100)
    """
    # 1. 处理扩展名
    if not orig_ext.startswith('.') and orig_ext:
        orig_ext = '.' + orig_ext

    # 2. 加密数据体
    if algo == ALGO_OFFSET:
        body = _encrypt_offset(data, _key_to_int(key_str),
                               progress_cb=lambda p: progress_cb(p * 0.7) if progress_cb else None)
    elif algo == ALGO_XOR:
        body = _encrypt_xor(data, _key_to_int(key_str),
                            progress_cb=lambda p: progress_cb(p * 0.7) if progress_cb else None)
    elif algo == ALGO_AES256:
        body = _encrypt_aes(data, key_str,
                            progress_cb=lambda p: progress_cb(p * 0.7) if progress_cb else None)
    else:
        raise ValueError(f"未知算法: {algo}")

    # 3. 拼文件头
    if progress_cb:
        progress_cb(85)
    header = _build_header_new(algo, orig_ext)
    if progress_cb:
        progress_cb(100)
    return header + body


def decrypt_file_content(data, key_str, progress_cb=None):
    """
    解密加密文件内容，返回 (原始数据, 原始扩展名, 使用的算法)
    自动检测新格式（JMD1 魔数）还是旧格式（纯 offset）
    """
    algo, is_new = detect_format(data)

    if is_new:
        algo, ext, body = _read_header_new(data)
    else:
        ext, body = _read_header_old(data)

    # 旧格式兼容：旧版用 int(key_str) % 256，新版用 md5 hash
    legacy = not is_new

    # 解密
    if algo == ALGO_OFFSET:
        raw = _decrypt_offset(body, _key_to_int(key_str, legacy=legacy),
                              progress_cb=lambda p: progress_cb(10 + p * 0.8) if progress_cb else None)
    elif algo == ALGO_XOR:
        raw = _decrypt_xor(body, _key_to_int(key_str, legacy=legacy),
                           progress_cb=lambda p: progress_cb(10 + p * 0.8) if progress_cb else None)
    elif algo == ALGO_AES256:
        raw = _decrypt_aes(body, key_str,
                           progress_cb=lambda p: progress_cb(10 + p * 0.8) if progress_cb else None)
    else:
        raise ValueError(f"未知算法: {algo}")

    if progress_cb:
        progress_cb(100)

    return raw, ext, algo
