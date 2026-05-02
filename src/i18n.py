"""
系统监控工具 - 国际化模块

支持中文/英文界面切换。
所有 UI 字符串集中管理，方便扩展其他语言。
"""


LANGUAGES = {
    "zh": {
        # 窗口标题
        "window_title": "系统监控工具 v2.0",
        "running": "● 运行中",

        # 标签页
        "tab_info": "  系统信息  ",
        "tab_cpu": "  CPU  ",
        "tab_memory": "  内存  ",
        "tab_disk": "  磁盘  ",
        "tab_gpu": "  显卡  ",
        "tab_network": "  网络  ",
        "tab_process": "  进程  ",

        # 系统信息页
        "os_section": "  操作系统  ",
        "cpu_section": "  处理器 (CPU)  ",
        "memory_section": "  内存 (RAM)  ",
        "disk_section": "  磁盘  ",
        "gpu_section": "  显卡 (GPU)  ",
        "mb_section": "  主板  ",
        "bios_section": "  BIOS  ",
        "net_section": "  网络适配器  ",
        "hostname": "主机名：",
        "os_name": "操作系统：",
        "os_arch": "系统架构：",
        "uptime": "运行时间：",
        "cpu_model": "型号：",
        "cpu_arch": "架构：",
        "cpu_physical_cores": "物理核心：",
        "cpu_logical_cores": "逻辑核心：",
        "cpu_max_freq": "最大频率：",
        "cpu_l2_cache": "L2 缓存：",
        "cpu_l3_cache": "L3 缓存：",
        "mem_total": "总容量：",
        "mem_type": "内存类型：",
        "mem_speed": "频率：",
        "mem_slots": "插槽数：",
        "disk_model": "磁盘 {n} 型号：",
        "disk_capacity": "  容量：",
        "disk_interface": "  接口：",
        "disk_media": "  介质：",
        "gpu_card": "显卡 {n}：",
        "gpu_vram": "  显存：",
        "mb_manufacturer": "制造商：",
        "mb_product": "型号：",
        "bios_manufacturer": "制造商：",
        "bios_version": "版本：",
        "bios_date": "日期：",
        "unknown": "未知",
        "not_detected": "未检测到",
        "cores_unit": "核",
        "threads_unit": "线程",
        "slots_unit": "个",

        # CPU 页
        "cpu_model_bar": "{name}  |  {cores}核{threads}线程  |  最大 {freq} MHz",
        "cpu_overall": "CPU 总体使用率",
        "cpu_freq": "CPU 频率",
        "cpu_cores": "核心数",
        "cpu_core_label": "核心{n}",
        "cpu_cores_usage": " 各核心使用率 ",
        "cpu_trend": "CPU 使用率趋势",
        "cpu_trend_y": "%",
        "cpu_trend_label": "CPU",
        "mem_trend_label": "内存",
        "gpu_trend_labels": ["GPU", "显存"],
        "net_trend_labels": ["上传", "下载"],

        # 内存页
        "mem_model_bar": "{type}  |  {speed}  |  总容量 {total}  |  {slots} 个插槽",
        "mem_usage": "使用率",
        "mem_used": "已用",
        "mem_available": "可用",
        "mem_total_card": "总量",
        "mem_bar": " 内存使用 ",
        "mem_trend": "内存使用率趋势",

        # 磁盘页
        "disk_model_bar": "{models}",
        "disk_read": "读取速度",
        "disk_write": "写入速度",
        "disk_partitions": " 磁盘分区 ",
        "col_device": "设备",
        "col_mount": "挂载点",
        "col_fstype": "文件系统",
        "col_total": "总量",
        "col_used": "已用",
        "col_free": "可用",
        "col_percent": "使用率",

        # 显卡页
        "gpu_model_bar": "{name}  |  {vendor}",
        "gpu_usage": "GPU 使用率",
        "gpu_mem_usage": "显存使用率",
        "gpu_temp": "温度",
        "gpu_power": "功耗",
        "gpu_vram_section": " 显存 ",
        "gpu_trend": "GPU 使用率趋势",

        # 网络页
        "net_upload": "上传速度",
        "net_download": "下载速度",
        "net_sent": "总上传量",
        "net_recv": "总下载量",
        "net_trend": "网络流量趋势",
        "net_trend_y": "KB/s",

        # 进程页
        "process_title": "进程列表（按内存排序）",
        "process_kill": "终止选中进程",
        "process_refresh": "刷新",
        "col_pid": "PID",
        "col_name": "名称",
        "col_cpu_pct": "CPU%",
        "col_mem_pct": "内存%",
        "col_mem_mb": "内存(MB)",
        "col_status": "状态",
        "col_user": "用户",

        # 对话框
        "confirm": "确认",
        "warning": "提示",
        "success": "成功",
        "error": "失败",
        "select_process": "请先选择一个进程",
        "kill_confirm": "确定要终止进程 {name} (PID: {pid}) 吗？",
        "kill_success": "进程 {name} 已终止",
        "kill_fail": "无法终止进程 {name}，可能权限不足",

        # 语言切换
        "lang_switch": "EN",
        "lang_tooltip": "Switch to English",
    },

    "en": {
        # Window title
        "window_title": "System Monitor v2.0",
        "running": "● Running",

        # Tabs
        "tab_info": "  System  ",
        "tab_cpu": "  CPU  ",
        "tab_memory": "  Memory  ",
        "tab_disk": "  Disk  ",
        "tab_gpu": "  GPU  ",
        "tab_network": "  Network  ",
        "tab_process": "  Process  ",

        # System info page
        "os_section": "  Operating System  ",
        "cpu_section": "  Processor (CPU)  ",
        "memory_section": "  Memory (RAM)  ",
        "disk_section": "  Disk  ",
        "gpu_section": "  Graphics (GPU)  ",
        "mb_section": "  Motherboard  ",
        "bios_section": "  BIOS  ",
        "net_section": "  Network Adapters  ",
        "hostname": "Hostname:",
        "os_name": "OS:",
        "os_arch": "Architecture:",
        "uptime": "Uptime:",
        "cpu_model": "Model:",
        "cpu_arch": "Architecture:",
        "cpu_physical_cores": "Physical Cores:",
        "cpu_logical_cores": "Logical Cores:",
        "cpu_max_freq": "Max Frequency:",
        "cpu_l2_cache": "L2 Cache:",
        "cpu_l3_cache": "L3 Cache:",
        "mem_total": "Total:",
        "mem_type": "Type:",
        "mem_speed": "Speed:",
        "mem_slots": "Slots:",
        "disk_model": "Disk {n} Model:",
        "disk_capacity": "  Capacity:",
        "disk_interface": "  Interface:",
        "disk_media": "  Media:",
        "gpu_card": "GPU {n}:",
        "gpu_vram": "  VRAM:",
        "mb_manufacturer": "Manufacturer:",
        "mb_product": "Model:",
        "bios_manufacturer": "Manufacturer:",
        "bios_version": "Version:",
        "bios_date": "Date:",
        "unknown": "Unknown",
        "not_detected": "Not detected",
        "cores_unit": "",
        "threads_unit": "",
        "slots_unit": "",

        # CPU page
        "cpu_model_bar": "{name}  |  {cores}C/{threads}T  |  Max {freq} MHz",
        "cpu_overall": "CPU Usage",
        "cpu_freq": "CPU Frequency",
        "cpu_cores": "Cores",
        "cpu_core_label": "Core {n}",
        "cpu_cores_usage": " Per-Core Usage ",
        "cpu_trend": "CPU Usage Trend",
        "cpu_trend_y": "%",
        "cpu_trend_label": "CPU",
        "mem_trend_label": "Memory",
        "gpu_trend_labels": ["GPU", "VRAM"],
        "net_trend_labels": ["Upload", "Download"],

        # Memory page
        "mem_model_bar": "{type}  |  {speed}  |  Total {total}  |  {slots} slots",
        "mem_usage": "Usage",
        "mem_used": "Used",
        "mem_available": "Available",
        "mem_total_card": "Total",
        "mem_bar": " Memory Usage ",
        "mem_trend": "Memory Usage Trend",

        # Disk page
        "disk_model_bar": "{models}",
        "disk_read": "Read Speed",
        "disk_write": "Write Speed",
        "disk_partitions": " Partitions ",
        "col_device": "Device",
        "col_mount": "Mount",
        "col_fstype": "Filesystem",
        "col_total": "Total",
        "col_used": "Used",
        "col_free": "Free",
        "col_percent": "Usage",

        # GPU page
        "gpu_model_bar": "{name}  |  {vendor}",
        "gpu_usage": "GPU Usage",
        "gpu_mem_usage": "VRAM Usage",
        "gpu_temp": "Temperature",
        "gpu_power": "Power",
        "gpu_vram_section": " VRAM ",
        "gpu_trend": "GPU Usage Trend",

        # Network page
        "net_upload": "Upload Speed",
        "net_download": "Download Speed",
        "net_sent": "Total Sent",
        "net_recv": "Total Received",
        "net_trend": "Network Traffic Trend",
        "net_trend_y": "KB/s",

        # Process page
        "process_title": "Process List (sorted by memory)",
        "process_kill": "Kill Process",
        "process_refresh": "Refresh",
        "col_pid": "PID",
        "col_name": "Name",
        "col_cpu_pct": "CPU%",
        "col_mem_pct": "MEM%",
        "col_mem_mb": "Memory(MB)",
        "col_status": "Status",
        "col_user": "User",

        # Dialogs
        "confirm": "Confirm",
        "warning": "Warning",
        "success": "Success",
        "error": "Error",
        "select_process": "Please select a process first",
        "kill_confirm": "Are you sure you want to kill {name} (PID: {pid})?",
        "kill_success": "Process {name} has been terminated",
        "kill_fail": "Failed to kill {name}, possibly insufficient permissions",

        # Language switch
        "lang_switch": "中",
        "lang_tooltip": "切换到中文",
    },
}


def get_text(lang: str, key: str, **kwargs) -> str:
    """
    获取指定语言的文本
    
    Args:
        lang: 语言代码 ("zh" 或 "en")
        key: 文本键名
        **kwargs: 格式化参数
        
    Returns:
        翻译后的文本字符串
    """
    text = LANGUAGES.get(lang, LANGUAGES["zh"]).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
