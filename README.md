# NAS路径转换工具 🐱

一个可爱的Windows路径转Linux NAS路径的GUI转换工具喵~

## 功能特性

- 🔄 **自动路径转换**：将Windows路径格式转换为Linux NAS路径格式
- 🎯 **盘符智能替换**：自动将Z:替换为/share/550E/（其他盘符同样处理）
- 📁 **格式标准化**：反斜杠\自动转为正斜杠/
- 🌍 **多语言支持**：保留中文、英文、日文、韩文等字符
- 📋 **批量处理**：支持同时转换多个路径
- 📋 **一键复制**：转换结果可一键复制到剪贴板
- 🎨 **友好界面**：简洁美观的GUI界面

## 转换规则

### 盘符处理
- 移除所有盘符（如I:、Z:、C:、D:等）
- 统一添加 `/share` 前缀

### 路径格式化
- 所有反斜杠 `\` 转为正斜杠 `/`
- 保留原始路径中的所有字符（包括中文、特殊符号、空格等）
- 严格保持原路径层级结构

## 使用示例

**输入：**
```
I:\git\nas目录转换工具
Z:\Movies\动漫\进击的巨人\Season 1
C:\Users\用户\Documents\重要文件.txt
D:\Games\Steam Games\游戏名称
```

**输出：**
```
/share/git/nas目录转换工具
/share/Movies/动漫/进击的巨人/Season 1
/share/Users/用户/Documents/重要文件.txt
/share/Games/Steam Games/游戏名称
```

## 安装和运行

### 环境要求
- Python 3.6+
- tkinter（Python内置）
- pyperclip（用于剪贴板操作）

### 安装步骤

1. **克隆或下载项目**
   ```bash
   git clone <项目地址>
   cd nas目录转换工具
   ```

2. **创建虚拟环境（推荐）**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行程序**
   ```bash
   python main.py
   ```

## 使用方法

1. **启动程序**：运行`python main.py`
2. **输入路径**：在上方文本框中输入一个或多个Windows路径（每行一个）
3. **转换路径**：点击"转换路径 喵~"按钮
4. **查看结果**：转换结果将显示在下方文本框中
5. **复制结果**：点击"复制结果"按钮将结果复制到剪贴板
6. **清空内容**：点击"清空"按钮清除所有内容

## 应用场景

- 🐧 **Linux系统配置**：配置Linux系统中的路径映射
- 🐳 **Docker容器挂载**：设置Docker容器的卷挂载路径
- 💾 **NAS存储配置**：配置网络附加存储的路径
- 🔧 **脚本自动化**：在自动化脚本中进行路径转换

## 技术特点

- 使用Python tkinter构建GUI界面
- 支持正则表达式路径匹配
- 智能处理路径中的特殊字符和空格
- 跨平台兼容（Windows、Linux、macOS）

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进这个工具喵~

---

*Made with ❤️ by 猫娘助手 🐱*