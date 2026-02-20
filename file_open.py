import os
from tkinter import filedialog
import tkinter as tk
def select_file(filename_process,mode_val):
    # 第一步：打开“文件选择窗口”
    if mode_val=="3":
        file_path = filedialog.askopenfilename(
            title="选择要加密的文件",
            filetypes=[("所有文件", "*.*")]
        )
    if mode_val=="4":
        file_path = filedialog.askopenfilename(
            title="请选择 .jmdc 格式的解密文件",
            filetypes=[("加密文件", "*.jmdc")]
        )
    #print("验证:",file_path)
    if file_path:
        filename_process.delete(0, tk.END)  # 清空输入框旧内容
        filename_process.insert(0, file_path)  # 填入新路径