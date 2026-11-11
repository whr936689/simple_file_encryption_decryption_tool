"""
文件读写工具模块
"""

import os


def read_file(file_path, progress_cb=None):
    """
    分块读取整个文件
    :param file_path: 文件路径
    :param progress_cb: 进度回调 (0-30)
    """
    file_size = os.path.getsize(file_path)
    chunk_size = 1024 * 1024  # 1MB
    data = bytearray()

    if file_size == 0:
        return bytes(data)

    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            data.extend(chunk)
            if progress_cb:
                percent = (len(data) / file_size) * 30
                progress_cb(percent)

    return bytes(data)


def write_encrypted_file(data, source_path, output_ext=".jmdc", progress_cb=None):
    """
    把加密后的数据写到磁盘
    :param data: 加密后的完整数据（含头部）
    :param source_path: 原始文件路径（用它来推断输出路径）
    :param output_ext: 输出扩展名，默认 .jmdc
    :param progress_cb: 进度回调 (70-100)
    :return: 实际写入的文件路径
    """
    if not output_ext.startswith('.'):
        output_ext = '.' + output_ext
    save_path = os.path.splitext(source_path)[0] + output_ext

    total_size = len(data)
    chunk_size = 1024 * 1024
    written = 0

    # 防止覆盖：如果文件已存在，加数字后缀
    counter = 1
    final_path = save_path
    while os.path.exists(final_path):
        stem = os.path.splitext(save_path)[0]
        final_path = f"{stem}_{counter}{output_ext}"
        counter += 1

    with open(final_path, "wb") as f:
        for i in range(0, total_size, chunk_size):
            chunk = data[i:i + chunk_size]
            f.write(chunk)
            written += len(chunk)
            if progress_cb:
                percent = 70 + (written / total_size * 30)
                progress_cb(percent)

    return final_path


def write_decrypted_file(data, source_path, orig_ext, progress_cb=None):
    """
    把解密后的数据写到磁盘，还原原始扩展名
    :param data: 解密后的原始数据
    :param source_path: 加密文件路径
    :param orig_ext: 原始扩展名（如 '.txt'）
    :param progress_cb: 进度回调 (70-100)
    :return: 实际写入的文件路径
    """
    # 推断输出路径：去掉加密后缀，加回原始扩展名
    base = source_path
    # 如果源文件以 .jmdc 或 .enc 结尾，去掉那个后缀
    for enc_suffix in ['.jmdc', '.enc', '.encrypted']:
        if base.lower().endswith(enc_suffix):
            base = base[:-len(enc_suffix)]
            break

    # 去掉可能残留的尾部点
    base = base.rstrip('.')
    save_path = base + orig_ext

    total_size = len(data)
    chunk_size = 1024 * 1024
    written = 0

    # 防止覆盖
    counter = 1
    final_path = save_path
    while os.path.exists(final_path):
        stem = os.path.splitext(save_path)[0]
        final_path = f"{stem}_{counter}{orig_ext}"
        counter += 1

    with open(final_path, "wb") as f:
        for i in range(0, total_size, chunk_size):
            chunk = data[i:i + chunk_size]
            f.write(chunk)
            written += len(chunk)
            if progress_cb:
                percent = 70 + (written / total_size * 30)
                progress_cb(percent)

    return final_path
