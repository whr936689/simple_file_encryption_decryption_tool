"""
文件加密/解密工具 GUI - 支持多文件批量处理 + 多种加密算法
"""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

from crypto_core import (
    ALGO_OFFSET, ALGO_XOR, ALGO_AES256, ALGO_NAMES,
)
from main import batch_process


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # ========= 窗口设置 =========
        self.title("文件加密/解密工具 v2.0")
        self.geometry("780x640")
        self.resizable(False, False)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # 后台线程
        self._worker = None

        # 已选文件列表
        self.file_list = []

        # ========= 背景 =========
        try:
            raw_image = Image.open("background_1.png")
            bg_img = ctk.CTkImage(light_image=raw_image, dark_image=raw_image, size=(780, 640))
            bg_label = ctk.CTkLabel(self, image=bg_img, text="", fg_color="transparent")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception:
            pass

        # ========= 标题 =========
        lab_title = ctk.CTkLabel(
            self,
            text="文件加密 / 解密工具 v2.0",
            font=("Microsoft YaHei", 22, "bold"),
            fg_color="#6c7bb8",
            text_color="white",
            corner_radius=8,
            height=44,
        )
        lab_title.pack(pady=(14, 8), padx=20, fill="x")

        # ========= 密码输入 =========
        frame_key = ctk.CTkFrame(self, fg_color=("#6c7bb8", "#6c7bb8"), corner_radius=10)
        frame_key.pack(pady=6, padx=20, fill="x")

        ctk.CTkLabel(frame_key, text="🔑 密码 / Key：", text_color="white",
                     font=("Microsoft YaHei", 16)).pack(side="left", padx=10, pady=8)

        self.ent_key = ctk.CTkEntry(frame_key, font=("", 14), show="●", height=34)
        self.ent_key.pack(side="left", padx=6, pady=8, fill="x", expand=True)
        self.ent_key.insert(0, "123456")  # 默认密码，方便测试

        self.chk_show = ctk.CTkCheckBox(
            frame_key, text="显示", text_color="white",
            fg_color="#3d4566", hover_color="#5a6794",
            command=self._toggle_password,
        )
        self.chk_show.pack(side="left", padx=10)

        # ========= 模式选择 =========
        frame_mode = ctk.CTkFrame(self, fg_color="#babce0", corner_radius=10)
        frame_mode.pack(pady=6, padx=20, fill="x")

        ctk.CTkLabel(frame_mode, text="模式：", font=("Microsoft YaHei", 14),
                     text_color="#3d4566").pack(side="left", padx=(10, 4), pady=8)

        self.radio_mode = ctk.StringVar(value="encrypt")
        ctk.CTkRadioButton(
            frame_mode, text="加密文件", variable=self.radio_mode, value="encrypt",
            fg_color="#4d5880", hover_color="#3d4566", border_color="#5a6794",
            font=("Microsoft YaHei", 13), command=self._on_mode_change,
        ).pack(side="left", padx=8, pady=8)

        ctk.CTkRadioButton(
            frame_mode, text="解密文件", variable=self.radio_mode, value="decrypt",
            fg_color="#4d5880", hover_color="#3d4566", border_color="#5a6794",
            font=("Microsoft YaHei", 13), command=self._on_mode_change,
        ).pack(side="left", padx=8, pady=8)

        # ========= 算法 + 输出格式 =========
        frame_opts = ctk.CTkFrame(self, fg_color="#babce0", corner_radius=10)
        frame_opts.pack(pady=6, padx=20, fill="x")

        ctk.CTkLabel(frame_opts, text="算法：", font=("Microsoft YaHei", 14),
                     text_color="#3d4566").grid(row=0, column=0, padx=(10, 4), pady=8)

        algo_values = [ALGO_NAMES[ALGO_OFFSET], ALGO_NAMES[ALGO_XOR], ALGO_NAMES[ALGO_AES256]]
        self.cmb_algo = ctk.CTkOptionMenu(
            frame_opts, values=algo_values,
            font=("Microsoft YaHei", 13), height=32,
            fg_color="#6c7bb8", button_color="#4d5880", button_hover_color="#3d4566",
        )
        self.cmb_algo.set(algo_values[0])
        self.cmb_algo.grid(row=0, column=1, padx=4, pady=8)

        ctk.CTkLabel(frame_opts, text="输出后缀：", font=("Microsoft YaHei", 14),
                     text_color="#3d4566").grid(row=0, column=2, padx=(14, 4), pady=8)

        self.cmb_ext = ctk.CTkOptionMenu(
            frame_opts, values=[".jmdc", ".enc", ".encrypted"],
            font=("Microsoft YaHei", 13), height=32,
            fg_color="#6c7bb8", button_color="#4d5880", button_hover_color="#3d4566",
        )
        self.cmb_ext.set(".jmdc")
        self.cmb_ext.grid(row=0, column=3, padx=4, pady=8)

        self._algo_map = {v: k for k, v in ALGO_NAMES.items()}

        # ========= 文件列表 =========
        frame_files = ctk.CTkFrame(self, fg_color="#d1d8f0", corner_radius=10)
        frame_files.pack(pady=6, padx=20, fill="both", expand=True)

        frame_files_header = ctk.CTkFrame(frame_files, fg_color="#d1d8f0")
        frame_files_header.pack(fill="x", padx=10, pady=(8, 2))

        ctk.CTkLabel(frame_files_header, text="📁 待处理文件列表：",
                     font=("Microsoft YaHei", 14, "bold"),
                     text_color="#3d4566").pack(side="left")

        self.lbl_count = ctk.CTkLabel(frame_files_header, text="(0 个)",
                                       font=("Microsoft YaHei", 12),
                                       text_color="#5a6794")
        self.lbl_count.pack(side="right")

        # Listbox（原生 tkinter 组件，ctk 没有 listbox）
        self.listbox = tk.Listbox(
            frame_files, height=8, font=("Consolas", 11),
            bg="#f0f2fa", fg="#3d4566", selectbackground="#6c7bb8",
            activestyle="none", relief="flat", bd=0, highlightthickness=1,
            highlightbackground="#babce0", highlightcolor="#6c7bb8",
        )
        self.listbox.pack(fill="both", expand=True, padx=10, pady=6)

        frame_btns = ctk.CTkFrame(frame_files, fg_color="#d1d8f0")
        frame_btns.pack(fill="x", padx=10, pady=(0, 8))

        self.btn_add = ctk.CTkButton(
            frame_btns, text="➕ 添加文件", font=("Microsoft YaHei", 13),
            fg_color="#6c7bb8", hover_color="#3d4566", height=32,
            command=self._add_files,
        )
        self.btn_add.pack(side="left", padx=4)

        self.btn_remove = ctk.CTkButton(
            frame_btns, text="➖ 移除选中", font=("Microsoft YaHei", 13),
            fg_color="#6c7bb8", hover_color="#3d4566", height=32, width=110,
            command=self._remove_selected,
        )
        self.btn_remove.pack(side="left", padx=4)

        self.btn_clear = ctk.CTkButton(
            frame_btns, text="🗑 清空列表", font=("Microsoft YaHei", 13),
            fg_color="#6c7bb8", hover_color="#3d4566", height=32, width=110,
            command=self._clear_list,
        )
        self.btn_clear.pack(side="left", padx=4)

        # ========= 进度条 + 状态 =========
        frame_progress = ctk.CTkFrame(self, fg_color="#babce0", corner_radius=10)
        frame_progress.pack(pady=6, padx=20, fill="x")

        self.progress_bar = ctk.CTkProgressBar(
            frame_progress, orientation="horizontal",
            progress_color="#8fa0d4", fg_color="#d1d8f0",
            height=20, corner_radius=5,
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=10, pady=(10, 2))

        self.lbl_progress = ctk.CTkLabel(
            frame_progress, text="0%",
            font=("Microsoft YaHei", 12), text_color="#3d4566",
        )
        self.lbl_progress.pack(anchor="w", padx=12)

        self.lbl_status = ctk.CTkLabel(
            frame_progress, text="准备就绪 — 请添加文件并点击「开始处理」",
            font=("Microsoft YaHei", 13), text_color="#4d5880",
        )
        self.lbl_status.pack(anchor="w", padx=12, pady=(0, 10))

        # ========= 开始按钮 =========
        self.btn_start = ctk.CTkButton(
            self, text="🚀 开始处理", font=("Microsoft YaHei", 20, "bold"),
            fg_color="#6c7bb8", hover_color="#3d4566", height=48,
            corner_radius=10, command=self._start,
        )
        self.btn_start.pack(pady=(4, 14), padx=20, fill="x")

        # 初次切换模式（初始化文件过滤器提示）
        self._on_mode_change()

    # =========================================
    # UI 事件处理
    # =========================================
    def _toggle_password(self):
        if self.chk_show.get():
            self.ent_key.configure(show="")
        else:
            self.ent_key.configure(show="●")

    def _on_mode_change(self):
        mode = self.radio_mode.get()
        if mode == "encrypt":
            self.lbl_status.configure(text="加密模式 — 支持任意文件类型")
        else:
            self.lbl_status.configure(text="解密模式 — 仅支持 .jmdc / .enc / .encrypted 文件")

    def _add_files(self):
        mode = self.radio_mode.get()
        if mode == "encrypt":
            filetypes = [("所有文件", "*.*")]
            title = "选择要加密的文件（可多选）"
        else:
            filetypes = [("加密文件", "*.jmdc *.enc *.encrypted"), ("所有文件", "*.*")]
            title = "选择要解密的加密文件（可多选）"

        paths = filedialog.askopenfilenames(title=title, filetypes=filetypes)
        added = 0
        for p in paths:
            if p not in self.file_list:
                self.file_list.append(p)
                self.listbox.insert("end", p)
                added += 1
        if added:
            self.lbl_count.configure(text=f"({len(self.file_list)} 个)")

    def _remove_selected(self):
        sel = self.listbox.curselection()
        for idx in reversed(sel):
            self.listbox.delete(idx)
            del self.file_list[idx]
        self.lbl_count.configure(text=f"({len(self.file_list)} 个)")

    def _clear_list(self):
        self.listbox.delete(0, "end")
        self.file_list.clear()
        self.lbl_count.configure(text="(0 个)")

    def _start(self):
        if self._worker and self._worker.is_alive():
            messagebox.showwarning("提示", "正在处理中，请稍候...")
            return

        if not self.file_list:
            messagebox.showwarning("提示", "请先添加文件！")
            return

        key = self.ent_key.get().strip()
        if not key:
            messagebox.showwarning("提示", "请输入密码！")
            return

        mode = self.radio_mode.get()

        # 禁用按钮
        self.btn_start.configure(state="disabled", text="⏳ 处理中...")
        self.btn_add.configure(state="disabled")
        self.btn_remove.configure(state="disabled")
        self.btn_clear.configure(state="disabled")

        # 重置进度
        self.progress_bar.set(0)
        self.lbl_progress.configure(text="0%")

        algo_name = self.cmb_algo.get()
        algo = self._algo_map.get(algo_name, ALGO_OFFSET)
        ext = self.cmb_ext.get()

        self._worker = threading.Thread(
            target=self._run_batch,
            args=(self.file_list[:], key, mode, algo, ext),
            daemon=True,
        )
        self._worker.start()

    # =========================================
    # 后台处理
    # =========================================
    def _run_batch(self, file_list, key, mode, algo, ext):
        total = len(file_list)

        def overall_cb(idx, total_, n_in_file, fpath, status):
            # 总体进度 = (已完成文件数 + 当前文件进度) / 总文件数
            overall = (idx + n_in_file / 100) / total_ * 100
            self.after(0, self._update_progress, overall, status)

        def done_cb(idx, total_, result, is_ok):
            label = "✅" if is_ok else "❌"
            name = os.path.basename(file_list[idx])
            detail = result if is_ok else result
            self.after(0, self.lbl_status.configure,
                       {"text": f"[{idx + 1}/{total_}] {label} {name} — {detail}"})

        try:
            success, failures = batch_process(
                file_list, key, mode, algo=algo, output_ext=ext,
                overall_progress_cb=overall_cb,
                file_done_cb=done_cb,
            )
            self.after(0, self._on_done, success, failures, mode)
        except Exception as e:
            self.after(0, self._on_error, str(e))

    def _update_progress(self, percent, status):
        self.progress_bar.set(percent / 100)
        self.lbl_progress.configure(text=f"{int(percent)}%")
        if status:
            self.lbl_status.configure(text=status)

    def _on_done(self, success, failures, mode):
        self.btn_start.configure(state="normal", text="🚀 开始处理")
        self.btn_add.configure(state="normal")
        self.btn_remove.configure(state="normal")
        self.btn_clear.configure(state="normal")

        verb = "加密" if mode == "encrypt" else "解密"
        msg = f"处理完成！\n\n✅ 成功：{len(success)} 个\n❌ 失败：{len(failures)} 个"
        if failures:
            msg += "\n\n失败文件："
            for fp, err in failures:
                msg += f"\n  · {os.path.basename(fp)}: {err}"
        messagebox.showinfo("完成", msg)
        self.lbl_status.configure(text=f"全部完成 — 成功 {len(success)}，失败 {len(failures)}")

    def _on_error(self, err):
        self.btn_start.configure(state="normal", text="🚀 开始处理")
        self.btn_add.configure(state="normal")
        self.btn_remove.configure(state="normal")
        self.btn_clear.configure(state="normal")
        self.lbl_status.configure(text=f"出错了：{err}")
        messagebox.showerror("错误", f"处理失败：\n{err}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
