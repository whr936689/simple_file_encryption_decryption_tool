# 文件加密 / 解密工具

一个用 Python + CustomTkinter 写的简洁文件加密工具，支持**多文件批量处理**和**多种加密算法**。

## ✨ 功能特性

- 🔐 **三种加密算法** 可选：
  - **字节偏移** — 最简单的加法偏移，兼容旧版 `.jmdc` 文件
  - **XOR 循环异或** — 轻量对称加密，速度快
  - **AES-256-CBC** — 标准安全加密，推荐用于敏感文件
- 📂 **批量处理** — 一次选多个文件，一键加密/解密
- 🔄 **自动格式识别** — 解密时自动识别文件使用的算法
- 🔙 **向后兼容** — 能正常解密旧版（v0.1 / v0.3）生成的 `.jmdc` 文件
- 🎨 **CustomTkinter 现代化界面** — 进度条、状态提示、密码显示切换
- 📁 **智能输出** — 自动保留原始扩展名，自动防覆盖（同名加 `_1` 后缀）

## 📷 截图

> 界面改版中，稍后更新

## 🚀 快速开始

### 下载 Release

直接去 [Releases](../../releases) 下载最新版 `加密解密工具-windows.zip`，解压双击 `文件加密解密工具.exe` 即可使用。

### 从源码运行

```bash
# 克隆项目
git clone https://github.com/whr936689/simple_file_encryption_decryption_tool.git
cd simple_file_encryption_decryption_tool

# 安装依赖
pip install pycryptodome customtkinter pillow

# 运行
python gui_version.py
```

### 打包为 exe

```bash
pip install pyinstaller
pyinstaller --noconfirm --windowed --onefile \
  --name "文件加密解密工具" \
  --add-data "background_1.png;." \
  gui_version.py
```

## 📖 使用方法

### 加密文件

1. 在「密码」框输入加密密码（AES 模式下建议 8 位以上）
2. 选择「加密文件」模式
3. 选择加密算法（建议敏感文件用 AES-256-CBC）
4. 选择输出后缀（默认 `.jmdc`）
5. 点击 **➕ 添加文件** 选择要加密的文件（可多选）
6. 点击 **🚀 开始处理**

加密完成后，原文件旁边会生成一个 `.jmdc` 文件。

### 解密文件

1. 在「密码」框输入加密时用的密码
2. 切换到「解密文件」模式
3. 选择 `.jmdc` / `.enc` 文件（可多选）
4. 点击 **🚀 开始处理**

解密时会自动识别使用的算法，不需要手动选择。

## 🔑 加密算法说明

| 算法 | 强度 | 速度 | 说明 |
|------|------|------|------|
| 字节偏移 | ⭐ | ⭐⭐⭐⭐⭐ | 最简单，兼容性好，**不要用于敏感数据** |
| XOR 循环 | ⭐⭐ | ⭐⭐⭐⭐ | 对称加密，密码越长越安全 |
| AES-256-CBC | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 工业标准，带随机 IV，安全性最高 |

### 文件格式

**新格式（JMD1 魔数）**
```
[4字节魔数 "JMD1"][2字节算法号][4字节扩展名长度][N字节扩展名][加密数据体]
```

**旧格式（兼容读取）**
```
[4字节扩展名长度][N字节扩展名][offset加密数据体]
```

> 新版加密时始终使用新格式，解密时自动识别新旧格式。

## 📁 项目结构

```
simple_file_encryption_decryption_tool/
├── gui_version.py      # 主程序入口（GUI）
├── crypto_core.py      # 加密核心（三种算法 + 格式处理）
├── main.py             # 业务逻辑（单文件/批量处理）
├── file_cz.py          # 文件读写工具
├── file_open.py        # 文件选择对话框（旧版，保留参考）
├── background_1.png    # GUI 背景图
└── README.md
```

## ⚠️ 注意事项

- 加密密码**请妥善保管**，丢失后无法找回
- AES 模式下密码建议 8 位以上，越复杂越安全
- 加密大文件时请耐心等待，进度条会实时更新
- 旧版 `.jmdc` 文件仅兼容「字节偏移」算法

## 📄 License

MIT License
