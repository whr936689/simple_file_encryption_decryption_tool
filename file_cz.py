import os
def cz_bin(file_foca,jd_sh=None):
    file_size = os.path.getsize(file_foca)
    chunk_size=1024*1024
    with open(file_foca,"rb") as f:     #打开文件
        texta = bytearray()
        while True:  # 无限循环
            chunk=f.read(chunk_size)  #每次读1MB=1024^2Byte
            if not chunk:
                break
            texta.extend(chunk)     #细嚼慢咽这一块
            if jd_sh:
                percent=(len(texta)/file_size)*30
                jd_sh(percent)
    return texta     #返回字节流


def cz_save_bin(textb, file_foca, dec, type_ext, jd_sh=None):
    #先在外面确定好到底存到哪个路径
    if dec:
        save_path = os.path.splitext(file_foca)[0] + ".jmdc"
    else:
        save_path = os.path.splitext(file_foca)[0] + type_ext

    total_size = len(textb)
    chunk_size = 1024 * 1024
    written_size = 0
    with open(save_path, "wb") as f:
        for i in range(0, total_size, chunk_size):
            chunk = textb[i: i + chunk_size]
            f.write(chunk)
            written_size += len(chunk)
            if jd_sh:
                percent = 70 + (written_size / total_size * 30)
                jd_sh(percent)
    #jd_sh(100,"文件已写入完成喵！")
    print("写入动作已执行喵！")