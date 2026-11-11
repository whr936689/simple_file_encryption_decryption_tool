"""
主流程 - 支持单文件和批量加密/解密
"""

import os
from crypto_core import (
    encrypt_file_content,
    decrypt_file_content,
    detect_format,
    ALGO_OFFSET, ALGO_XOR, ALGO_AES256,
    ALGO_NAMES,
)
from file_cz import (
    read_file,
    write_encrypted_file,
    write_decrypted_file,
)


def encrypt_one_file(file_path, key_str, algo, output_ext=".jmdc", progress_cb=None):
    """
    加密单个文件
    :param progress_cb: 回调 (percent, status) - percent 0~100
    :return: (输出路径, 错误信息或 None)
    """
    try:
        fname = os.path.basename(file_path)

        def cb(n, status=None):
            if progress_cb:
                progress_cb(n, status or f"加密中: {fname}")

        cb(0, "准备读取...")
        raw = read_file(file_path, progress_cb=lambda p: cb(p, "读取文件..."))
        cb(32, "加密数据...")

        orig_ext = os.path.splitext(file_path)[1] or ".dat"
        encrypted = encrypt_file_content(
            raw, key_str, algo, orig_ext,
            progress_cb=lambda p: cb(32 + p * 0.56, "加密数据..."),
        )
        cb(88, "写入磁盘...")

        out_path = write_encrypted_file(
            encrypted, file_path, output_ext,
            progress_cb=lambda p: cb(p, "写入磁盘..."),
        )
        cb(100, f"完成: {os.path.basename(out_path)}")
        return out_path, None
    except Exception as e:
        return None, str(e)


def decrypt_one_file(file_path, key_str, progress_cb=None):
    """
    解密单个文件（自动检测算法）
    :param progress_cb: 回调 (percent, status) - percent 0~100
    :return: (输出路径, 错误信息或 None)
    """
    try:
        fname = os.path.basename(file_path)

        def cb(n, status=None):
            if progress_cb:
                progress_cb(n, status or f"解密中: {fname}")

        cb(0, "准备读取...")
        raw = read_file(file_path, progress_cb=lambda p: cb(p, "读取文件..."))
        cb(32, "解密数据...")

        plain_data, orig_ext, used_algo = decrypt_file_content(
            raw, key_str,
            progress_cb=lambda p: cb(32 + p * 0.56, "解密数据..."),
        )
        cb(88, "写入磁盘...")

        out_path = write_decrypted_file(
            plain_data, file_path, orig_ext,
            progress_cb=lambda p: cb(p, "写入磁盘..."),
        )
        cb(100, f"完成: {os.path.basename(out_path)}")
        return out_path, None
    except Exception as e:
        return None, str(e)


def batch_process(file_list, key_str, mode, algo=None, output_ext=".jmdc",
                  overall_progress_cb=None, file_done_cb=None):
    """
    批量处理文件
    :param file_list: 文件路径列表
    :param key_str: 密码
    :param mode: "encrypt" 或 "decrypt"
    :param algo: 加密算法（仅加密时用）
    :param output_ext: 加密输出后缀（仅加密时用）
    :param overall_progress_cb: 总体进度回调 (file_index, total, n_in_file, filename, status)
    :param file_done_cb: 每个文件完成回调 (index, total, path_or_error)
    :return: 成功列表, 失败列表
    """
    success = []
    failures = []
    total = len(file_list)

    for idx, fpath in enumerate(file_list):
        if overall_progress_cb:
            overall_progress_cb(idx, total, 0, fpath, f"[{idx + 1}/{total}] 准备中...")

        def per_file_cb(n, status=""):
            if overall_progress_cb:
                overall_progress_cb(idx, total, n, fpath, status)

        if mode == "encrypt":
            out_path, err = encrypt_one_file(fpath, key_str, algo, output_ext, progress_cb=per_file_cb)
        else:
            out_path, err = decrypt_one_file(fpath, key_str, progress_cb=per_file_cb)

        if err is None:
            success.append((fpath, out_path))
        else:
            failures.append((fpath, err))

        if file_done_cb:
            file_done_cb(idx, total, out_path if err is None else err, err is None)

    return success, failures
