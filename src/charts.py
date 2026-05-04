"""
系统监控工具 - 图表组件

使用 matplotlib 绘制 CPU、内存、网络的实时趋势图。
"""
import tkinter as tk
from tkinter import ttk
from typing import List, Optional
from collections import deque

try:
    import matplotlib
    matplotlib.use("TkAgg")
    matplotlib.rcParams["font.sans-serif"] = ["Microsoft YaHei UI", "SimHei", "Arial"]
    matplotlib.rcParams["axes.unicode_minus"] = False
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class RealtimeChart(ttk.Frame):
    """
    实时趋势图组件
    
    可以显示一条或多条数据线的实时变化趋势。
    常用于 CPU 使用率、内存使用率、网络速度的监控。
    """

    def __init__(
        self,
        parent,
        title: str = "",
        y_label: str = "%",
        y_max: float = 100,
        line_labels: Optional[List[str]] = None,
        line_colors: Optional[List[str]] = None,
        figsize: tuple = (5, 2.5),
        x_label: str = None,
    ):
        """
        初始化图表
        
        Args:
            parent: 父容器
            title: 图表标题
            y_label: Y轴标签
            y_max: Y轴最大值（None则自动）
            line_labels: 数据线名称列表
            line_colors: 数据线颜色列表
            figsize: 图表尺寸
        """
        super().__init__(parent)

        if not HAS_MATPLOTLIB:
            ttk.Label(self, text="需要安装 matplotlib: pip install matplotlib").pack()
            return

        self.title = title
        self.y_label = y_label
        self.y_max = y_max
        self.line_labels = line_labels or ["数据"]
        self.line_colors = line_colors or ["#4FC3F7", "#FF7043", "#66BB6A", "#FFA726"]

        # 数据缓冲区
        self.data_buffers: List[deque] = [
            deque(maxlen=120) for _ in self.line_labels
        ]

        # 创建 matplotlib 图表
        self.figure = Figure(figsize=figsize, dpi=80, facecolor="#2b2b2b")
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor("#2b2b2b")

        # 设置坐标轴样式
        self.ax.tick_params(colors="white", labelsize=11)
        self.ax.set_title(title, color="white", fontsize=13, fontweight="bold")
        self.ax.set_ylabel(y_label, color="white", fontsize=12)
        self.x_label = x_label or "时间 (秒)"
        self.ax.set_xlabel(self.x_label, color="white", fontsize=12)

        for spine in self.ax.spines.values():
            spine.set_color("#555555")

        # 创建数据线
        self.lines = []
        for i, label in enumerate(self.line_labels):
            color = self.line_colors[i % len(self.line_colors)]
            line, = self.ax.plot([], [], color=color, linewidth=1.5, label=label)
            self.lines.append(line)

        if len(self.line_labels) > 1:
            self.ax.legend(loc="upper left", fontsize=14, facecolor="#333333",
                           edgecolor="#555555", labelcolor="white")

        self.ax.grid(True, alpha=0.2, color="white")

        # 嵌入 tkinter
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.figure.tight_layout(pad=1.0)
        self.figure.subplots_adjust(left=0.06, right=0.97, top=0.93, bottom=0.12)

    def update_data(self, values: List[float]):
        """
        更新图表数据
        
        Args:
            values: 每条数据线的最新值
        """
        if not HAS_MATPLOTLIB:
            return

        for i, val in enumerate(values):
            if i < len(self.data_buffers):
                self.data_buffers[i].append(val)

        # 更新数据线
        for i, line in enumerate(self.lines):
            if i < len(self.data_buffers):
                data = list(self.data_buffers[i])
                line.set_data(range(len(data)), data)

        # 动态调整X轴
        max_len = max(len(buf) for buf in self.data_buffers) if self.data_buffers else 0
        if max_len > 0:
            self.ax.set_xlim(0, max(max_len, 10))

        # Y轴
        if self.y_max is not None:
            self.ax.set_ylim(0, self.y_max)
        else:
            all_vals = [v for buf in self.data_buffers for v in buf]
            if all_vals:
                max_val = max(all_vals)
                self.ax.set_ylim(0, max(max_val * 1.2, 10))

        self.canvas.draw_idle()

    def update_labels(self, title: str, y_label: str, line_labels: List[str], x_label: str = None):
        """更新图表标题、Y轴标签和折线图例（用于语言切换）"""
        if not HAS_MATPLOTLIB:
            return
        self.ax.set_title(title, color="white", fontsize=13, fontweight="bold")
        self.ax.set_ylabel(y_label, color="white", fontsize=12)
        new_xlabel = x_label or self.x_label
        self.ax.set_xlabel(new_xlabel, color="white", fontsize=12)
        for i, line in enumerate(self.lines):
            if i < len(line_labels):
                line.set_label(line_labels[i])
        if len(line_labels) > 1:
            self.ax.legend(loc="upper left", fontsize=14, facecolor="#333333",
                           edgecolor="#555555", labelcolor="white")
        self.canvas.draw_idle()
