from main import mainLG
from tkinter import messagebox
def process(key,mode,File_location,proc_ch):
    mainLG(key,int(mode),File_location,proc_ch)
    if(mode=="3"):
        messagebox.showinfo("提示", "文件加密成功啦喵！")
    if(mode=="4"):
        messagebox.showinfo("提示", "文件解密成功啦喵！")