#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows路径转Linux NAS路径转换工具 - PyQt版本
功能：自动将Windows路径转换为Linux NAS路径
作者：Sallos
"""

# 版本信息
VERSION = "2.1.0"

import sys
import re
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QGroupBox, QMessageBox,
    QSplitter, QFrame, QToolButton, QScrollArea, QStackedWidget,
    QSpinBox, QCheckBox
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
        
        # 配置文件路径
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
        
        # 加载配置（必须在UI设置之前）
        self.load_config()
        
        # 获取DPI缩放比例
        self.dpi_scale = self.get_dpi_scale()
        print(f"[调试] DPI缩放比例: {self.dpi_scale}")
        
        # 创建堆叠窗口部件来管理页面
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # 创建主页面
        self.main_page = QWidget()
        self.stacked_widget.addWidget(self.main_page)
        
        # 创建设置页面
        self.settings_page = QWidget()
        self.stacked_widget.addWidget(self.settings_page)
        
        # 设置主页面为当前页面
        self.stacked_widget.setCurrentWidget(self.main_page)
        
        # 设置窗口属性
        self.setWindowTitle(f"NAS路径转换工具 v{VERSION}")
        self.setMinimumSize(900, 700)
        
        # 设置UI
        self.setup_ui()
        self.create_settings_page()
        
        # 应用保存的窗口状态
        self.apply_saved_window_state()
        
        # 初始化状态变量
        self.help_expanded = False
        self.initial_size = None
    
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
                # 使用保存的窗口大小
                saved_width = self.saved_window_width
                saved_height = self.saved_window_height
                print(f"[调试] 应用保存的窗口大小: {saved_width}x{saved_height}")
                
                # 设置窗口位置和大小
                self.setGeometry(100, 100, saved_width, saved_height)
                
                # 再次强制处理事件并检查最终大小
                QApplication.processEvents()
                final_size = self.size()
                print(f"[调试] 最终窗口大小: {final_size.width()}x{final_size.height()}")
            else:
                # 如果没有保存的窗口大小，使用默认大小
                default_width = self.scale_size(1198)
                default_height = self.scale_size(1046)
                print(f"[调试] 使用默认窗口大小: {default_width}x{default_height}")
                self.setGeometry(100, 100, default_width, default_height)
                
        except Exception as e:
            print(f"[调试] 应用保存的窗口状态时出错: {e}")
            # 出错时使用默认大小
            default_width = self.scale_size(1198)
            default_height = self.scale_size(1046)
            self.setGeometry(100, 100, default_width, default_height)
    
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
        """根据DPI缩放和用户设置的字体大小"""
        # 获取用户设置的字体大小，如果没有设置则使用默认值
        user_font_size = getattr(self, 'saved_font_size', 9)
        # 计算字体大小：用户设置的字体大小 + (基础大小 - 9) 的差值，然后应用DPI缩放
        adjusted_size = user_font_size + (base_size - 9)
        return int(adjusted_size * self.dpi_scale * 0.6)  # 缩小25%
    
    def scale_size(self, base_size):
        """根据DPI缩放尺寸"""
        return int(base_size * self.dpi_scale)
    
    def scale_button_size(self, base_size):
        """根据字体大小缩放按钮尺寸"""
        return int(base_size * self.dpi_scale * 0.6)  # 与字体保持相同的缩放比例
        
    def setup_ui(self):
        """设置用户界面"""
        # 主布局 - 垂直布局包含标题和内容区域
        main_layout = QVBoxLayout(self.main_page)
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
        
        # 设置按钮
        self.settings_btn = QPushButton("⚙️ 设置")
        self.settings_btn.setFont(QFont("Arial", self.scale_font_size(10), QFont.Bold))
        self.settings_btn.setMinimumHeight(self.scale_button_size(50))
        self.settings_btn.setStyleSheet(f"""
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
        self.settings_btn.clicked.connect(self.show_settings)
        button_layout.addWidget(self.settings_btn)
        
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
            "help_expanded": False,
            "font_size": 9,  # 默认字体大小
            "auto_resize": False  # 是否自动调整界面大小
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
                    # 读取设置页面配置
                    self.saved_font_size = config.get('font_size', default_config['font_size'])
                    self.saved_auto_resize = config.get('auto_resize', default_config['auto_resize'])
                    print(f"[调试] 从配置文件读取: 窗口大小 {self.saved_window_width}x{self.saved_window_height}, 帮助信息展开: {self.saved_help_expanded}, 字体大小: {self.saved_font_size}, 自动调整: {self.saved_auto_resize}")
            else:
                # 创建默认配置文件
                self.nas_prefix = default_config['nas_prefix']
                self.saved_window_width = default_config['window_width']
                self.saved_window_height = default_config['window_height']
                self.saved_help_expanded = default_config['help_expanded']
                self.saved_font_size = default_config['font_size']
                self.saved_auto_resize = default_config['auto_resize']
                self.save_config(default_config)
                print(f"[调试] 使用默认配置: 窗口大小 {self.saved_window_width}x{self.saved_window_height}, 帮助信息展开: {self.saved_help_expanded}, 字体大小: {self.saved_font_size}, 自动调整: {self.saved_auto_resize}")
        except Exception as e:
            # 如果配置文件损坏，使用默认配置并重新创建文件
            self.nas_prefix = default_config['nas_prefix']
            self.saved_window_width = default_config['window_width']
            self.saved_window_height = default_config['window_height']
            self.saved_help_expanded = default_config['help_expanded']
            self.saved_font_size = default_config['font_size']
            self.saved_auto_resize = default_config['auto_resize']
            self.save_config(default_config)
            print(f"[调试] 配置文件损坏，使用默认配置: 窗口大小 {self.saved_window_width}x{self.saved_window_height}, 帮助信息展开: {self.saved_help_expanded}, 字体大小: {self.saved_font_size}, 自动调整: {self.saved_auto_resize}")
    
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
                    "help_expanded": getattr(self, 'help_expanded', False),
                    "font_size": getattr(self, 'saved_font_size', 9),
                    "auto_resize": getattr(self, 'saved_auto_resize', False)
                }
                print(f"[调试] 保存当前配置: 窗口大小 {config['window_width']}x{config['window_height']}, 帮助信息展开: {config['help_expanded']}, 字体大小: {config['font_size']}, 自动调整: {config['auto_resize']}")
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置文件失败：{str(e)}")
    
    def create_settings_page(self):
        """创建设置页面"""
        # 设置页面主布局
        settings_layout = QVBoxLayout(self.settings_page)
        settings_layout.setSpacing(self.scale_size(20))
        settings_layout.setContentsMargins(self.scale_size(20), self.scale_size(20), 
                                         self.scale_size(20), self.scale_size(20))
        
        # 标题
        title_label = QLabel("⚙️ 设置")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", self.scale_font_size(18), QFont.Bold))
        title_label.setStyleSheet(f"""
            QLabel {{
                color: #2c3e50;
                padding: {self.scale_size(15)}px;
                background-color: #ecf0f1;
                border: 2px solid #bdc3c7;
                border-radius: {self.scale_size(10)}px;
                margin-bottom: {self.scale_size(10)}px;
            }}
        """)
        settings_layout.addWidget(title_label)
        
        # 设置内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(self.scale_size(15))
        
        # 字体大小设置
        font_group = QGroupBox("字体大小设置")
        font_group.setFont(QFont("Arial", self.scale_font_size(12), QFont.Bold))
        font_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid #3498db;
                border-radius: {self.scale_size(8)}px;
                margin-top: {self.scale_size(10)}px;
                padding-top: {self.scale_size(10)}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {self.scale_size(10)}px;
                padding: 0 {self.scale_size(5)}px 0 {self.scale_size(5)}px;
                color: #2c3e50;
            }}
        """)
        font_layout = QHBoxLayout(font_group)
        
        font_label = QLabel("字体大小:")
        font_label.setFont(QFont("Arial", self.scale_font_size(11)))
        font_layout.addWidget(font_label)
        
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 20)
        self.font_size_spinbox.setValue(getattr(self, 'saved_font_size', 9))
        self.font_size_spinbox.setSuffix(" pt")
        self.font_size_spinbox.setFont(QFont("Arial", self.scale_font_size(11)))
        self.font_size_spinbox.setStyleSheet(f"""
            QSpinBox {{
                border: 2px solid #bdc3c7;
                border-radius: {self.scale_size(5)}px;
                padding: {self.scale_size(5)}px;
                background-color: white;
                min-width: {self.scale_size(80)}px;
            }}
            QSpinBox:focus {{
                border-color: #3498db;
            }}
        """)
        self.font_size_spinbox.valueChanged.connect(self.on_font_size_changed)
        font_layout.addWidget(self.font_size_spinbox)
        
        apply_font_btn = QPushButton("应用字体")
        apply_font_btn.setFont(QFont("Arial", self.scale_font_size(10), QFont.Bold))
        apply_font_btn.setMinimumHeight(self.scale_button_size(50))
        apply_font_btn.setStyleSheet(f"""
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
        apply_font_btn.clicked.connect(self.apply_font_size)
        font_layout.addWidget(apply_font_btn)
        
        font_layout.addStretch()
        content_layout.addWidget(font_group)
        
        # 界面大小设置
        size_group = QGroupBox("界面大小设置")
        size_group.setFont(QFont("Arial", self.scale_font_size(12), QFont.Bold))
        size_group.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid #e67e22;
                border-radius: {self.scale_size(8)}px;
                margin-top: {self.scale_size(10)}px;
                padding-top: {self.scale_size(10)}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: {self.scale_size(10)}px;
                padding: 0 {self.scale_size(5)}px 0 {self.scale_size(5)}px;
                color: #2c3e50;
            }}
        """)
        size_layout = QVBoxLayout(size_group)
        
        # 自动调整界面大小选项
        auto_resize_layout = QHBoxLayout()
        self.auto_resize_checkbox = QCheckBox("自动调整界面大小")
        self.auto_resize_checkbox.setChecked(getattr(self, 'saved_auto_resize', False))
        self.auto_resize_checkbox.setFont(QFont("Arial", self.scale_font_size(11)))
        self.auto_resize_checkbox.setStyleSheet(f"""
            QCheckBox {{
                spacing: {self.scale_size(8)}px;
            }}
            QCheckBox::indicator {{
                width: {self.scale_size(18)}px;
                height: {self.scale_size(18)}px;
            }}
            QCheckBox::indicator:unchecked {{
                border: 2px solid #bdc3c7;
                border-radius: {self.scale_size(3)}px;
                background-color: white;
            }}
            QCheckBox::indicator:checked {{
                border: 2px solid #e67e22;
                border-radius: {self.scale_size(3)}px;
                background-color: #e67e22;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEwIDNMNC41IDguNUwyIDYiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
            }}
        """)
        self.auto_resize_checkbox.stateChanged.connect(self.on_auto_resize_changed)
        auto_resize_layout.addWidget(self.auto_resize_checkbox)
        auto_resize_layout.addStretch()
        size_layout.addLayout(auto_resize_layout)
        
        # 手动调整界面大小按钮
        manual_resize_layout = QHBoxLayout()
        resize_btn = QPushButton("🔧 调整界面大小")
        resize_btn.setFont(QFont("Arial", self.scale_font_size(10), QFont.Bold))
        resize_btn.setMinimumHeight(self.scale_button_size(50))
        resize_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #f39c12;
                color: white;
                border: none;
                padding: {self.scale_button_size(12)}px {self.scale_button_size(24)}px;
                border-radius: {self.scale_size(8)}px;
                font-weight: bold;
                min-height: {self.scale_button_size(40)}px;
            }}
            QPushButton:hover {{
                background-color: #e67e22;
            }}
            QPushButton:pressed {{
                background-color: #d35400;
            }}
        """)
        resize_btn.clicked.connect(self.adjust_window_size)
        manual_resize_layout.addWidget(resize_btn)
        manual_resize_layout.addStretch()
        size_layout.addLayout(manual_resize_layout)
        
        content_layout.addWidget(size_group)
        
        # 添加弹性空间
        content_layout.addStretch()
        
        settings_layout.addWidget(content_widget)
        
        # 返回按钮
        back_btn = QPushButton("← 返回主页")
        back_btn.setFont(QFont("Arial", self.scale_font_size(10), QFont.Bold))
        back_btn.setMinimumHeight(self.scale_button_size(50))
        back_btn.setStyleSheet(f"""
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
        back_btn.clicked.connect(self.show_main_page)
        
        # 按钮容器，居中显示
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.addStretch()
        button_layout.addWidget(back_btn)
        button_layout.addStretch()
        
        settings_layout.addWidget(button_container)
    
    def show_settings(self):
        """显示设置页面"""
        self.stacked_widget.setCurrentWidget(self.settings_page)
    
    def show_main_page(self):
        """显示主页面"""
        self.stacked_widget.setCurrentWidget(self.main_page)
    
    def on_font_size_changed(self, value):
        """字体大小改变时的处理"""
        self.saved_font_size = value
    
    def apply_font_size(self):
        """应用字体大小设置"""
        try:
            # 更新所有文本控件的字体大小
            new_font_size = self.font_size_spinbox.value()
            self.saved_font_size = new_font_size
            
            # 保存设置到配置文件
            self.save_config()
            
            # 立即应用字体大小到当前界面
            self.update_all_fonts()
            
            QMessageBox.information(self, "设置已应用", 
                                  f"字体大小已设置为 {new_font_size} pt 并立即生效喵~")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"应用字体大小失败：{str(e)}")
    
    def update_all_fonts(self):
        """更新所有控件的字体大小"""
        try:
            # 递归更新主页面的所有控件字体
            self.update_widget_fonts(self.main_page)
            # 递归更新设置页面的所有控件字体
            self.update_widget_fonts(self.settings_page)
            # 强制重绘界面
            self.update()
        except Exception as e:
            print(f"[调试] 更新字体时出错: {e}")
    
    def update_widget_fonts(self, widget):
        """递归更新控件及其子控件的字体"""
        try:
            # 更新当前控件的字体
            if hasattr(widget, 'font'):
                current_font = widget.font()
                if current_font:
                    # 根据控件类型设置合适的字体大小
                    if isinstance(widget, QLabel):
                        # 标签字体
                        if "title" in widget.objectName().lower() or widget.font().pointSize() > 15:
                            # 标题类标签使用较大字体
                            new_size = self.scale_font_size(18)
                        else:
                            # 普通标签
                            new_size = self.scale_font_size(12)
                    elif isinstance(widget, QPushButton):
                        # 按钮字体
                        new_size = self.scale_font_size(11)
                    elif isinstance(widget, (QSpinBox, QCheckBox)):
                        # 输入控件字体
                        new_size = self.scale_font_size(11)
                    else:
                        # 其他控件使用默认字体大小
                        new_size = self.scale_font_size(12)
                    
                    current_font.setPointSize(max(8, new_size))  # 确保字体不会太小
                    widget.setFont(current_font)
            
            # 递归处理子控件
            for child in widget.findChildren(QWidget):
                if child.parent() == widget:  # 只处理直接子控件，避免重复处理
                    self.update_widget_fonts(child)
                    
        except Exception as e:
            print(f"[调试] 更新控件字体时出错: {e}")
    
    def on_auto_resize_changed(self, state):
        """自动调整界面大小选项改变时的处理"""
        self.saved_auto_resize = state == 2  # Qt.Checked = 2
        self.save_config()
        
        if self.saved_auto_resize:
            # 如果启用自动调整，立即执行一次
            self.adjust_window_size()
    
    def adjust_window_size(self):
        """调整界面大小"""
        try:
            # 获取当前DPI缩放
            dpi_scale = self.get_dpi_scale()
            
            # 根据DPI缩放计算合适的窗口大小
            base_width = 1249
            base_height = 1046
            
            # 如果帮助信息展开，增加高度
            if getattr(self, 'help_expanded', False):
                base_height += 200
            
            new_width = int(base_width * dpi_scale)
            new_height = int(base_height * dpi_scale)
            
            # 应用新的窗口大小
            self.resize(new_width, new_height)
            
            # 保存新的窗口大小
            self.save_config()
            
            QMessageBox.information(self, "界面调整完成", 
                                  f"界面大小已调整为 {new_width}x{new_height}\n"
                                  f"DPI缩放比例: {dpi_scale:.2f} 喵~")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"调整界面大小失败：{str(e)}")

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