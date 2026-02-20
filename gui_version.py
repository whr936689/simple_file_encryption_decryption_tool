import tkinter as tk
from process import process
from tkinter import filedialog
import os
from file_open import select_file
from tkinter import ttk #为导入进度条做准备
import customtkinter
#def callback():
#    print("你点了一下按钮")
root=tk.Tk()    #创建窗口
root.title("文件解密/解密工具ver0.1")
root.geometry("600x400")
root.resizable(False, False)
try:
    bg_img=tk.PhotoImage(file="background_1.png")
    bg_label=tk.Label(root, image=bg_img)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    root.bg_img=bg_img # 这里的引用非常重要喵！
except:
    print("背景图加载失败，请检查文件名和路径喵~")
lab_1=tk.Label(root,text="文件解密/解密工具ver0.1",relief="solid",cursor="hand2",font=("UniSun", 20))
lab_1.bind("<Button-1>",lambda e: root.destroy())
lab_1.pack(pady=10)
# 创建一个StringVar变量以存储单选按钮的值
radio_var = tk.StringVar()
radio_var.set("3")  #默认为3加密文件
grid_frame_Key=tk.Frame(root)
grid_frame_Key.pack(pady=10)
Label_Key=tk.Label(grid_frame_Key,text="密钥/Key:",font=("UniSun",15)).grid(row=0, column=0)
Ent1=tk.Entry(grid_frame_Key,font=("",20))   #密钥
Ent1.grid(row=0, column=1)
grid_frame_Loca=tk.Frame(root)
grid_frame_Loca.pack(pady=10)
Label_Loca=tk.Label(grid_frame_Loca,text="文件路径/Location:",font=("UniSun",15)).grid(row=0, column=0)
Ent2=tk.Entry(grid_frame_Loca,font=("",20))    #路径
Ent2.grid(row=0, column=1)
btn_cfile=tk.Button(grid_frame_Loca,text="打开文件",command=lambda:select_file(Ent2,radio_var.get()))
btn_cfile.grid(row=0, column=2)
btn1=tk.Button(root,font=("UniSun",20),text="start",command=lambda:process(int(Ent1.get()),radio_var.get(),Ent2.get(),update_p))   #实现方法1，后面懒得写
btn1.pack(pady=10)
# 创建单选按钮
grid_frame=tk.Frame(root)
grid_frame.pack(pady=10)
radio_button1 = tk.Radiobutton(grid_frame, text="加密",font=("UniSun",15), variable=radio_var, value="3").grid(row=0, column=0)
radio_button2 = tk.Radiobutton(grid_frame, text="解密",font=("UniSun",15), variable=radio_var, value="4").grid(row=0, column=1)
#radio_button1.pack()
#radio_button2.pack()
#image = tkinter.PhotoImage(file="图片文件路径")
grid_frame_bar=tk.Frame(root)
grid_frame_bar.pack(pady=10)
progress_bar = ttk.Progressbar(grid_frame_bar, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=0,column=0) # 把它擺在介面上
progress_bar["maximum"] = 100
label_proc=tk.Label(grid_frame_bar,text="0%",font=("UniSun",15),width=5)
label_proc.grid(row=0,column=1)
label_status = tk.Label(grid_frame_bar, text="准备就绪喵...", font=("UniSun", 12), fg="blue")
label_status.grid(row=1, column=0, columnspan=2, pady=5)    #状态标识
def update_p(n,status="处理中..."):    #更新进度原点在这里
    progress_bar['value']=n
    label_proc.config(text=str(int(n))+"%")
    label_status.config(text=status)
    root.update()
    root.update_idletasks()
root.mainloop()
