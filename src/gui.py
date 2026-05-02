"""
系统监控工具 v2.0 - GUI 主窗口

支持中英文切换。
"""
import tkinter as tk
from tkinter import ttk, messagebox

from .monitor import SystemMonitor
from .hardware import HardwareCollector
from .gpu_monitor import GpuMonitor
from .charts import RealtimeChart, HAS_MATPLOTLIB
from .i18n import get_text, LANGUAGES


class MainWindow:
    REFRESH_INTERVAL = 1000

    def __init__(self):
        self.lang = "zh"
        self.monitor = SystemMonitor(history_size=120)
        self.hw = HardwareCollector()
        self.gpu_monitor = GpuMonitor()

        self._cpu_detail = self.hw.get_cpu_detail()
        self._mem_detail = self.hw.get_memory_detail()
        self._disk_details = self.hw.get_disk_details()
        self._gpu_details = self.hw.get_gpu_details()
        self._sys_info = self.hw.get_system_info()
        self._mb_info = self.hw.get_motherboard()
        self._bios_info = self.hw.get_bios()
        self._net_adapters = self.hw.get_network_adapters()

        self.root = tk.Tk()
        self.root.geometry("950x700")
        self.root.minsize(850, 650)

        self.colors = {
            "bg": "#1e1e1e", "card_bg": "#2d2d2d",
            "text": "#ffffff", "text_dim": "#888888",
            "accent": "#4FC3F7", "green": "#66BB6A",
            "orange": "#FFA726", "red": "#EF5350",
            "progress_bg": "#404040",
        }
        self.root.configure(bg=self.colors["bg"])

        default_font = ("Microsoft YaHei UI", 10)
        self.root.option_add("*Font", default_font)
        self.root.option_add("*TNotebook.Tab.Font", ("Microsoft YaHei UI", 10))
        self.root.option_add("*TButton.Font", ("Microsoft YaHei UI", 9))
        self.root.option_add("*TLabel.Font", ("Microsoft YaHei UI", 10))
        self.root.option_add("*Treeview.Heading.Font", ("Microsoft YaHei UI", 9, "bold"))
        self.root.option_add("*Treeview.Font", ("Microsoft YaHei UI", 9))

        self._setup_styles()

        self._widgets = {}
        self.cpu_core_bars = []

        self._build_header()
        self._build_notebook()

        self._running = True
        self._refresh_data()
        self._apply_texts()

    def _t(self, key, **kwargs):
        return get_text(self.lang, key, **kwargs)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=self.colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=self.colors["card_bg"],
                        foreground=self.colors["text"], padding=[15, 8])
        style.map("TNotebook.Tab",
                  background=[("selected", self.colors["accent"])],
                  foreground=[("selected", "#ffffff")])
        style.configure("Custom.Horizontal.TProgressbar",
                        background=self.colors["accent"],
                        troughcolor=self.colors["progress_bg"],
                        borderwidth=0, lightcolor=self.colors["accent"],
                        darkcolor=self.colors["accent"])
        style.configure("Danger.TButton", background=self.colors["red"],
                        foreground="#ffffff")

    def _build_header(self):
        header = tk.Frame(self.root, bg=self.colors["card_bg"], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        self._widgets["title"] = tk.Label(
            header, bg=self.colors["card_bg"], fg=self.colors["text"],
            font=("Microsoft YaHei UI", 14, "bold"))
        self._widgets["title"].pack(side=tk.LEFT, padx=15)

        self._widgets["os_label"] = tk.Label(
            header, bg=self.colors["card_bg"], fg=self.colors["text_dim"],
            font=("Microsoft YaHei UI", 9))
        self._widgets["os_label"].pack(side=tk.RIGHT, padx=15)

        self._widgets["status"] = tk.Label(
            header, bg=self.colors["card_bg"], fg=self.colors["green"],
            font=("Microsoft YaHei UI", 10))
        self._widgets["status"].pack(side=tk.RIGHT, padx=10)

        # 语言切换按钮
        self._lang_btn = tk.Button(
            header, font=("Microsoft YaHei UI", 10, "bold"),
            bg=self.colors["accent"], fg="#ffffff",
            relief="flat", cursor="hand2", width=3,
            command=self._switch_language)
        self._lang_btn.pack(side=tk.RIGHT, padx=5, pady=10)

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._build_info_tab()
        self._build_cpu_tab()
        self._build_memory_tab()
        self._build_disk_tab()
        self._build_gpu_tab()
        self._build_network_tab()
        self._build_process_tab()

    def _card(self, parent, title_key, row, col):
        card = tk.Frame(parent, bg=self.colors["card_bg"], padx=15, pady=10)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        lbl_title = tk.Label(card, bg=self.colors["card_bg"], fg=self.colors["text_dim"],
                             font=("Microsoft YaHei UI", 9))
        lbl_title.pack(anchor="w")
        lbl_val = tk.Label(card, text="--", bg=self.colors["card_bg"],
                           fg=self.colors["text"], font=("Microsoft YaHei UI", 18, "bold"))
        lbl_val.pack(anchor="w", pady=(5, 0))
        key = f"card_{title_key}_{row}_{col}"
        self._widgets[f"{key}_title"] = lbl_title
        self._widgets[f"{key}_title_key"] = title_key
        return lbl_val

    def _info_row(self, parent, label_key, value, row):
        lbl = tk.Label(parent, bg=self.colors["card_bg"], fg=self.colors["text_dim"],
                       font=("Microsoft YaHei UI", 10), anchor="e", width=14)
        lbl.grid(row=row, column=0, padx=(15, 10), pady=4, sticky="e")
        val_lbl = tk.Label(parent, text=value, bg=self.colors["card_bg"],
                           fg=self.colors["text"], font=("Microsoft YaHei UI", 10), anchor="w")
        val_lbl.grid(row=row, column=1, padx=(0, 15), pady=4, sticky="w")
        key = f"info_row_{label_key}_{row}"
        self._widgets[key] = lbl
        self._widgets[f"{key}_key"] = label_key
        return val_lbl

    def _section(self, parent, title_key, fg=None):
        frame = tk.LabelFrame(parent, bg=self.colors["card_bg"],
                              fg=fg or self.colors["accent"],
                              font=("Microsoft YaHei UI", 11, "bold"),
                              padx=10, pady=10)
        key = f"section_{title_key}_{id(frame)}"
        self._widgets[key] = frame
        self._widgets[f"{key}_key"] = title_key
        return frame

    # ==================== 系统信息 ====================
    def _build_info_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors["bg"])

        canvas = tk.Canvas(tab, bg=self.colors["bg"], highlightthickness=0)
        sb = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=canvas.yview)
        sf = tk.Frame(canvas, bg=self.colors["bg"])
        sf.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=sf, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        self._info_tab_frame = sf

        # 左右两列容器
        columns = tk.Frame(sf, bg=self.colors["bg"])
        columns.pack(fill=tk.X, padx=15, pady=15)
        columns.columnconfigure(0, weight=1)
        columns.columnconfigure(1, weight=1)

        left = tk.Frame(columns, bg=self.colors["bg"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right = tk.Frame(columns, bg=self.colors["bg"])
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        # === 左列 ===

        # OS
        sys_f = self._section(left, "os_section")
        sys_f.pack(fill=tk.X, pady=(0, 8))
        sys_f.grid_columnconfigure(1, weight=1)
        self._info_row(sys_f, "hostname", self._sys_info.hostname, 0)
        self._info_row(sys_f, "os_name", f"{self._sys_info.os_name} {self._sys_info.os_version}", 1)
        self._info_row(sys_f, "os_arch", self._sys_info.os_arch, 2)
        # 运行时间
        self._uptime_val = self._info_row(sys_f, "uptime", self._sys_info.uptime, 3)

        # CPU
        cpu = self._cpu_detail
        cpu_f = self._section(left, "cpu_section")
        cpu_f.pack(fill=tk.X, pady=(0, 8))
        cpu_f.grid_columnconfigure(1, weight=1)
        r = 0
        self._info_row(cpu_f, "cpu_model", cpu.name, r); r += 1
        self._info_row(cpu_f, "cpu_arch", cpu.architecture, r); r += 1
        self._info_row(cpu_f, "cpu_physical_cores", f"{cpu.physical_cores}", r); r += 1
        self._info_row(cpu_f, "cpu_logical_cores", f"{cpu.logical_cores}", r); r += 1
        self._info_row(cpu_f, "cpu_max_freq", f"{cpu.max_freq:.0f} MHz", r); r += 1
        if cpu.l2_cache:
            self._info_row(cpu_f, "cpu_l2_cache", cpu.l2_cache, r); r += 1
        if cpu.l3_cache:
            self._info_row(cpu_f, "cpu_l3_cache", cpu.l3_cache, r); r += 1

        # Memory
        mem = self._mem_detail
        mem_f = self._section(left, "memory_section")
        mem_f.pack(fill=tk.X, pady=(0, 8))
        mem_f.grid_columnconfigure(1, weight=1)
        r = 0
        self._info_row(mem_f, "mem_total", HardwareCollector.format_bytes(mem.total), r); r += 1
        if mem.type:
            self._info_row(mem_f, "mem_type", mem.type, r); r += 1
        if mem.speed:
            self._info_row(mem_f, "mem_speed", mem.speed, r); r += 1
        self._info_row(mem_f, "mem_slots", f"{len(mem.slots)}", r); r += 1
        for i, slot in enumerate(mem.slots):
            cap = HardwareCollector.format_bytes(slot.get("capacity", 0))
            part = slot.get("part_number", "")
            mfr = slot.get("manufacturer", "")
            self._info_row(mem_f, f"slot_{i}", f"{cap}  {part}  {mfr}", r); r += 1

        # === 右列 ===

        # Motherboard
        mb = self._mb_info
        mb_f = self._section(right, "mb_section")
        mb_f.pack(fill=tk.X, pady=(0, 8))
        mb_f.grid_columnconfigure(1, weight=1)
        self._info_row(mb_f, "mb_manufacturer", mb.manufacturer or "N/A", 0)
        self._info_row(mb_f, "mb_product", mb.product or "N/A", 1)

        # BIOS
        bios = self._bios_info
        bios_f = self._section(right, "bios_section")
        bios_f.pack(fill=tk.X, pady=(0, 8))
        bios_f.grid_columnconfigure(1, weight=1)
        self._info_row(bios_f, "bios_manufacturer", bios.manufacturer or "N/A", 0)
        self._info_row(bios_f, "bios_version", bios.version or "N/A", 1)
        self._info_row(bios_f, "bios_date", bios.date or "N/A", 2)

        # Disk
        disk_f = self._section(right, "disk_section")
        disk_f.pack(fill=tk.X, pady=(0, 8))
        disk_f.grid_columnconfigure(1, weight=1)
        r = 0
        for i, d in enumerate(self._disk_details):
            self._info_row(disk_f, f"disk_{i}_model", d.model or "N/A", r); r += 1
            self._info_row(disk_f, f"disk_{i}_cap",
                           HardwareCollector.format_bytes(d.size) if d.size else "N/A", r); r += 1
            self._info_row(disk_f, f"disk_{i}_iface", d.interface or "N/A", r); r += 1

        # GPU
        gpu_f = self._section(right, "gpu_section")
        gpu_f.pack(fill=tk.X, pady=(0, 8))
        gpu_f.grid_columnconfigure(1, weight=1)
        r = 0
        for i, g in enumerate(self._gpu_details):
            self._info_row(gpu_f, f"gpu_{i}", g.name, r); r += 1
            if g.memory:
                self._info_row(gpu_f, f"gpu_{i}_mem", g.memory, r); r += 1

        # Network Adapters
        net_f = self._section(right, "net_section")
        net_f.pack(fill=tk.X, pady=(0, 8))
        net_f.grid_columnconfigure(1, weight=1)
        r = 0
        for i, adapter in enumerate(self._net_adapters):
            self._info_row(net_f, f"net_{i}", adapter.name, r); r += 1
            if adapter.mac:
                self._info_row(net_f, f"net_{i}_mac", adapter.mac, r); r += 1
            if adapter.speed:
                self._info_row(net_f, f"net_{i}_speed", adapter.speed, r); r += 1

        self.notebook.add(tab, text="")

    # ==================== CPU ====================
    def _build_cpu_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors["bg"])

        self._widgets["cpu_model_bar"] = tk.Frame(tab, bg=self.colors["card_bg"], height=30)
        self._widgets["cpu_model_bar"].pack(fill=tk.X, padx=10, pady=(10, 0))
        self._widgets["cpu_model_bar"].pack_propagate(False)
        self._widgets["cpu_model_text"] = tk.Label(
            self._widgets["cpu_model_bar"], bg=self.colors["card_bg"],
            fg=self.colors["text_dim"], font=("Microsoft YaHei UI", 9))
        self._widgets["cpu_model_text"].pack(side=tk.LEFT, padx=10)

        cards = tk.Frame(tab, bg=self.colors["bg"])
        cards.pack(fill=tk.X, padx=10, pady=10)
        cards.columnconfigure((0, 1, 2), weight=1)
        self._widgets["cpu_overall"] = self._card(cards, "cpu_overall", 0, 0)
        self._widgets["cpu_freq"] = self._card(cards, "cpu_freq", 0, 1)
        self._widgets["cpu_cores"] = self._card(cards, "cpu_cores", 0, 2)

        self._cpu_cores_frame = tk.LabelFrame(
            tab, bg=self.colors["card_bg"], fg=self.colors["text"],
            font=("Microsoft YaHei UI", 10), padx=10, pady=10)
        self._cpu_cores_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        self._widgets["cpu_cores_section"] = self._cpu_cores_frame

        self.cpu_chart = RealtimeChart(
            tab, y_label="%", y_max=100, line_labels=["CPU"],
            line_colors=[self.colors["accent"]], figsize=(8, 2.5))
        self.cpu_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.notebook.add(tab, text="")

    # ==================== Memory ====================
    def _build_memory_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors["bg"])

        self._widgets["mem_model_bar"] = tk.Frame(tab, bg=self.colors["card_bg"], height=30)
        self._widgets["mem_model_bar"].pack(fill=tk.X, padx=10, pady=(10, 0))
        self._widgets["mem_model_bar"].pack_propagate(False)
        self._widgets["mem_model_text"] = tk.Label(
            self._widgets["mem_model_bar"], bg=self.colors["card_bg"],
            fg=self.colors["text_dim"], font=("Microsoft YaHei UI", 9))
        self._widgets["mem_model_text"].pack(side=tk.LEFT, padx=10)

        cards = tk.Frame(tab, bg=self.colors["bg"])
        cards.pack(fill=tk.X, padx=10, pady=10)
        cards.columnconfigure((0, 1, 2, 3), weight=1)
        self._widgets["mem_percent"] = self._card(cards, "mem_usage", 0, 0)
        self._widgets["mem_used"] = self._card(cards, "mem_used", 0, 1)
        self._widgets["mem_avail"] = self._card(cards, "mem_available", 0, 2)
        self._widgets["mem_total"] = self._card(cards, "mem_total_card", 0, 3)

        bar_f = tk.LabelFrame(tab, bg=self.colors["card_bg"], fg=self.colors["text"],
                              font=("Microsoft YaHei UI", 10), padx=10, pady=10)
        bar_f.pack(fill=tk.X, padx=10, pady=(0, 10))
        self._widgets["mem_bar_section"] = bar_f

        self.mem_progress = ttk.Progressbar(bar_f, style="Custom.Horizontal.TProgressbar",
                                            length=400, mode="determinate")
        self.mem_progress.pack(fill=tk.X, pady=5)
        self._widgets["mem_bar_label"] = tk.Label(bar_f, bg=self.colors["card_bg"],
                                                   fg=self.colors["text_dim"],
                                                   font=("Microsoft YaHei UI", 9))
        self._widgets["mem_bar_label"].pack(anchor="w")

        self.mem_chart = RealtimeChart(
            tab, y_label="%", y_max=100, line_labels=["MEM"],
            line_colors=[self.colors["green"]], figsize=(8, 2.5))
        self.mem_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.notebook.add(tab, text="")

    # ==================== Disk ====================
    def _build_disk_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors["bg"])

        self._widgets["disk_model_bar"] = tk.Frame(tab, bg=self.colors["card_bg"], height=30)
        self._widgets["disk_model_bar"].pack(fill=tk.X, padx=10, pady=(10, 0))
        self._widgets["disk_model_bar"].pack_propagate(False)
        self._widgets["disk_model_text"] = tk.Label(
            self._widgets["disk_model_bar"], bg=self.colors["card_bg"],
            fg=self.colors["text_dim"], font=("Microsoft YaHei UI", 9))
        self._widgets["disk_model_text"].pack(side=tk.LEFT, padx=10)

        cards = tk.Frame(tab, bg=self.colors["bg"])
        cards.pack(fill=tk.X, padx=10, pady=10)
        cards.columnconfigure((0, 1), weight=1)
        self._widgets["disk_read"] = self._card(cards, "disk_read", 0, 0)
        self._widgets["disk_write"] = self._card(cards, "disk_write", 0, 1)

        part_f = tk.LabelFrame(tab, bg=self.colors["card_bg"], fg=self.colors["text"],
                               font=("Microsoft YaHei UI", 10), padx=10, pady=10)
        part_f.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self._widgets["disk_part_section"] = part_f

        cols = ("col_device", "col_mount", "col_fstype", "col_total", "col_used", "col_free", "col_percent")
        self._disk_cols = cols
        self.disk_tree = ttk.Treeview(part_f, columns=cols, show="headings", height=6)
        for c in cols:
            self.disk_tree.heading(c, text=self._t(c))
            self.disk_tree.column(c, width=100, anchor="center")
        sb = ttk.Scrollbar(part_f, orient=tk.VERTICAL, command=self.disk_tree.yview)
        self.disk_tree.configure(yscrollcommand=sb.set)
        self.disk_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        self.notebook.add(tab, text="")

    # ==================== GPU ====================
    def _build_gpu_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors["bg"])

        vendor = self.gpu_monitor._vendor
        gpu_name = self.gpu_monitor._gpu_name
        self._widgets["gpu_model_bar"] = tk.Frame(tab, bg=self.colors["card_bg"], height=30)
        self._widgets["gpu_model_bar"].pack(fill=tk.X, padx=10, pady=(10, 0))
        self._widgets["gpu_model_bar"].pack_propagate(False)
        self._widgets["gpu_model_text"] = tk.Label(
            self._widgets["gpu_model_bar"], bg=self.colors["card_bg"],
            fg=self.colors["text_dim"], font=("Microsoft YaHei UI", 9))
        self._widgets["gpu_model_text"].pack(side=tk.LEFT, padx=10)

        cards = tk.Frame(tab, bg=self.colors["bg"])
        cards.pack(fill=tk.X, padx=10, pady=10)
        cards.columnconfigure((0, 1, 2, 3), weight=1)
        self._widgets["gpu_usage"] = self._card(cards, "gpu_usage", 0, 0)
        self._widgets["gpu_mem"] = self._card(cards, "gpu_mem_usage", 0, 1)
        self._widgets["gpu_temp"] = self._card(cards, "gpu_temp", 0, 2)
        self._widgets["gpu_power"] = self._card(cards, "gpu_power", 0, 3)

        mem_f = tk.LabelFrame(tab, bg=self.colors["card_bg"], fg=self.colors["text"],
                              font=("Microsoft YaHei UI", 10), padx=10, pady=10)
        mem_f.pack(fill=tk.X, padx=10, pady=(0, 10))
        self._widgets["gpu_vram_section"] = mem_f
        self.gpu_mem_progress = ttk.Progressbar(mem_f, style="Custom.Horizontal.TProgressbar",
                                                length=400, mode="determinate")
        self.gpu_mem_progress.pack(fill=tk.X, pady=5)
        self._widgets["gpu_mem_detail"] = tk.Label(mem_f, bg=self.colors["card_bg"],
                                                    fg=self.colors["text_dim"],
                                                    font=("Microsoft YaHei UI", 9))
        self._widgets["gpu_mem_detail"].pack(anchor="w")

        self.gpu_chart = RealtimeChart(
            tab, y_label="%", y_max=100,
            line_labels=["GPU", "VRAM"],
            line_colors=[self.colors["accent"], self.colors["orange"]], figsize=(8, 2.5))
        self.gpu_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.notebook.add(tab, text="")

    # ==================== Network ====================
    def _build_network_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors["bg"])

        cards = tk.Frame(tab, bg=self.colors["bg"])
        cards.pack(fill=tk.X, padx=10, pady=10)
        cards.columnconfigure((0, 1, 2, 3), weight=1)
        self._widgets["net_upload"] = self._card(cards, "net_upload", 0, 0)
        self._widgets["net_download"] = self._card(cards, "net_download", 0, 1)
        self._widgets["net_sent"] = self._card(cards, "net_sent", 0, 2)
        self._widgets["net_recv"] = self._card(cards, "net_recv", 0, 3)

        self.net_chart = RealtimeChart(
            tab, y_label="KB/s", y_max=None,
            line_labels=["Upload", "Download"],
            line_colors=[self.colors["orange"], self.colors["accent"]], figsize=(8, 3))
        self.net_chart.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.notebook.add(tab, text="")

    # ==================== Process ====================
    def _build_process_tab(self):
        tab = tk.Frame(self.notebook, bg=self.colors["bg"])

        toolbar = tk.Frame(tab, bg=self.colors["bg"])
        toolbar.pack(fill=tk.X, padx=10, pady=10)

        self._widgets["proc_title"] = tk.Label(
            toolbar, bg=self.colors["bg"], fg=self.colors["text"],
            font=("Microsoft YaHei UI", 10))
        self._widgets["proc_title"].pack(side=tk.LEFT)

        self._widgets["proc_kill"] = ttk.Button(
            toolbar, style="Danger.TButton", command=self._kill_process)
        self._widgets["proc_kill"].pack(side=tk.RIGHT)

        self._widgets["proc_refresh"] = ttk.Button(toolbar, command=self._refresh_processes)
        self._widgets["proc_refresh"].pack(side=tk.RIGHT, padx=(0, 10))

        tree_f = tk.Frame(tab, bg=self.colors["card_bg"])
        tree_f.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self._proc_cols = ("col_pid", "col_name", "col_cpu_pct", "col_mem_pct",
                           "col_mem_mb", "col_status", "col_user")
        self.process_tree = ttk.Treeview(tree_f, columns=self._proc_cols, show="headings")
        widths = [60, 200, 70, 70, 90, 80, 150]
        for c, w in zip(self._proc_cols, widths):
            self.process_tree.heading(c, text=self._t(c))
            self.process_tree.column(c, width=w, anchor="center")

        sb_y = ttk.Scrollbar(tree_f, orient=tk.VERTICAL, command=self.process_tree.yview)
        sb_x = ttk.Scrollbar(tree_f, orient=tk.HORIZONTAL, command=self.process_tree.xview)
        self.process_tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        self.process_tree.grid(row=0, column=0, sticky="nsew")
        sb_y.grid(row=0, column=1, sticky="ns")
        sb_x.grid(row=1, column=0, sticky="ew")
        tree_f.grid_rowconfigure(0, weight=1)
        tree_f.grid_columnconfigure(0, weight=1)

        self.notebook.add(tab, text="")

    # ==================== Language Switch ====================
    def _switch_language(self):
        self.lang = "en" if self.lang == "zh" else "zh"
        self._apply_texts()

    def _apply_texts(self):
        t = self._t
        self.root.title(t("window_title"))
        self._lang_btn.config(text=t("lang_switch"))
        self._widgets["title"].config(text=f"🖥 {t('window_title')}")
        self._widgets["os_label"].config(
            text=f"{self._sys_info.os_name} {self._sys_info.os_arch}")
        self._widgets["status"].config(text=t("running"))

        # Update uptime format based on language
        info = self._sys_info
        if info.uptime_days > 0:
            if self.lang == "zh":
                uptime_text = f"{info.uptime_days}天 {info.uptime_hours}时 {info.uptime_minutes}分"
            else:
                uptime_text = f"{info.uptime_days}d {info.uptime_hours}h {info.uptime_minutes}m"
        elif info.uptime_hours > 0:
            if self.lang == "zh":
                uptime_text = f"{info.uptime_hours}时 {info.uptime_minutes}分"
            else:
                uptime_text = f"{info.uptime_hours}h {info.uptime_minutes}m"
        else:
            if self.lang == "zh":
                uptime_text = f"{info.uptime_minutes}分 {info.uptime_seconds}秒"
            else:
                uptime_text = f"{info.uptime_minutes}m {info.uptime_seconds}s"
        if hasattr(self, '_uptime_val'):
            self._uptime_val.config(text=uptime_text)

        tabs = [t("tab_info"), t("tab_cpu"), t("tab_memory"), t("tab_disk"),
                t("tab_gpu"), t("tab_network"), t("tab_process")]
        for i, txt in enumerate(tabs):
            try:
                self.notebook.tab(i, text=txt)
            except Exception:
                pass

        for key, widget in self._widgets.items():
            if key.endswith("_key"):
                continue
            wkey = self._widgets.get(f"{key}_key")
            if wkey and key.endswith("_title"):
                try:
                    widget.config(text=t(wkey))
                except Exception:
                    pass
            elif wkey and key.startswith("info_row_"):
                try:
                    widget.config(text=t(wkey))
                except Exception:
                    pass
            elif wkey and key.startswith("section_"):
                try:
                    widget.config(text=t(wkey))
                except Exception:
                    pass

        # CPU tab
        cpu = self._cpu_detail
        self._widgets["cpu_model_text"].config(
            text=t("cpu_model_bar", name=cpu.name, cores=cpu.physical_cores,
                   threads=cpu.logical_cores, freq=f"{cpu.max_freq:.0f}"))

        cores_label = self._cpu_cores_frame
        try:
            cores_label.config(text=t("cpu_cores_usage"))
        except Exception:
            pass

        if not self.cpu_core_bars:
            cols = min(cpu.logical_cores, 4)
            for i in range(cpu.logical_cores):
                row, col = divmod(i, cols)
                frame = tk.Frame(self._cpu_cores_frame, bg=self.colors["card_bg"])
                frame.grid(row=row, column=col, padx=5, pady=2, sticky="ew")
                lbl = tk.Label(frame, bg=self.colors["card_bg"], fg=self.colors["text_dim"],
                               font=("Microsoft YaHei UI", 8), width=6)
                lbl.pack(side=tk.LEFT)
                bar = ttk.Progressbar(frame, style="Custom.Horizontal.TProgressbar",
                                      length=150, mode="determinate")
                bar.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                val = tk.Label(frame, text="0%", bg=self.colors["card_bg"],
                               fg=self.colors["text"], font=("Microsoft YaHei UI", 8), width=5)
                val.pack(side=tk.RIGHT)
                self.cpu_core_bars.append((bar, val, lbl))
                self._cpu_cores_frame.grid_columnconfigure(col, weight=1)

        for i, (bar, val, lbl) in enumerate(self.cpu_core_bars):
            lbl.config(text=t("cpu_core_label", n=i))

        # Memory tab
        mem = self._mem_detail
        self._widgets["mem_model_text"].config(
            text=t("mem_model_bar", type=mem.type or "", speed=mem.speed or "",
                   total=HardwareCollector.format_bytes(mem.total), slots=len(mem.slots)))
        try:
            self._widgets["mem_bar_section"].config(text=t("mem_bar"))
        except Exception:
            pass

        # Disk tab
        models = " | ".join(d.model for d in self._disk_details if d.model) or t("not_detected")
        self._widgets["disk_model_text"].config(text=models)
        for c in self._disk_cols:
            self.disk_tree.heading(c, text=t(c))
        try:
            self._widgets["disk_part_section"].config(text=t("disk_partitions"))
        except Exception:
            pass

        # GPU tab
        self._widgets["gpu_model_text"].config(
            text=t("gpu_model_bar", name=self.gpu_monitor._gpu_name,
                   vendor=self.gpu_monitor._vendor))
        try:
            self._widgets["gpu_vram_section"].config(text=t("gpu_vram_section"))
        except Exception:
            pass

        # Process tab
        self._widgets["proc_title"].config(text=t("process_title"))
        self._widgets["proc_kill"].config(text=t("process_kill"))
        self._widgets["proc_refresh"].config(text=t("process_refresh"))
        for c in self._proc_cols:
            self.process_tree.heading(c, text=t(c))

        # Chart titles + legend labels
        if hasattr(self, 'cpu_chart'):
            self.cpu_chart.update_labels(
                t("cpu_trend"), t("cpu_trend_y"),
                [t("cpu_trend_label")])
        if hasattr(self, 'mem_chart'):
            self.mem_chart.update_labels(
                t("mem_trend"), "%",
                [t("mem_trend_label")])
        if hasattr(self, 'gpu_chart'):
            self.gpu_chart.update_labels(
                t("gpu_trend"), "%",
                t("gpu_trend_labels"))
        if hasattr(self, 'net_chart'):
            self.net_chart.update_labels(
                t("net_trend"), t("net_trend_y"),
                t("net_trend_labels"))

    # ==================== Data Refresh ====================
    def _refresh_data(self):
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
            print(f"Error: {e}")
        self.root.after(self.REFRESH_INTERVAL, self._refresh_data)

    def _update_cpu(self):
        cpu = self.monitor.get_cpu()
        color = self._color(cpu.overall)
        self._widgets["cpu_overall"].config(text=f"{cpu.overall:.1f}%", fg=color)
        self._widgets["cpu_freq"].config(text=f"{cpu.freq_current:.0f} MHz")
        self._widgets["cpu_cores"].config(text=f"{cpu.core_count}")

        for i, (bar, val, lbl) in enumerate(self.cpu_core_bars):
            if i < len(cpu.per_core):
                bar["value"] = cpu.per_core[i]
                val.config(text=f"{cpu.per_core[i]:.0f}%")
        self.cpu_chart.update_data([cpu.overall])

    def _update_memory(self):
        mem = self.monitor.get_memory()
        color = self._color(mem.percent)
        self._widgets["mem_percent"].config(text=f"{mem.percent:.1f}%", fg=color)
        self._widgets["mem_used"].config(text=self.monitor.format_bytes(mem.used))
        self._widgets["mem_avail"].config(text=self.monitor.format_bytes(mem.available))
        self._widgets["mem_total"].config(text=self.monitor.format_bytes(mem.total))
        self.mem_progress["value"] = mem.percent
        self._widgets["mem_bar_label"].config(
            text=f"{self.monitor.format_bytes(mem.used)} / {self.monitor.format_bytes(mem.total)}")
        self.mem_chart.update_data([mem.percent])

    def _update_disk(self):
        disk = self.monitor.get_disk()
        self._widgets["disk_read"].config(text=self.monitor.format_bytes(disk.read_speed) + self._t("speed_unit"))
        self._widgets["disk_write"].config(text=self.monitor.format_bytes(disk.write_speed) + self._t("speed_unit"))
        self.disk_tree.delete(*self.disk_tree.get_children())
        for p in disk.partitions:
            self.disk_tree.insert("", tk.END, values=(
                p["device"], p["mountpoint"], p["fstype"],
                self.monitor.format_bytes(p["total"]),
                self.monitor.format_bytes(p["used"]),
                self.monitor.format_bytes(p["free"]),
                f"{p['percent']:.1f}%"))

    def _update_gpu(self):
        stats = self.gpu_monitor.get_stats()
        color = self._color(stats.gpu_usage)
        self._widgets["gpu_usage"].config(text=f"{stats.gpu_usage:.0f}%", fg=color)
        self._widgets["gpu_temp"].config(
            text=f"{stats.temperature:.0f}" + self._t("temp_unit") if stats.temperature > 0 else "--")
        self._widgets["gpu_power"].config(
            text=f"{stats.power:.0f}" + self._t("watt_unit") if stats.power > 0 else "--")
        self._widgets["gpu_mem"].config(
            text=f"{stats.memory_usage:.0f}%" if stats.memory_usage > 0 else "--")
        if stats.memory_usage > 0:
            self.gpu_mem_progress["value"] = stats.memory_usage
            self._widgets["gpu_mem_detail"].config(
                text=f"{stats.memory_used} / {stats.memory_total}")
        self.gpu_chart.update_data([stats.gpu_usage, stats.memory_usage])

    def _update_network(self):
        net = self.monitor.get_network()
        self._widgets["net_upload"].config(text=self.monitor.format_bytes(net.upload_speed) + self._t("speed_unit"))
        self._widgets["net_download"].config(text=self.monitor.format_bytes(net.download_speed) + self._t("speed_unit"))
        self._widgets["net_sent"].config(text=self.monitor.format_bytes(net.bytes_sent))
        self._widgets["net_recv"].config(text=self.monitor.format_bytes(net.bytes_recv))
        self.net_chart.update_data([net.upload_speed / 1024, net.download_speed / 1024])

    def _update_processes(self):
        if self.notebook.index(self.notebook.select()) != 6:
            return
        self._refresh_processes()

    def _refresh_processes(self):
        procs = self.monitor.get_processes(top_n=50)
        self.process_tree.delete(*self.process_tree.get_children())
        for p in procs:
            self.process_tree.insert("", tk.END, values=(
                p.pid, p.name, f"{p.cpu_percent:.1f}", f"{p.memory_percent:.1f}",
                f"{p.memory_mb:.1f}", p.status, p.username))

    def _kill_process(self):
        sel = self.process_tree.selection()
        if not sel:
            messagebox.showwarning(self._t("warning"), self._t("select_process"))
            return
        item = self.process_tree.item(sel[0])
        pid = int(item["values"][0])
        name = item["values"][1]
        if messagebox.askyesno(self._t("confirm"), self._t("kill_confirm", name=name, pid=pid)):
            if SystemMonitor.kill_process(pid):
                messagebox.showinfo(self._t("success"), self._t("kill_success", name=name))
                self._refresh_processes()
            else:
                messagebox.showerror(self._t("error"), self._t("kill_fail", name=name))

    @staticmethod
    def _color(pct):
        if pct < 60:
            return "#66BB6A"
        elif pct < 85:
            return "#FFA726"
        return "#EF5350"

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()

    def _on_close(self):
        self._running = False
        self.root.destroy()
