#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows路径转Linux NAS路径转换工具 - PyQt版本
功能：自动将Windows路径转换为Linux NAS路径
作者：Sallos
"""

# 版本信息
VERSION = "1.0.0"

import sys
import re
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QGroupBox, QMessageBox,
    QSplitter, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

try:
    import pyperclip
except ImportError:
    pyperclip = None

class PathConverterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"NAS路径转换工具 v{VERSION}")
        self.setGeometry(100, 100, 900, 700)
        
        # 配置文件路径
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        
        # 加载配置
        self.load_config()
        
        # 设置界面
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("Windows → Linux NAS 路径转换工具")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # 创建分割器
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # 输入区域
        input_group = QGroupBox("输入Windows路径")
        input_group.setFont(QFont("Arial", 10, QFont.Bold))
        input_layout = QVBoxLayout(input_group)
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("请输入要转换的Windows路径，支持多行输入...\n\n示例：\nI:\\git\\nas目录转换工具\nZ:\\Movies\\动漫\\进击的巨人\\Season 1")
        self.input_text.setFont(QFont("Consolas", 10))
        self.input_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px;
                background-color: #ffffff;
                selection-background-color: #3498db;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        input_layout.addWidget(self.input_text)
        
        splitter.addWidget(input_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # 转换按钮
        self.convert_btn = QPushButton("🔄 转换路径")
        self.convert_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.convert_btn.setMinimumHeight(50)
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 1.5% 3%;
                border-radius: 8px;
                font-size: 12px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.convert_btn.clicked.connect(self.convert_paths)
        button_layout.addWidget(self.convert_btn)
        
        # 清空按钮
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.clear_btn.setMinimumHeight(50)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 1.5% 3%;
                border-radius: 8px;
                font-size: 12px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_btn)
        
        # 复制按钮
        self.copy_btn = QPushButton("📋 复制结果")
        self.copy_btn.setFont(QFont("Arial", 10, QFont.Bold))
        self.copy_btn.setMinimumHeight(50)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 1.5% 3%;
                border-radius: 8px;
                font-size: 12px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.copy_btn.clicked.connect(self.copy_result)
        button_layout.addWidget(self.copy_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # 输出区域
        output_group = QGroupBox("转换结果")
        output_group.setFont(QFont("Arial", 10, QFont.Bold))
        output_layout = QVBoxLayout(output_group)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("转换结果将显示在这里...")
        self.output_text.setFont(QFont("Consolas", 10))
        self.output_text.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px;
                background-color: #f8f9fa;
                selection-background-color: #3498db;
            }
        """)
        output_layout.addWidget(self.output_text)
        
        splitter.addWidget(output_group)
        
        # 设置分割器比例
        splitter.setSizes([300, 300])
        
        # 规则说明区域
        rules_group = QGroupBox("转换规则")
        rules_group.setFont(QFont("Arial", 9, QFont.Bold))
        rules_layout = QVBoxLayout(rules_group)
        
        rules_text = (
            "• 盘符移除：去掉盘符，直接转换路径\n"
            "• 路径格式：反斜杠 \\ 转为正斜杠 /\n"
            "• 前缀添加：统一添加 /share 前缀\n"
            "• 字符保留：支持中/英/日/韩等字符\n"
            "• 层级保持：严格保持原路径结构\n"
            "• 支持含空格和特殊符号的路径"
        )
        
        rules_label = QLabel(rules_text)
        rules_label.setFont(QFont("Arial", 9))
        rules_label.setStyleSheet("""
            QLabel {
                color: #34495e;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border-left: 4px solid #3498db;
            }
        """)
        rules_layout.addWidget(rules_label)
        
        main_layout.addWidget(rules_group)
        
        # 示例区域
        example_group = QGroupBox("使用示例")
        example_group.setFont(QFont("Arial", 9, QFont.Bold))
        example_layout = QVBoxLayout(example_group)
        
        example_text = (
            "输入：I:\\git\\nas目录转换工具\n"
            "输出：/share/git/nas目录转换工具\n\n"
            "输入：Z:\\Movies\\动漫\\进击的巨人\\Season 1\n"
            "输出：/share/Movies/动漫/进击的巨人/Season 1"
        )
        
        example_label = QLabel(example_text)
        example_label.setFont(QFont("Consolas", 9))
        example_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 6px;
                border-left: 4px solid #27ae60;
            }
        """)
        example_layout.addWidget(example_label)
        
        main_layout.addWidget(example_group)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
            }
        """)
    
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
        
        # 添加自定义前缀
        final_path = self.nas_prefix + linux_path
        
        # 确保路径格式正确，避免双斜杠
        final_path = re.sub(r'/+', '/', final_path)
        
        return final_path
    
    def convert_paths(self):
        """转换所有输入的路径"""
        input_content = self.input_text.toPlainText().strip()
        
        if not input_content:
            QMessageBox.warning(self, "警告", "请输入要转换的Windows路径")
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
        if converted_lines:
            result = '\n'.join(converted_lines)
            self.output_text.setPlainText(result)
            
            # 自动复制结果到剪贴板
            self.copy_to_clipboard(result)
        else:
            self.output_text.setPlainText("没有找到有效的Windows路径格式")
    
    def clear_all(self):
        """清空所有文本框"""
        self.input_text.clear()
        self.output_text.clear()
    
    def copy_result(self):
        """复制转换结果到剪贴板"""
        result = self.output_text.toPlainText().strip()
        if result:
            self.copy_to_clipboard(result)
            QMessageBox.information(self, "提示", "结果已复制到剪贴板")
        else:
            QMessageBox.warning(self, "警告", "没有可复制的内容")
    
    def copy_to_clipboard(self, text):
        """复制文本到剪贴板"""
        try:
            if pyperclip:
                pyperclip.copy(text)
            else:
                # 使用PyQt的剪贴板
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"复制到剪贴板失败：{str(e)}")
    
    def load_config(self):
        """加载配置文件"""
        default_config = {
            "nas_prefix": "/share"
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.nas_prefix = config.get('nas_prefix', default_config['nas_prefix'])
            else:
                # 创建默认配置文件
                self.nas_prefix = default_config['nas_prefix']
                self.save_config(default_config)
        except Exception as e:
            # 如果配置文件损坏，使用默认配置并重新创建文件
            self.nas_prefix = default_config['nas_prefix']
            self.save_config(default_config)
    
    def save_config(self, config):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置文件失败：{str(e)}")

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("NAS路径转换工具")
    app.setApplicationVersion(VERSION)
    app.setOrganizationName("Sallos")
    
    # 创建主窗口
    window = PathConverterGUI()
    window.show()
    
    # 启动应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()