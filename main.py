#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows路径转Linux NAS路径转换工具 - PyQt版本
功能：自动将Windows路径转换为Linux NAS路径
作者：Sallos
"""

# 版本信息
VERSION = "2.0.0"

import sys
import re
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QGroupBox, QMessageBox,
    QSplitter, QFrame, QToolButton, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QFontMetrics

try:
    import pyperclip
except ImportError:
    pyperclip = None

class CollapsibleGroupBox(QGroupBox):
    """可折叠的GroupBox"""
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setCheckable(True)
        self.setChecked(False)  # 默认折叠
        self.toggled.connect(self.on_toggled)
        self.main_window = None  # 用于引用主窗口
        
    def set_main_window(self, main_window):
        """设置主窗口引用"""
        self.main_window = main_window
        
    def on_toggled(self, checked):
        """切换显示/隐藏内容"""
        # 输出点击时的当前窗口大小
        if self.main_window:
            current_size = self.main_window.size()
            print(f"[调试] 点击帮助信息按钮 - 状态: {'展开' if checked else '收起'}, 当前窗口大小: {current_size.width()} x {current_size.height()}")
        
        # 控制窗口大小 - 在改变内容可见性之前处理
        if self.main_window:
            if checked:  # 即将展开
                if not self.main_window.help_expanded:
                    # 记录当前窗口大小（展开前的大小）
                    self.main_window.initial_size = self.main_window.size()
                    self.main_window.help_expanded = True
                    print(f"[调试] 帮助信息即将展开，记录当前窗口大小: {self.main_window.initial_size.width()} x {self.main_window.initial_size.height()}")
            else:  # 即将收起
                if self.main_window.help_expanded:
                    print(f"[调试] 帮助信息即将收起，当前窗口大小: {self.main_window.size().width()} x {self.main_window.size().height()}")
        
        # 切换子部件可见性
        for child in self.findChildren(QWidget):
            if child != self:
                child.setVisible(checked)
        
        # 在内容变化后调整窗口大小
        if self.main_window:
            if not checked:  # 收起后
                if self.main_window.help_expanded and self.main_window.initial_size:
                    # 恢复到展开前记录的窗口大小
                    target_width = self.main_window.initial_size.width()
                    target_height = self.main_window.initial_size.height()
                    print(f"[调试] 准备恢复到展开前的窗口大小: {target_width} x {target_height}")
                    
                    # 先设置为固定大小
                    self.main_window.setFixedSize(target_width, target_height)
                    print(f"[调试] 设置固定大小后窗口大小: {self.main_window.size().width()} x {self.main_window.size().height()}")
                    
                    # 立即恢复为可调整大小
                    self.main_window.setMinimumSize(0, 0)
                    self.main_window.setMaximumSize(16777215, 16777215)  # PyQt的最大值
                    
                    self.main_window.help_expanded = False
                    
                    # 检查最终大小
                    final_size = self.main_window.size()
                    print(f"[调试] 帮助信息已收起，最终窗口大小: {final_size.width()} x {final_size.height()}")
    
    def showEvent(self, event):
        """重写showEvent确保初始状态正确"""
        super().showEvent(event)
        # 确保初始状态下内容被隐藏
        if not self.isChecked():
            for child in self.findChildren(QWidget):
                if child != self:
                    child.setVisible(False)

class PathConverterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"NAS路径转换工具 v{VERSION}")
        
        # 获取DPI缩放比例
        self.dpi_scale = self.get_dpi_scale()
        print(f"[调试] DPI缩放比例: {self.dpi_scale}")
        
        # 设置窗口几何
        target_width = self.scale_size(1198)
        target_height = self.scale_size(1046)
        self.setGeometry(100, 100, target_width, target_height)
        print(f"[调试] 设置窗口几何: 位置(100, 100), 目标大小({self.scale_size(1198)} x {self.scale_size(1046)}), 实际设置({target_width} x {target_height})")
        
        # 初始化状态变量
        self.help_expanded = False
        self.initial_size = None
        
        # 配置文件路径
        self.config_file = "config.json"
        
        # 加载配置
        self.load_config()
        
        # 设置UI
        self.setup_ui()
    
    def apply_saved_window_state(self):
        """应用保存的窗口状态"""
        try:
            # 应用保存的帮助信息状态（先设置状态，再调整窗口大小）
            if hasattr(self, 'saved_help_expanded') and self.saved_help_expanded:
                # 如果保存时帮助信息是展开的，则展开它
                if hasattr(self, 'help_group'):
                    self.help_group.setChecked(True)
                    self.help_expanded = True
                    print(f"[调试] 应用保存的帮助信息状态: 展开")
            else:
                # 确保帮助信息是收起的
                if hasattr(self, 'help_group'):
                    self.help_group.setChecked(False)
                    self.help_expanded = False
                    print(f"[调试] 应用保存的帮助信息状态: 收起")
            
            # 强制处理所有待处理的事件
            QApplication.processEvents()
            
            # 应用保存的窗口大小（在状态设置后）
            if hasattr(self, 'saved_window_width') and hasattr(self, 'saved_window_height'):
                self.resize(self.saved_window_width, self.saved_window_height)
                print(f"[调试] 应用保存的窗口大小: {self.saved_window_width}x{self.saved_window_height}")
                
                # 再次强制处理事件并检查最终大小
                QApplication.processEvents()
                final_size = self.size()
                print(f"[调试] 最终窗口大小: {final_size.width()}x{final_size.height()}")
                
        except Exception as e:
            print(f"[调试] 应用保存的窗口状态时出错: {e}")
    
    def get_dpi_scale(self):
        """获取DPI缩放比例"""
        app = QApplication.instance()
        if app:
            screen = app.primaryScreen()
            dpi = screen.logicalDotsPerInch()
            # 标准DPI为96，计算缩放比例
            scale = dpi / 96.0
            return max(1.0, min(scale, 3.0))  # 限制在1.0-3.0之间
        return 1.0
    
    def scale_font_size(self, base_size):
        """根据DPI缩放字体大小"""
        return int(base_size * self.dpi_scale * 0.6)  # 缩小25%
    
    def scale_size(self, base_size):
        """根据DPI缩放尺寸"""
        return int(base_size * self.dpi_scale)
    
    def scale_button_size(self, base_size):
        """根据字体大小缩放按钮尺寸"""
        return int(base_size * self.dpi_scale * 0.6)  # 与字体保持相同的缩放比例
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局 - 垂直布局包含标题和内容区域
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(self.scale_size(15))
        main_layout.setContentsMargins(self.scale_size(20), self.scale_size(20), 
                                     self.scale_size(20), self.scale_size(20))
        
        # 标题
        title_label = QLabel("Windows → Linux NAS 路径转换工具")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", self.scale_font_size(16), QFont.Bold))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: #2c3e50;
                padding: {self.scale_size(10)}px;
                background-color: #ecf0f1;
                border-radius: {self.scale_size(8)}px;
                margin-bottom: {self.scale_size(10)}px;
            }}
        """)
        main_layout.addWidget(title_label)
        
        # 内容区域 - 水平布局分为左右两列
        content_layout = QHBoxLayout()
        content_layout.setSpacing(self.scale_size(20))
        
        # 左侧区域 - 输入输出和提示
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(self.scale_size(15))
        
        # 输入区域
        input_group = QGroupBox("输入Windows路径")
        input_group.setFont(QFont("Arial", self.scale_font_size(10), QFont.Bold))
        input_layout = QVBoxLayout(input_group)
        
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("请输入要转换的Windows路径，支持多行输入...\n\n示例：\nI:\\git\\nas目录转换工具\nZ:\\Movies\\动漫\\进击的巨人\\Season 1")
        self.input_text.setFont(QFont("Consolas", self.scale_font_size(10)))
        self.input_text.setMinimumHeight(self.scale_size(120))
        self.input_text.setStyleSheet(f"""
            QTextEdit {{
                border: 2px solid #bdc3c7;
                border-radius: {self.scale_size(8)}px;
                padding: {self.scale_size(10)}px;
                background-color: #ffffff;
                selection-background-color: #3498db;
            }}
            QTextEdit:focus {{
                border-color: #3498db;
            }}
        """)
        input_layout.addWidget(self.input_text)
        left_layout.addWidget(input_group)
        
        # 输出区域
        output_group = QGroupBox("转换结果")
        output_group.setFont(QFont("Arial", self.scale_font_size(10), QFont.Bold))
        output_layout = QVBoxLayout(output_group)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("转换结果将显示在这里...")
        self.output_text.setFont(QFont("Consolas", self.scale_font_size(10)))
        self.output_text.setMinimumHeight(self.scale_size(120))
        self.output_text.setStyleSheet(f"""
            QTextEdit {{
                border: 2px solid #bdc3c7;
                border-radius: {self.scale_size(8)}px;
                padding: {self.scale_size(10)}px;
                background-color: #f8f9fa;
                selection-background-color: #3498db;
            }}
        """)
        output_layout.addWidget(self.output_text)
        left_layout.addWidget(output_group)
        
        # 规则说明区域
        # 帮助信息区域 - 可折叠的下拉菜单
        help_group = CollapsibleGroupBox("📖 帮助信息（点击展开/收起）")
        help_group.set_main_window(self)  # 设置主窗口引用
        help_group.setFont(QFont("Arial", self.scale_font_size(9), QFont.Bold))
        help_layout = QVBoxLayout(help_group)
        
        # 转换规则部分
        rules_title = QLabel("转换规则：")
        rules_title.setFont(QFont("Arial", self.scale_font_size(9), QFont.Bold))
        rules_title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        help_layout.addWidget(rules_title)
        
        rules_text = (
            "• 盘符移除：去掉盘符，直接转换路径\n"
            "• 路径格式：反斜杠 \\ 转为正斜杠 /\n"
            "• 前缀添加：统一添加 /share 前缀\n"
            "• 字符保留：支持中/英/日/韩等字符\n"
            "• 层级保持：严格保持原路径结构\n"
            "• 支持含空格和特殊符号的路径"
        )
        
        rules_label = QLabel(rules_text)
        rules_label.setFont(QFont("Arial", self.scale_font_size(9)))
        rules_label.setStyleSheet(f"""
            QLabel {{
                color: #34495e;
                padding: {self.scale_size(10)}px;
                background-color: #f8f9fa;
                border-radius: {self.scale_size(6)}px;
                border-left: {self.scale_size(4)}px solid #3498db;
                line-height: {self.scale_size(18)}px;
                margin-bottom: {self.scale_size(10)}px;
            }}
        """)
        help_layout.addWidget(rules_label)
        
        # 使用示例部分
        example_title = QLabel("使用示例：")
        example_title.setFont(QFont("Arial", self.scale_font_size(9), QFont.Bold))
        example_title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        help_layout.addWidget(example_title)
        
        example_text = (
            "输入：I:\\git\\nas目录转换工具\n"
            "输出：/share/git/nas目录转换工具\n\n"
            "输入：Z:\\Movies\\动漫\\进击的巨人\\Season 1\n"
            "输出：/share/Movies/动漫/进击的巨人/Season 1"
        )
        
        example_label = QLabel(example_text)
        example_label.setFont(QFont("Consolas", self.scale_font_size(9)))
        example_label.setStyleSheet(f"""
            QLabel {{
                color: #2c3e50;
                padding: {self.scale_size(10)}px;
                background-color: #f8f9fa;
                border-radius: {self.scale_size(6)}px;
                border-left: {self.scale_size(4)}px solid #27ae60;
                line-height: {self.scale_size(16)}px;
            }}
        """)
        help_layout.addWidget(example_label)
        
        left_layout.addWidget(help_group)
        
        # 右侧区域 - 按钮竖排
        right_widget = QWidget()
        right_widget.setFixedWidth(self.scale_size(180))  # 增加右侧宽度，使用scale_size而不是scale_button_size
        button_layout = QVBoxLayout(right_widget)
        button_layout.setSpacing(self.scale_button_size(15))
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 转换按钮
        self.convert_btn = QPushButton("🔄 转换路径")
        self.convert_btn.setFont(QFont("Arial", self.scale_font_size(10), QFont.Bold))
        self.convert_btn.setMinimumHeight(self.scale_button_size(50))
        self.convert_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #3498db;
                color: white;
                border: none;
                padding: {self.scale_button_size(12)}px {self.scale_button_size(24)}px;
                border-radius: {self.scale_size(8)}px;
                font-weight: bold;
                min-height: {self.scale_button_size(40)}px;
            }}
            QPushButton:hover {{
                background-color: #2980b9;
            }}
            QPushButton:pressed {{
                background-color: #21618c;
            }}
        """)
        self.convert_btn.clicked.connect(self.convert_paths)
        button_layout.addWidget(self.convert_btn)
        
        # 清空按钮
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.setFont(QFont("Arial", self.scale_font_size(10), QFont.Bold))
        self.clear_btn.setMinimumHeight(self.scale_button_size(50))
        self.clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: {self.scale_button_size(12)}px {self.scale_button_size(24)}px;
                border-radius: {self.scale_size(8)}px;
                font-weight: bold;
                min-height: {self.scale_button_size(40)}px;
            }}
            QPushButton:hover {{
                background-color: #c0392b;
            }}
            QPushButton:pressed {{
                background-color: #a93226;
            }}
        """)
        self.clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_btn)
        
        # 复制按钮
        self.copy_btn = QPushButton("📋 复制结果")
        self.copy_btn.setFont(QFont("Arial", self.scale_font_size(10), QFont.Bold))
        self.copy_btn.setMinimumHeight(self.scale_button_size(50))
        self.copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #27ae60;
                color: white;
                border: none;
                padding: {self.scale_button_size(12)}px {self.scale_button_size(24)}px;
                border-radius: {self.scale_size(8)}px;
                font-weight: bold;
                min-height: {self.scale_button_size(40)}px;
            }}
            QPushButton:hover {{
                background-color: #229954;
            }}
            QPushButton:pressed {{
                background-color: #1e8449;
            }}
        """)
        self.copy_btn.clicked.connect(self.copy_result)
        button_layout.addWidget(self.copy_btn)
        
        # 添加底部弹性空间，让按钮向上贴齐
        button_layout.addStretch()
        
        # 窗口尺寸显示标签
        self.size_label = QLabel("窗口尺寸: 900 × 700")
        self.size_label.setFont(QFont("Arial", self.scale_font_size(8)))
        self.size_label.setAlignment(Qt.AlignCenter)
        self.size_label.setStyleSheet(f"""
            QLabel {{
                color: #7f8c8d;
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: {self.scale_size(4)}px;
                padding: {self.scale_size(4)}px;
                margin-top: {self.scale_size(5)}px;
            }}
        """)
        button_layout.addWidget(self.size_label)
        
        # 将左右区域添加到内容布局
        content_layout.addWidget(left_widget, 3)  # 左侧占3份
        content_layout.addWidget(right_widget, 1)  # 右侧占1份
        
        # 将内容区域添加到主布局
        main_layout.addLayout(content_layout)
        
        # 设置窗口样式
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: #ffffff;
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: {self.scale_size(8)}px;
                margin-top: {self.scale_size(10)}px;
                padding-top: {self.scale_size(10)}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {self.scale_size(10)}px;
                padding: 0 {self.scale_size(8)}px 0 {self.scale_size(8)}px;
                color: #2c3e50;
            }}
        """)
        
        # 初始化窗口尺寸显示
        self.update_size_label()
        print(f"[调试] setup_ui完成后窗口大小: {self.size().width()} x {self.size().height()}")
        
        # 应用保存的窗口状态
        self.apply_saved_window_state()
        
    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        size = self.size()
        pos = self.pos()
        print(f"[调试] showEvent - 窗口位置: ({pos.x()}, {pos.y()}), 大小: {size.width()} x {size.height()}")
    
    def update_size_label(self):
        """更新窗口尺寸显示"""
        size = self.size()
        self.size_label.setText(f"窗口尺寸: {size.width()} × {size.height()}")
    
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        size = event.size()
        print(f"[调试] resizeEvent - 新窗口大小: {size.width()} x {size.height()}")
        if hasattr(self, 'size_label'):
            self.update_size_label()
    
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
    
    def closeEvent(self, event):
        """程序关闭时保存配置"""
        try:
            # 保存当前窗口状态
            self.save_config()
            print(f"[调试] 程序关闭时已保存配置")
        except Exception as e:
            print(f"[调试] 保存配置时出错: {e}")
        
        # 调用父类的closeEvent
        super().closeEvent(event)
    
    def load_config(self):
        """加载配置文件"""
        default_config = {
            "nas_prefix": "/share",
            "window_width": 1249,
            "window_height": 1046,
            "help_expanded": False
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.nas_prefix = config.get('nas_prefix', default_config['nas_prefix'])
                    # 读取窗口大小和帮助信息状态
                    self.saved_window_width = config.get('window_width', default_config['window_width'])
                    self.saved_window_height = config.get('window_height', default_config['window_height'])
                    self.saved_help_expanded = config.get('help_expanded', default_config['help_expanded'])
                    print(f"[调试] 从配置文件读取: 窗口大小 {self.saved_window_width}x{self.saved_window_height}, 帮助信息展开: {self.saved_help_expanded}")
            else:
                # 创建默认配置文件
                self.nas_prefix = default_config['nas_prefix']
                self.saved_window_width = default_config['window_width']
                self.saved_window_height = default_config['window_height']
                self.saved_help_expanded = default_config['help_expanded']
                self.save_config(default_config)
                print(f"[调试] 使用默认配置: 窗口大小 {self.saved_window_width}x{self.saved_window_height}, 帮助信息展开: {self.saved_help_expanded}")
        except Exception as e:
            # 如果配置文件损坏，使用默认配置并重新创建文件
            self.nas_prefix = default_config['nas_prefix']
            self.saved_window_width = default_config['window_width']
            self.saved_window_height = default_config['window_height']
            self.saved_help_expanded = default_config['help_expanded']
            self.save_config(default_config)
            print(f"[调试] 配置文件损坏，使用默认配置: 窗口大小 {self.saved_window_width}x{self.saved_window_height}, 帮助信息展开: {self.saved_help_expanded}")
    
    def save_config(self, config=None):
        """保存配置文件"""
        try:
            # 如果没有传入config，则创建当前状态的配置
            if config is None:
                current_size = self.size()
                config = {
                    "nas_prefix": self.nas_prefix,
                    "window_width": current_size.width(),
                    "window_height": current_size.height(),
                    "help_expanded": getattr(self, 'help_expanded', False)
                }
                print(f"[调试] 保存当前配置: 窗口大小 {config['window_width']}x{config['window_height']}, 帮助信息展开: {config['help_expanded']}")
            
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