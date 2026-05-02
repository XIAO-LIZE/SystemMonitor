"""
系统监控工具 - GUI 主窗口

使用 tkinter 构建的系统监控面板，包含系统信息、CPU、内存、磁盘、显卡、网络、进程七个标签页。
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

from .monitor import SystemMonitor
from .hardware import HardwareCollector
from .gpu_monitor import GpuMonitor
from .charts import RealtimeChart, HAS_MATPLOTLIB


class MainWindow:
    """
    系统监控主窗口
    
    功能：
    - 系统信息总览（硬件型号、操作系统）
    - CPU 使用率实时监控（总体 + 每核心）
    - 内存使用率实时监控
    - 磁盘分区信息 + 读写速度
    - 网络流量实时监控
    - 进程列表管理（查看/终止进程）
    """

    # 刷新间隔（毫秒）
    REFRESH_INTERVAL = 1000

    def __init__(self):
        self.monitor = SystemMonitor(history_size=120)
        self.hw = HardwareCollector()
        self.gpu_monitor = GpuMonitor()

        # 预采集硬件信息（只采一次）
        self._cpu_detail = self.hw.get_cpu_detail()
        self._mem_detail = self.hw.get_memory_detail()
        self._disk_details = self.hw.get_disk_details()
        self._gpu_details = self.hw.get_gpu_details()
        self._sys_info = self.hw.get_system_info()

        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("系统监控工具 v1.0")
        self.root.geometry("950x700")
        self.root.minsize(850, 650)

        # 深色主题配色
        self.colors = {
            "bg": "#1e1e1e",
            "card_bg": "#2d2d2d",
            "text": "#ffffff",
            "text_dim": "#888888",
            "accent": "#4FC3F7",
            "green": "#66BB6A",
            "orange": "#FFA726",
            "red": "#EF5350",
            "progress_bg": "#404040",
            "highlight": "#BB86FC",
        }

        self.root.configure(bg=self.colors["bg"])

        # 设置全局默认字体（解决中文乱码）
        default_font = ("Microsoft YaHei UI", 10)
        self.root.option_add("*Font", default_font)
        self.root.option_add("*TNotebook.Tab.Font", ("Microsoft YaHei UI", 10))
        self.root.option_add("*TButton.Font", ("Microsoft YaHei UI", 9))
        self.root.option_add("*TLabel.Font", ("Microsoft YaHei UI", 10))
        self.root.option_add("*Treeview.Heading.Font", ("Microsoft YaHei UI", 9, "bold"))
        self.root.option_add("*Treeview.Font", ("Microsoft YaHei UI", 9))

        # 设置 ttk 样式
        self._setup_styles()

        # 构建界面
        self._build_header()
        self._build_notebook()

        # 启动数据刷新
        self._running = True
        self._refresh_data()

    def _setup_styles(self):
        """配置 ttk 组件样式"""
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook", background=self.colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=self.colors["card_bg"],
                        foreground=self.colors["text"],
                        padding=[15, 8],
                        font=("Microsoft YaHei UI", 10))
        style.map("TNotebook.Tab",
                  background=[("selected", self.colors["accent"])],
                  foreground=[("selected", "#ffffff")])

        style.configure("Custom.Horizontal.TProgressbar",
                        background=self.colors["accent"],
                        troughcolor=self.colors["progress_bg"],
                        borderwidth=0,
                        lightcolor=self.colors["accent"],
                        darkcolor=self.colors["accent"])

        style.configure("Danger.TButton",
                        background=self.colors["red"],
                        foreground="#ffffff",
                        font=("Microsoft YaHei UI", 9))

    def _build_header(self):
        """构建顶部标题栏"""
        header = tk.Frame(self.root, bg=self.colors["card_bg"], height=50)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)

        # 标题 + 主机名
        hostname = self._sys_info.hostname
        title_text = f"🖥 系统监控工具  —  {hostname}"
        tk.Label(
            header, text=title_text,
            bg=self.colors["card_bg"], fg=self.colors["text"],
            font=("Microsoft YaHei UI", 14, "bold")
        ).pack(side=tk.LEFT, padx=15)

        # 操作系统标签
        os_text = f"{self._sys_info.os_name} {self._sys_info.os_arch}"
        tk.Label(
            header, text=os_text,
            bg=self.colors["card_bg"], fg=self.colors["text_dim"],
            font=("Microsoft YaHei UI", 9)
        ).pack(side=tk.RIGHT, padx=15)

        # 状态标签
        self.status_label = tk.Label(
            header, text="● 运行中",
            bg=self.colors["card_bg"], fg=self.colors["green"],
            font=("Microsoft YaHei UI", 10)
        )
        self.status_label.pack(side=tk.RIGHT, padx=10)

    def _build_notebook(self):
        """构建标签页"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._build_info_tab()      # 系统信息
        self._build_cpu_tab()       # CPU
        self._build_memory_tab()    # 内存
        self._build_disk_tab()      # 磁盘
        self._build_gpu_tab()       # 显卡
        self._build_network_tab()   # 网络
        self._build_process_tab()   # 进程

    def _build_info_card(self, parent, title: str, row: int, col: int):
        """创建信息卡片"""
        card = tk.Frame(parent, bg=self.colors["card_bg"], padx=15, pady=10)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        tk.Label(
            card, text=title,
            bg=self.colors["card_bg"], fg=self.colors["text_dim"],
            font=("Microsoft YaHei UI", 9)
        ).pack(anchor="w")

        value_label = tk.Label(
            card, text="--",
            bg=self.colors["card_bg"], fg=self.colors["text"],
            font=("Microsoft YaHei UI", 18, "bold")
        )
        value_label.pack(anchor="w", pady=(5, 0))

        return value_label

    def _build_info_row(self, parent, label: str, value: str, row: int):
        """在信息页面创建一行信息"""
        tk.Label(
            parent, text=label,
            bg=self.colors["card_bg"], fg=self.colors["text_dim"],
            font=("Microsoft YaHei UI", 10),
            anchor="e", width=14
        ).grid(row=row, column=0, padx=(15, 10), pady=4, sticky="e")

        tk.Label(
            parent, text=value,
            bg=self.colors["card_bg"], fg=self.colors["text"],
            font=("Microsoft YaHei UI", 10),
            anchor="w"
        ).grid(row=row, column=1, padx=(0, 15), pady=4, sticky="w")

    # ==================== 系统信息标签页 ====================

    def _build_info_tab(self):
        """系统信息标签页 - 显示所有硬件型号和规格"""
        tab = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(tab, text="  系统信息  ")

        # 可滚动区域
        canvas = tk.Canvas(tab, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=self.colors["bg"])

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 鼠标滚轮支持
        def _on_mousewheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ---- 操作系统信息 ----
        sys_frame = tk.LabelFrame(
            scroll_frame, text="  操作系统  ",
            bg=self.colors["card_bg"], fg=self.colors["accent"],
            font=("Microsoft YaHei UI", 11, "bold"),
            padx=10, pady=10
        )
        sys_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        sys_frame.grid_columnconfigure(1, weight=1)

        self._build_info_row(sys_frame, "主机名：", self._sys_info.hostname, 0)
        self._build_info_row(sys_frame, "操作系统：",
                             f"{self._sys_info.os_name} {self._sys_info.os_version}", 1)
        self._build_info_row(sys_frame, "系统架构：", self._sys_info.os_arch, 2)

        # ---- CPU 信息 ----
        cpu = self._cpu_detail
        cpu_frame = tk.LabelFrame(
            scroll_frame, text="  处理器 (CPU)  ",
            bg=self.colors["card_bg"], fg=self.colors["accent"],
            font=("Microsoft YaHei UI", 11, "bold"),
            padx=10, pady=10
        )
        cpu_frame.pack(fill=tk.X, padx=15, pady=5)
        cpu_frame.grid_columnconfigure(1, weight=1)

        self._build_info_row(cpu_frame, "型号：", cpu.name, 0)
        self._build_info_row(cpu_frame, "架构：", cpu.architecture, 1)
        self._build_info_row(cpu_frame, "物理核心：", f"{cpu.physical_cores} 核", 2)
        self._build_info_row(cpu_frame, "逻辑核心：", f"{cpu.logical_cores} 线程", 3)
        self._build_info_row(cpu_frame, "最大频率：", f"{cpu.max_freq:.0f} MHz", 4)
        if cpu.l2_cache:
            self._build_info_row(cpu_frame, "L2 缓存：", cpu.l2_cache, 5)
        if cpu.l3_cache:
            self._build_info_row(cpu_frame, "L3 缓存：", cpu.l3_cache, 6)

        # ---- 内存信息 ----
        mem = self._mem_detail
        mem_frame = tk.LabelFrame(
            scroll_frame, text="  内存 (RAM)  ",
            bg=self.colors["card_bg"], fg=self.colors["accent"],
            font=("Microsoft YaHei UI", 11, "bold"),
            padx=10, pady=10
        )
        mem_frame.pack(fill=tk.X, padx=15, pady=5)
        mem_frame.grid_columnconfigure(1, weight=1)

        row = 0
        self._build_info_row(mem_frame, "总容量：",
                             HardwareCollector.format_bytes(mem.total), row); row += 1
        if mem.type:
            self._build_info_row(mem_frame, "内存类型：", mem.type, row); row += 1
        if mem.speed:
            self._build_info_row(mem_frame, "频率：", mem.speed, row); row += 1
        self._build_info_row(mem_frame, "插槽数：", f"{len(mem.slots)} 个", row); row += 1

        # 每个插槽详情
        for i, slot in enumerate(mem.slots):
            cap = HardwareCollector.format_bytes(slot.get("capacity", 0))
            part = slot.get("part_number", "")
            mfr = slot.get("manufacturer", "")
            slot_name = slot.get("slot", f"插槽 {i+1}")
            detail = f"{cap}"
            if part:
                detail += f"  ({part})"
            if mfr:
                detail += f"  - {mfr}"
            self._build_info_row(mem_frame, f"{slot_name}：", detail, row); row += 1

        # ---- 磁盘信息 ----
        disk_frame = tk.LabelFrame(
            scroll_frame, text="  磁盘  ",
            bg=self.colors["card_bg"], fg=self.colors["accent"],
            font=("Microsoft YaHei UI", 11, "bold"),
            padx=10, pady=10
        )
        disk_frame.pack(fill=tk.X, padx=15, pady=5)
        disk_frame.grid_columnconfigure(1, weight=1)

        for i, disk in enumerate(self._disk_details):
            row_offset = i * 4
            self._build_info_row(disk_frame, f"磁盘 {i+1} 型号：", disk.model or "未知", row_offset)
            self._build_info_row(disk_frame, "  容量：",
                                 HardwareCollector.format_bytes(disk.size) if disk.size else "未知",
                                 row_offset + 1)
            self._build_info_row(disk_frame, "  接口：", disk.interface or "未知", row_offset + 2)
            self._build_info_row(disk_frame, "  介质：", disk.media_type or "未知", row_offset + 3)

        # ---- 显卡信息 ----
        gpu_frame = tk.LabelFrame(
            scroll_frame, text="  显卡 (GPU)  ",
            bg=self.colors["card_bg"], fg=self.colors["accent"],
            font=("Microsoft YaHei UI", 11, "bold"),
            padx=10, pady=10
        )
        gpu_frame.pack(fill=tk.X, padx=15, pady=(5, 15))
        gpu_frame.grid_columnconfigure(1, weight=1)

        for i, gpu in enumerate(self._gpu_details):
            self._build_info_row(gpu_frame, f"显卡 {i+1}：", gpu.name, i * 2)
            if gpu.memory:
                self._build_info_row(gpu_frame, "  显存：", gpu.memory, i * 2 + 1)

        if not self._gpu_details:
            self._build_info_row(gpu_frame, "显卡：", "未检测到", 0)

    # ==================== CPU 标签页 ====================

    def _build_cpu_tab(self):
        """CPU 标签页"""
        tab = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(tab, text="  CPU  ")

        # CPU 型号提示条
        model_bar = tk.Frame(tab, bg=self.colors["card_bg"], height=30)
        model_bar.pack(fill=tk.X, padx=10, pady=(10, 0))
        model_bar.pack_propagate(False)
        tk.Label(
            model_bar,
            text=f"  {self._cpu_detail.name}  |  "
                 f"{self._cpu_detail.physical_cores}核"
                 f"{self._cpu_detail.logical_cores}线程  |  "
                 f"最大 {self._cpu_detail.max_freq:.0f} MHz",
            bg=self.colors["card_bg"], fg=self.colors["text_dim"],
            font=("Microsoft YaHei UI", 9)
        ).pack(side=tk.LEFT, padx=10)

        # 顶部信息卡片
        cards_frame = tk.Frame(tab, bg=self.colors["bg"])
        cards_frame.pack(fill=tk.X, padx=10, pady=10)
        cards_frame.columnconfigure((0, 1, 2), weight=1)

        self.cpu_overall_label = self._build_info_card(cards_frame, "CPU 总体使用率", 0, 0)
        self.cpu_freq_label = self._build_info_card(cards_frame, "CPU 频率", 0, 1)
        self.cpu_cores_label = self._build_info_card(cards_frame, "核心数", 0, 2)

        # 每核心进度条
        cores_frame = tk.LabelFrame(
            tab, text=" 各核心使用率 ",
            bg=self.colors["card_bg"], fg=self.colors["text"],
            font=("Microsoft YaHei UI", 10),
            padx=10, pady=10
        )
        cores_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.cpu_core_bars = []
        self.cpu_core_frames = cores_frame

        # 趋势图
        self.cpu_chart = RealtimeChart(
            tab, title="CPU 使用率趋势", y_label="%",
            y_max=100, line_labels=["CPU"],
            line_colors=[self.colors["accent"]],
            figsize=(8, 2.5)
        )
        self.cpu_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    # ==================== 内存标签页 ====================

    def _build_memory_tab(self):
        """内存标签页"""
        tab = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(tab, text="  内存  ")

        # 内存型号提示条
        mem = self._mem_detail
        model_text = f"  {mem.type or '内存'}  |  {mem.speed or '频率未知'}  |  "
        model_text += f"总容量 {HardwareCollector.format_bytes(mem.total)}  |  "
        model_text += f"{len(mem.slots)} 个插槽"

        model_bar = tk.Frame(tab, bg=self.colors["card_bg"], height=30)
        model_bar.pack(fill=tk.X, padx=10, pady=(10, 0))
        model_bar.pack_propagate(False)
        tk.Label(
            model_bar, text=model_text,
            bg=self.colors["card_bg"], fg=self.colors["text_dim"],
            font=("Microsoft YaHei UI", 9)
        ).pack(side=tk.LEFT, padx=10)

        # 信息卡片
        cards_frame = tk.Frame(tab, bg=self.colors["bg"])
        cards_frame.pack(fill=tk.X, padx=10, pady=10)
        cards_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.mem_percent_label = self._build_info_card(cards_frame, "使用率", 0, 0)
        self.mem_used_label = self._build_info_card(cards_frame, "已用", 0, 1)
        self.mem_available_label = self._build_info_card(cards_frame, "可用", 0, 2)
        self.mem_total_label = self._build_info_card(cards_frame, "总量", 0, 3)

        # 内存进度条
        bar_frame = tk.LabelFrame(
            tab, text=" 内存使用 ",
            bg=self.colors["card_bg"], fg=self.colors["text"],
            font=("Microsoft YaHei UI", 10),
            padx=10, pady=10
        )
        bar_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.mem_progress = ttk.Progressbar(
            bar_frame, style="Custom.Horizontal.TProgressbar",
            length=400, mode="determinate"
        )
        self.mem_progress.pack(fill=tk.X, pady=5)

        self.mem_bar_label = tk.Label(
            bar_frame, text="",
            bg=self.colors["card_bg"], fg=self.colors["text_dim"],
            font=("Microsoft YaHei UI", 9)
        )
        self.mem_bar_label.pack(anchor="w")

        # 趋势图
        self.mem_chart = RealtimeChart(
            tab, title="内存使用率趋势", y_label="%",
            y_max=100, line_labels=["内存"],
            line_colors=[self.colors["green"]],
            figsize=(8, 2.5)
        )
        self.mem_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    # ==================== 磁盘标签页 ====================

    def _build_disk_tab(self):
        """磁盘标签页"""
        tab = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(tab, text="  磁盘  ")

        # 磁盘型号提示条
        disk_models = "  |  ".join(
            f"{d.model} ({HardwareCollector.format_bytes(d.size)})"
            for d in self._disk_details if d.model
        ) or "未检测到物理磁盘信息"

        model_bar = tk.Frame(tab, bg=self.colors["card_bg"], height=30)
        model_bar.pack(fill=tk.X, padx=10, pady=(10, 0))
        model_bar.pack_propagate(False)
        tk.Label(
            model_bar, text=f"  {disk_models}",
            bg=self.colors["card_bg"], fg=self.colors["text_dim"],
            font=("Microsoft YaHei UI", 9)
        ).pack(side=tk.LEFT, padx=10)

        # 速度信息
        speed_frame = tk.Frame(tab, bg=self.colors["bg"])
        speed_frame.pack(fill=tk.X, padx=10, pady=10)
        speed_frame.columnconfigure((0, 1), weight=1)

        self.disk_read_label = self._build_info_card(speed_frame, "读取速度", 0, 0)
        self.disk_write_label = self._build_info_card(speed_frame, "写入速度", 0, 1)

        # 分区列表
        partitions_frame = tk.LabelFrame(
            tab, text=" 磁盘分区 ",
            bg=self.colors["card_bg"], fg=self.colors["text"],
            font=("Microsoft YaHei UI", 10),
            padx=10, pady=10
        )
        partitions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        columns = ("设备", "挂载点", "文件系统", "总量", "已用", "可用", "使用率")
        self.disk_tree = ttk.Treeview(partitions_frame, columns=columns, show="headings", height=6)

        for col in columns:
            self.disk_tree.heading(col, text=col)
            self.disk_tree.column(col, width=100, anchor="center")

        scrollbar = ttk.Scrollbar(partitions_frame, orient=tk.VERTICAL, command=self.disk_tree.yview)
        self.disk_tree.configure(yscrollcommand=scrollbar.set)

        self.disk_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # ==================== 显卡标签页 ====================

    def _build_gpu_tab(self):
        """显卡标签页 - 实时监控 GPU 使用率、显存、温度"""
        tab = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(tab, text="  显卡  ")

        # 显卡型号提示条
        vendor = self.gpu_monitor._vendor
        gpu_name = self.gpu_monitor._gpu_name
        model_bar = tk.Frame(tab, bg=self.colors["card_bg"], height=30)
        model_bar.pack(fill=tk.X, padx=10, pady=(10, 0))
        model_bar.pack_propagate(False)
        tk.Label(
            model_bar, text=f"  {gpu_name}  |  {vendor}",
            bg=self.colors["card_bg"], fg=self.colors["text_dim"],
            font=("Microsoft YaHei UI", 9)
        ).pack(side=tk.LEFT, padx=10)

        # 顶部信息卡片
        cards_frame = tk.Frame(tab, bg=self.colors["bg"])
        cards_frame.pack(fill=tk.X, padx=10, pady=10)
        cards_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.gpu_usage_label = self._build_info_card(cards_frame, "GPU 使用率", 0, 0)
        self.gpu_mem_usage_label = self._build_info_card(cards_frame, "显存使用率", 0, 1)
        self.gpu_temp_label = self._build_info_card(cards_frame, "温度", 0, 2)
        self.gpu_power_label = self._build_info_card(cards_frame, "功耗", 0, 3)

        # 显存详情
        mem_frame = tk.LabelFrame(
            tab, text=" 显存 ",
            bg=self.colors["card_bg"], fg=self.colors["text"],
            font=("Microsoft YaHei UI", 10),
            padx=10, pady=10
        )
        mem_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.gpu_mem_progress = ttk.Progressbar(
            mem_frame, style="Custom.Horizontal.TProgressbar",
            length=400, mode="determinate"
        )
        self.gpu_mem_progress.pack(fill=tk.X, pady=5)

        self.gpu_mem_detail_label = tk.Label(
            mem_frame, text="",
            bg=self.colors["card_bg"], fg=self.colors["text_dim"],
            font=("Microsoft YaHei UI", 9)
        )
        self.gpu_mem_detail_label.pack(anchor="w")

        # 趋势图
        self.gpu_chart = RealtimeChart(
            tab, title="GPU 使用率趋势", y_label="%",
            y_max=100,
            line_labels=["GPU", "显存"],
            line_colors=[self.colors["accent"], self.colors["orange"]],
            figsize=(8, 2.5)
        )
        self.gpu_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    # ==================== 网络标签页 ====================

    def _build_network_tab(self):
        """网络标签页"""
        tab = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(tab, text="  网络  ")

        # 信息卡片
        cards_frame = tk.Frame(tab, bg=self.colors["bg"])
        cards_frame.pack(fill=tk.X, padx=10, pady=10)
        cards_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.net_upload_label = self._build_info_card(cards_frame, "上传速度", 0, 0)
        self.net_download_label = self._build_info_card(cards_frame, "下载速度", 0, 1)
        self.net_sent_label = self._build_info_card(cards_frame, "总上传量", 0, 2)
        self.net_recv_label = self._build_info_card(cards_frame, "总下载量", 0, 3)

        # 趋势图
        self.net_chart = RealtimeChart(
            tab, title="网络流量趋势", y_label="KB/s",
            y_max=None,
            line_labels=["上传", "下载"],
            line_colors=[self.colors["orange"], self.colors["accent"]],
            figsize=(8, 3)
        )
        self.net_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    # ==================== 进程标签页 ====================

    def _build_process_tab(self):
        """进程标签页"""
        tab = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(tab, text="  进程  ")

        # 工具栏
        toolbar = tk.Frame(tab, bg=self.colors["bg"])
        toolbar.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            toolbar, text="进程列表（按内存排序）",
            bg=self.colors["bg"], fg=self.colors["text"],
            font=("Microsoft YaHei UI", 10)
        ).pack(side=tk.LEFT)

        kill_btn = ttk.Button(
            toolbar, text="终止选中进程",
            style="Danger.TButton",
            command=self._kill_selected_process
        )
        kill_btn.pack(side=tk.RIGHT)

        refresh_btn = ttk.Button(
            toolbar, text="刷新",
            command=self._refresh_processes
        )
        refresh_btn.pack(side=tk.RIGHT, padx=(0, 10))

        # 进程表格
        tree_frame = tk.Frame(tab, bg=self.colors["card_bg"])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        columns = ("PID", "名称", "CPU%", "内存%", "内存(MB)", "状态", "用户")
        self.process_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        widths = [60, 200, 70, 70, 90, 80, 150]
        for col, w in zip(columns, widths):
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=w, anchor="center")

        scrollbar_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.process_tree.yview)
        scrollbar_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.process_tree.xview)
        self.process_tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.process_tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

    # ==================== 数据刷新 ====================

    def _refresh_data(self):
        """刷新所有监控数据"""
        if not self._running:
            return

        try:
            self._update_cpu()
            self._update_memory()
            self._update_disk()
            self._update_gpu()
            self._update_network()
            self._update_processes()
        except Exception as e:
            print(f"刷新数据出错: {e}")

        self.root.after(self.REFRESH_INTERVAL, self._refresh_data)

    def _update_cpu(self):
        """更新 CPU 数据"""
        cpu = self.monitor.get_cpu()

        color = self._get_usage_color(cpu.overall)
        self.cpu_overall_label.config(text=f"{cpu.overall:.1f}%", fg=color)
        self.cpu_freq_label.config(text=f"{cpu.freq_current:.0f} MHz")
        self.cpu_cores_label.config(text=f"{cpu.core_count} 核")

        if not self.cpu_core_bars:
            cols = min(cpu.core_count, 4)
            for i in range(cpu.core_count):
                row, col = divmod(i, cols)
                frame = tk.Frame(self.cpu_core_frames, bg=self.colors["card_bg"])
                frame.grid(row=row, column=col, padx=5, pady=2, sticky="ew")

                tk.Label(
                    frame, text=f"核心{i}",
                    bg=self.colors["card_bg"], fg=self.colors["text_dim"],
                    font=("Microsoft YaHei UI", 8), width=6
                ).pack(side=tk.LEFT)

                bar = ttk.Progressbar(
                    frame, style="Custom.Horizontal.TProgressbar",
                    length=150, mode="determinate"
                )
                bar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

                label = tk.Label(
                    frame, text="0%",
                    bg=self.colors["card_bg"], fg=self.colors["text"],
                    font=("Microsoft YaHei UI", 8), width=5
                )
                label.pack(side=tk.RIGHT)

                self.cpu_core_bars.append((bar, label))
                self.cpu_core_frames.grid_columnconfigure(col, weight=1)

        for i, (bar, label) in enumerate(self.cpu_core_bars):
            if i < len(cpu.per_core):
                bar["value"] = cpu.per_core[i]
                label.config(text=f"{cpu.per_core[i]:.0f}%")

        self.cpu_chart.update_data([cpu.overall])

    def _update_memory(self):
        """更新内存数据"""
        mem = self.monitor.get_memory()

        color = self._get_usage_color(mem.percent)
        self.mem_percent_label.config(text=f"{mem.percent:.1f}%", fg=color)
        self.mem_used_label.config(text=self.monitor.format_bytes(mem.used))
        self.mem_available_label.config(text=self.monitor.format_bytes(mem.available))
        self.mem_total_label.config(text=self.monitor.format_bytes(mem.total))

        self.mem_progress["value"] = mem.percent
        self.mem_bar_label.config(
            text=f"{self.monitor.format_bytes(mem.used)} / {self.monitor.format_bytes(mem.total)}"
        )

        self.mem_chart.update_data([mem.percent])

    def _update_disk(self):
        """更新磁盘数据"""
        disk = self.monitor.get_disk()

        self.disk_read_label.config(text=self.monitor.format_bytes(disk.read_speed) + "/s")
        self.disk_write_label.config(text=self.monitor.format_bytes(disk.write_speed) + "/s")

        self.disk_tree.delete(*self.disk_tree.get_children())
        for part in disk.partitions:
            self.disk_tree.insert("", tk.END, values=(
                part["device"],
                part["mountpoint"],
                part["fstype"],
                self.monitor.format_bytes(part["total"]),
                self.monitor.format_bytes(part["used"]),
                self.monitor.format_bytes(part["free"]),
                f"{part['percent']:.1f}%",
            ))

    def _update_gpu(self):
        """更新显卡数据"""
        stats = self.gpu_monitor.get_stats()

        color = self._get_usage_color(stats.gpu_usage)
        self.gpu_usage_label.config(text=f"{stats.gpu_usage:.0f}%", fg=color)
        self.gpu_temp_label.config(
            text=f"{stats.temperature:.0f}°C" if stats.temperature > 0 else "--"
        )
        self.gpu_power_label.config(
            text=f"{stats.power:.0f} W" if stats.power > 0 else "--"
        )
        self.gpu_mem_usage_label.config(
            text=f"{stats.memory_usage:.0f}%" if stats.memory_usage > 0 else "--"
        )

        # 显存进度条
        if stats.memory_usage > 0:
            self.gpu_mem_progress["value"] = stats.memory_usage
            self.gpu_mem_detail_label.config(
                text=f"{stats.memory_used} / {stats.memory_total}"
            )

        # 趋势图
        self.gpu_chart.update_data([stats.gpu_usage, stats.memory_usage])

    def _update_network(self):
        """更新网络数据"""
        net = self.monitor.get_network()

        self.net_upload_label.config(text=self.monitor.format_bytes(net.upload_speed) + "/s")
        self.net_download_label.config(text=self.monitor.format_bytes(net.download_speed) + "/s")
        self.net_sent_label.config(text=self.monitor.format_bytes(net.bytes_sent))
        self.net_recv_label.config(text=self.monitor.format_bytes(net.bytes_recv))

        self.net_chart.update_data([
            net.upload_speed / 1024,
            net.download_speed / 1024,
        ])

    def _update_processes(self):
        """更新进程列表"""
        if self.notebook.index(self.notebook.select()) != 6:
            return
        self._refresh_processes()

    def _refresh_processes(self):
        """手动刷新进程列表"""
        processes = self.monitor.get_processes(top_n=50)

        self.process_tree.delete(*self.process_tree.get_children())
        for proc in processes:
            self.process_tree.insert("", tk.END, values=(
                proc.pid,
                proc.name,
                f"{proc.cpu_percent:.1f}",
                f"{proc.memory_percent:.1f}",
                f"{proc.memory_mb:.1f}",
                proc.status,
                proc.username,
            ))

    def _kill_selected_process(self):
        """终止选中的进程"""
        selected = self.process_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择一个进程")
            return

        item = self.process_tree.item(selected[0])
        pid = int(item["values"][0])
        name = item["values"][1]

        if messagebox.askyesno("确认", f"确定要终止进程 {name} (PID: {pid}) 吗？"):
            if SystemMonitor.kill_process(pid):
                messagebox.showinfo("成功", f"进程 {name} 已终止")
                self._refresh_processes()
            else:
                messagebox.showerror("失败", f"无法终止进程 {name}，可能权限不足")

    @staticmethod
    def _get_usage_color(percent: float) -> str:
        """根据使用率返回颜色"""
        if percent < 60:
            return "#66BB6A"
        elif percent < 85:
            return "#FFA726"
        else:
            return "#EF5350"

    def run(self):
        """启动主循环"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        """关闭窗口"""
        self._running = False
        self.root.destroy()
