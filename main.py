#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows路径转Linux NAS路径转换工具
功能：自动将Windows路径转换为Linux NAS路径
作者：Sallos
版本：1.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import re
import pyperclip

class PathConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NAS路径转换工具 v1.0")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置主题样式
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="Windows → Linux NAS 路径转换工具", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 输入区域
        input_label = ttk.Label(main_frame, text="输入Windows路径：")
        input_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        # 输入文本框
        self.input_text = scrolledtext.ScrolledText(main_frame, height=8, width=70)
        self.input_text.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=2, sticky=(tk.N, tk.S), padx=(10, 0))
        
        # 转换按钮
        convert_btn = ttk.Button(button_frame, text="转换路径 喵~", command=self.convert_paths)
        convert_btn.pack(pady=(0, 10), fill=tk.X)
        
        # 清空按钮
        clear_btn = ttk.Button(button_frame, text="清空", command=self.clear_all)
        clear_btn.pack(pady=(0, 10), fill=tk.X)
        
        # 复制按钮
        copy_btn = ttk.Button(button_frame, text="复制结果", command=self.copy_result)
        copy_btn.pack(pady=(0, 10), fill=tk.X)
        
        # 输出区域
        output_label = ttk.Label(main_frame, text="转换结果：")
        output_label.grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        
        # 输出文本框
        self.output_text = scrolledtext.ScrolledText(main_frame, height=8, width=70, state=tk.DISABLED)
        self.output_text.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 规则说明
        rules_frame = ttk.LabelFrame(main_frame, text="转换规则", padding="10")
        rules_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        rules_text = (
            "• 盘符移除：去掉盘符，直接转换路径\n"
            "• 路径格式：反斜杠 \\ 转为正斜杠 /\n"
            "• 前缀添加：统一添加 /share 前缀\n"
            "• 字符保留：支持中/英/日/韩等字符\n"
            "• 层级保持：严格保持原路径结构\n"
            "• 支持含空格和特殊符号的路径"
        )
        
        rules_label = ttk.Label(rules_frame, text=rules_text, justify=tk.LEFT)
        rules_label.pack(anchor=tk.W)
        
        # 示例
        example_frame = ttk.LabelFrame(main_frame, text="使用示例", padding="10")
        example_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        example_text = (
            "输入：I:\\git\\nas目录转换工具\n"
            "输出：/share/git/nas目录转换工具\n\n"
            "输入：Z:\\Movies\\动漫\\进击的巨人\\Season 1\n"
            "输出：/share/Movies/动漫/进击的巨人/Season 1"
        )
        
        example_label = ttk.Label(example_frame, text=example_text, justify=tk.LEFT, 
                                 font=('Consolas', 9))
        example_label.pack(anchor=tk.W)
    
    def convert_path(self, windows_path):
        """转换单个Windows路径为Linux NAS路径"""
        if not windows_path.strip():
            return ""
        
        path = windows_path.strip()
        
        # 检查是否为Windows路径格式
        if not re.match(r'^[A-Za-z]:', path):
            return path  # 如果不是Windows路径格式，直接返回
        
        # 移除盘符和冒号，直接获取路径部分
        path_without_drive = path[2:]
        
        # 将反斜杠转换为正斜杠
        linux_path = path_without_drive.replace('\\', '/')
        
        # 直接添加/share前缀，不包含盘符
        final_path = '/share/550E' + linux_path
        
        # 确保路径格式正确，避免双斜杠
        final_path = re.sub(r'/+', '/', final_path)
        
        return final_path
    
    def convert_paths(self):
        """转换所有输入的路径"""
        input_content = self.input_text.get("1.0", tk.END).strip()
        
        if not input_content:
            messagebox.showwarning("警告", "请输入要转换的Windows路径 喵~")
            return
        
        # 按行分割输入
        lines = input_content.split('\n')
        converted_lines = []
        
        for line in lines:
            if line.strip():  # 跳过空行
                converted = self.convert_path(line)
                if converted:
                    converted_lines.append(converted)
        
        # 显示结果
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        
        if converted_lines:
            result = '\n'.join(converted_lines)
            self.output_text.insert("1.0", result)
            
            # 自动复制结果到剪贴板
            try:
                pyperclip.copy(result)
            except Exception as e:
                # 如果pyperclip不可用，使用tkinter的剪贴板
                self.root.clipboard_clear()
                self.root.clipboard_append(result)
        else:
            self.output_text.insert("1.0", "没有找到有效的Windows路径格式")
        
        self.output_text.config(state=tk.DISABLED)
    
    def clear_all(self):
        """清空所有文本框"""
        self.input_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def copy_result(self):
        """复制转换结果到剪贴板"""
        result = self.output_text.get("1.0", tk.END).strip()
        if result:
            try:
                pyperclip.copy(result)
            except Exception as e:
                # 如果pyperclip不可用，使用tkinter的剪贴板
                self.root.clipboard_clear()
                self.root.clipboard_append(result)

def main():
    """主函数"""
    root = tk.Tk()
    app = PathConverterGUI(root)
    
    # 设置窗口图标（如果有的话）
    try:
        # root.iconbitmap('icon.ico')  # 如果有图标文件的话
        pass
    except:
        pass
    
    # 启动GUI
    root.mainloop()

if __name__ == "__main__":
    main()
