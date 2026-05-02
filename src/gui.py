"""
系统监控工具 - GUI 主窗口

使用 tkinter 构建的系统监控面板，包含 CPU、内存、磁盘、网络、进程五个标签页。
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

from .monitor import SystemMonitor
from .charts import RealtimeChart, HAS_MATPLOTLIB


class MainWindow:
    """
    系统监控主窗口
    
    功能：
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

        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("系统监控工具 v1.0")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)

        # 深色主题配色
        self.colors = {
            "bg": "#1e1e1e",           # 主背景
            "card_bg": "#2d2d2d",      # 卡片背景
            "text": "#ffffff",          # 主文字
            "text_dim": "#888888",      # 次要文字
            "accent": "#4FC3F7",        # 强调色（蓝色）
            "green": "#66BB6A",         # 绿色
            "orange": "#FFA726",        # 橙色
            "red": "#EF5350",           # 红色
            "progress_bg": "#404040",   # 进度条背景
        }

        self.root.configure(bg=self.colors["bg"])

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

        # 标签页样式
        style.configure("TNotebook", background=self.colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=self.colors["card_bg"],
                        foreground=self.colors["text"],
                        padding=[15, 8],
                        font=("微软雅黑", 10))
        style.map("TNotebook.Tab",
                  background=[("selected", self.colors["accent"])],
                  foreground=[("selected", "#ffffff")])

        # 进度条样式
        style.configure("Custom.Horizontal.TProgressbar",
                        background=self.colors["accent"],
                        troughcolor=self.colors["progress_bg"],
                        borderwidth=0,
                        lightcolor=self.colors["accent"],
                        darkcolor=self.colors["accent"])

        # 按钮样式
        style.configure("Danger.TButton",
                        background=self.colors["red"],
                        foreground="#ffffff",
                        font=("微软雅黑", 9))

    def _build_header(self):
        """构建顶部标题栏"""
        header = tk.Frame(self.root, bg=self.colors["card_bg"], height=50)
        header.pack(fill=tk.X, padx=0, pady=0)
        header.pack_propagate(False)

        # 标题
        tk.Label(
            header, text="🖥 系统监控工具",
            bg=self.colors["card_bg"], fg=self.colors["text"],
            font=("微软雅黑", 14, "bold")
        ).pack(side=tk.LEFT, padx=15)

        # 状态标签
        self.status_label = tk.Label(
            header, text="运行中",
            bg=self.colors["card_bg"], fg=self.colors["green"],
            font=("微软雅黑", 10)
        )
        self.status_label.pack(side=tk.RIGHT, padx=15)

    def _build_notebook(self):
        """构建标签页"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # CPU 标签页
        self._build_cpu_tab()

        # 内存标签页
        self._build_memory_tab()

        # 磁盘标签页
        self._build_disk_tab()

        # 网络标签页
        self._build_network_tab()

        # 进程标签页
        self._build_process_tab()

    def _build_info_card(self, parent, title: str, row: int, col: int):
        """创建信息卡片"""
        card = tk.Frame(parent, bg=self.colors["card_bg"], padx=15, pady=10)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        tk.Label(
            card, text=title,
            bg=self.colors["card_bg"], fg=self.colors["text_dim"],
            font=("微软雅黑", 9)
        ).pack(anchor="w")

        value_label = tk.Label(
            card, text="--",
            bg=self.colors["card_bg"], fg=self.colors["text"],
            font=("微软雅黑", 18, "bold")
        )
        value_label.pack(anchor="w", pady=(5, 0))

        return value_label

    def _build_cpu_tab(self):
        """CPU 标签页"""
        tab = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(tab, text="  CPU  ")

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
            font=("微软雅黑", 10),
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

    def _build_memory_tab(self):
        """内存标签页"""
        tab = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(tab, text="  内存  ")

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
            font=("微软雅黑", 10),
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
            font=("微软雅黑", 9)
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

    def _build_disk_tab(self):
        """磁盘标签页"""
        tab = tk.Frame(self.notebook, bg=self.colors["bg"])
        self.notebook.add(tab, text="  磁盘  ")

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
            font=("微软雅黑", 10),
            padx=10, pady=10
        )
        partitions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # 分区信息表格
        columns = ("设备", "挂载点", "文件系统", "总量", "已用", "可用", "使用率")
        self.disk_tree = ttk.Treeview(partitions_frame, columns=columns, show="headings", height=6)

        for col in columns:
            self.disk_tree.heading(col, text=col)
            self.disk_tree.column(col, width=100, anchor="center")

        scrollbar = ttk.Scrollbar(partitions_frame, orient=tk.VERTICAL, command=self.disk_tree.yview)
        self.disk_tree.configure(yscrollcommand=scrollbar.set)

        self.disk_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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
            font=("微软雅黑", 10)
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

    def _refresh_data(self):
        """刷新所有监控数据"""
        if not self._running:
            return

        try:
            self._update_cpu()
            self._update_memory()
            self._update_disk()
            self._update_network()
            self._update_processes()
        except Exception as e:
            print(f"刷新数据出错: {e}")

        # 安排下次刷新
        self.root.after(self.REFRESH_INTERVAL, self._refresh_data)

    def _update_cpu(self):
        """更新 CPU 数据"""
        cpu = self.monitor.get_cpu()

        # 信息卡片
        color = self._get_usage_color(cpu.overall)
        self.cpu_overall_label.config(text=f"{cpu.overall:.1f}%", fg=color)
        self.cpu_freq_label.config(text=f"{cpu.freq_current:.0f} MHz")
        self.cpu_cores_label.config(text=f"{cpu.core_count} 核")

        # 每核心进度条（只创建一次）
        if not self.cpu_core_bars:
            cols = min(cpu.core_count, 4)
            for i in range(cpu.core_count):
                row, col = divmod(i, cols)
                frame = tk.Frame(self.cpu_core_frames, bg=self.colors["card_bg"])
                frame.grid(row=row, column=col, padx=5, pady=2, sticky="ew")

                tk.Label(
                    frame, text=f"核心{i}",
                    bg=self.colors["card_bg"], fg=self.colors["text_dim"],
                    font=("微软雅黑", 8), width=6
                ).pack(side=tk.LEFT)

                bar = ttk.Progressbar(
                    frame, style="Custom.Horizontal.TProgressbar",
                    length=150, mode="determinate"
                )
                bar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

                label = tk.Label(
                    frame, text="0%",
                    bg=self.colors["card_bg"], fg=self.colors["text"],
                    font=("微软雅黑", 8), width=5
                )
                label.pack(side=tk.RIGHT)

                self.cpu_core_bars.append((bar, label))

                # 配置列权重
                self.cpu_core_frames.grid_columnconfigure(col, weight=1)

        # 更新核心进度条
        for i, (bar, label) in enumerate(self.cpu_core_bars):
            if i < len(cpu.per_core):
                bar["value"] = cpu.per_core[i]
                label.config(text=f"{cpu.per_core[i]:.0f}%")

        # 趋势图
        self.cpu_chart.update_data([cpu.overall])

    def _update_memory(self):
        """更新内存数据"""
        mem = self.monitor.get_memory()

        color = self._get_usage_color(mem.percent)
        self.mem_percent_label.config(text=f"{mem.percent:.1f}%", fg=color)
        self.mem_used_label.config(text=self.monitor.format_bytes(mem.used))
        self.mem_available_label.config(text=self.monitor.format_bytes(mem.available))
        self.mem_total_label.config(text=self.monitor.format_bytes(mem.total))

        # 进度条
        self.mem_progress["value"] = mem.percent
        self.mem_bar_label.config(
            text=f"{self.monitor.format_bytes(mem.used)} / {self.monitor.format_bytes(mem.total)}"
        )

        # 趋势图
        self.mem_chart.update_data([mem.percent])

    def _update_disk(self):
        """更新磁盘数据"""
        disk = self.monitor.get_disk()

        self.disk_read_label.config(text=self.monitor.format_bytes(disk.read_speed) + "/s")
        self.disk_write_label.config(text=self.monitor.format_bytes(disk.write_speed) + "/s")

        # 更新分区表格
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

    def _update_network(self):
        """更新网络数据"""
        net = self.monitor.get_network()

        self.net_upload_label.config(text=self.monitor.format_bytes(net.upload_speed) + "/s")
        self.net_download_label.config(text=self.monitor.format_bytes(net.download_speed) + "/s")
        self.net_sent_label.config(text=self.monitor.format_bytes(net.bytes_sent))
        self.net_recv_label.config(text=self.monitor.format_bytes(net.bytes_recv))

        # 趋势图（转换为 KB/s）
        self.net_chart.update_data([
            net.upload_speed / 1024,
            net.download_speed / 1024,
        ])

    def _update_processes(self):
        """更新进程列表"""
        # 只在进程标签页激活时刷新，节省资源
        if self.notebook.index(self.notebook.select()) != 4:
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
            return "#66BB6A"   # 绿色
        elif percent < 85:
            return "#FFA726"   # 橙色
        else:
            return "#EF5350"   # 红色

    def run(self):
        """启动主循环"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        """关闭窗口"""
        self._running = False
        self.root.destroy()
