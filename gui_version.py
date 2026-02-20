import tkinter as tk
from process import process
from tkinter import filedialog
import os
from file_open import select_file
from tkinter import ttk #为导入进度条做准备
import customtkinter as ctk
from PIL import Image
#def callback():
#    print("你点了一下按钮")
root=ctk.CTk()    #创建窗口
root.title("文件解密/解密工具ver0.1_with_ctk")
root.geometry("600x400")
root.resizable(False, False)
try:
    raw_image = Image.open("background_1.png")
    bg_img = ctk.CTkImage(light_image=raw_image, dark_image=raw_image, size=(600, 400))
    bg_label = ctk.CTkLabel(root, image=bg_img, text="", fg_color="transparent")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    #root.bg_img=bg_img # 这里的引用非常重要喵！
except:
    print("背景图加载失败，请检查文件名和路径喵~")
lab_1=ctk.CTkLabel(root,text="文件解密/解密工具ver0.1_with_ctk",cursor="hand2",font=("UniSun", 25),fg_color="#6c7bb8",text_color="white")
lab_1.bind("<Button-1>",lambda e: root.destroy())
lab_1.pack(pady=10)
# 创建一个StringVar变量以存储单选按钮的值
radio_var = ctk.StringVar()
radio_var.set("3")  #默认为3加密文件
grid_frame_Key=ctk.CTkFrame(root,fg_color=("#6c7bb8", "#6c7bb8"))
grid_frame_Key.pack(pady=10)
Label_Key=ctk.CTkLabel(grid_frame_Key,text="密钥/Key:",text_color="white",font=("UniSun",20)).grid(row=0, column=0)
Ent1=ctk.CTkEntry(grid_frame_Key,font=("",20),width=400)   #密钥
Ent1.grid(row=0, column=1)
grid_frame_Loca=ctk.CTkFrame(root,fg_color=("#6c7bb8", "#6c7bb8"))
grid_frame_Loca.pack(pady=10)
Label_Loca=ctk.CTkLabel(grid_frame_Loca,text="文件路径/Location:",text_color="white",font=("UniSun",20)).grid(row=0, column=0)
Ent2=ctk.CTkEntry(grid_frame_Loca,font=("",20),width=280)    #路径
Ent2.grid(row=0, column=1)
btn_cfile=ctk.CTkButton(grid_frame_Loca,text="打开文件",font=("UniSun",20),fg_color="#6c7bb8",hover_color="#3d4566",command=lambda:select_file(Ent2,radio_var.get()))
btn_cfile.grid(row=0, column=2)
btn1=ctk.CTkButton(root,font=("UniSun",30),text="start",height=50,fg_color="#6c7bb8",hover_color="#3d4566",command=lambda:process(int(Ent1.get()),radio_var.get(),Ent2.get(),update_p))   #实现方法1，后面懒得写
btn1.pack(pady=10)
# 创建单选按钮
grid_frame=ctk.CTkFrame(root)
grid_frame.pack(pady=10)
radio_button1 = ctk.CTkRadioButton(grid_frame, text="加密",font=("UniSun",20), variable=radio_var, value="3").grid(row=0, column=0)
radio_button2 = ctk.CTkRadioButton(grid_frame, text="解密",font=("UniSun",20), variable=radio_var, value="4").grid(row=0, column=1)
#radio_button1.pack()
#radio_button2.pack()
#image = tkinter.PhotoImage(file="图片文件路径")
grid_frame_bar=ctk.CTkFrame(root,fg_color=("#babce0", "#babce0"))#进度条父系方块
grid_frame_bar.pack(pady=10)
progress_bar = ctk.CTkProgressBar(
    grid_frame_bar,
    orientation="horizontal",
    width=500,       # 宽度（原来的 length）
    height=20,      # <--- 调这个数字，进度条就变胖了！
    corner_radius=5,  # 给进度条也来点圆角
    # 设置进度条颜色（比如用个好看的深紫色）
    progress_color="#8fa0d4",
    # 设置背景槽颜色（我们可以设为透明，或者比背景深一点点）
    fg_color="#d1d8f0"
)
# 别忘了初始值！ctk 的进度条默认是 0.5（一半），记得设为 0
progress_bar.set(0)
#progress_bar = ctk.CTkProgressBar(grid_frame_bar, orient="horizontal", length=800, mode="determinate")
progress_bar.grid(row=0,column=0) # 把它擺在介面上
progress_bar["maximum"] = 100
label_proc=ctk.CTkLabel(grid_frame_bar,text="0%",font=("UniSun",20),width=5)
label_proc.grid(row=0,column=1)
label_status = ctk.CTkLabel(grid_frame_bar, text="准备就绪喵...", font=("UniSun", 20), text_color="blue")
label_status.grid(row=1, column=0, columnspan=2, pady=5)    #状态标识
def update_p(n,status="处理中..."):    #更新进度原点在这里
    #progress_bar['value']=n/100
    progress_bar.set(n / 100)
    label_proc.configure(text=str(int(n))+"%")
    label_status.configure(text=status,font=("UniSun", 20))
    root.update()
    root.update_idletasks()
root.mainloop()
