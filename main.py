def mainLG(keyd,modes,locas,sx_proc=None):
    from jiami_jiemi import FileProtector
    from file_cz import cz_bin,cz_save_bin
    import struct
    import os
    mode=modes
    key=keyd
    jm=FileProtector(key)
    if mode==1:
        print(jm.jiami(input("源字符串：")))
    if mode==2:
        print(jm.jiemi(input("源字符串：")))
    if mode==3:
        loca=locas
        text=cz_bin(loca,jd_sh=lambda n: sx_proc(n, "正在读取文件喵..."))   #文件转字节流，读取文件的进度显示喵
        file_ext = os.path.splitext(loca)[1].encode('utf-8')  #获取后缀并转字节,encode表示转字节流,前面负责提取拓展名
        ext_len = struct.pack('I', len(file_ext))
        text=ext_len+file_ext+text  #合并拓展名长度和原拓展名和字节流喵
        text=jm.jiami(text,process_callback=lambda n: sx_proc(n, "正在加密数据喵...")) #字节流加密
        #print(text)
        cz_save_bin(text,loca,True,file_ext,jd_sh=lambda n: sx_proc(n, "正在写入磁盘喵..."))   #写入加密后文件
    if mode==4:
        loca=locas
        text=cz_bin(loca,jd_sh=lambda n: sx_proc(n, "正在读取文件喵..."))
        text=jm.jiemi(text,process_callback=lambda n: sx_proc(n, "正在解密数据喵..."))
        ext_len_bytes=text[:4]
        ext_len=struct.unpack('I', ext_len_bytes)[0]    #拓展名长度
        file_ext = text[4: 4 + ext_len].decode('utf-8') #文件拓展名
        real_text = text[4 + ext_len:]         #真实源文件的字节流
        cz_save_bin(real_text,loca,False,file_ext,jd_sh=lambda n: sx_proc(n, "正在导出原始文件喵..."))##写入解密后文件