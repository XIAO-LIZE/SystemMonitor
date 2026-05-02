"""
系统监控工具 - 系统信息采集模块

使用 psutil 采集 CPU、内存、磁盘、网络等系统信息。
"""
import time
import psutil
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class CpuInfo:
    """CPU 信息"""
    overall: float = 0.0            # 总体使用率 (%)
    per_core: List[float] = field(default_factory=list)  # 每个核心的使用率
    core_count: int = 0             # 核心数
    freq_current: float = 0.0       # 当前频率 (MHz)
    freq_max: float = 0.0           # 最大频率 (MHz)


@dataclass
class MemoryInfo:
    """内存信息"""
    total: int = 0          # 总内存 (字节)
    used: int = 0           # 已用 (字节)
    available: int = 0      # 可用 (字节)
    percent: float = 0.0    # 使用率 (%)
    swap_total: int = 0     # 交换区总量
    swap_used: int = 0      # 交换区已用
    swap_percent: float = 0.0


@dataclass
class DiskInfo:
    """磁盘信息"""
    partitions: List[Dict] = field(default_factory=list)   # 分区列表
    read_speed: float = 0.0     # 读取速度 (字节/秒)
    write_speed: float = 0.0    # 写入速度 (字节/秒)


@dataclass
class NetworkInfo:
    """网络信息"""
    bytes_sent: int = 0         # 已发送字节
    bytes_recv: int = 0         # 已接收字节
    upload_speed: float = 0.0   # 上传速度 (字节/秒)
    download_speed: float = 0.0 # 下载速度 (字节/秒)
    connections: int = 0        # 活跃连接数


@dataclass
class ProcessInfo:
    """进程信息"""
    pid: int = 0
    name: str = ""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_mb: float = 0.0
    status: str = ""
    username: str = ""


class SystemMonitor:
    """
    系统信息采集器
    
    采集 CPU、内存、磁盘、网络、进程等信息。
    支持历史数据记录，用于绘制趋势图。
    """

    def __init__(self, history_size: int = 120):
        """
        初始化采集器
        
        Args:
            history_size: 历史数据保留数量（默认120个点，即2分钟@1秒/次）
        """
        self.history_size = history_size

        # 历史数据
        self.cpu_history: List[float] = []
        self.memory_history: List[float] = []
        self.upload_history: List[float] = []
        self.download_history: List[float] = []

        # 上一次的网络/磁盘计数器（用于计算速度）
        self._last_net_io = psutil.net_io_counters()
        self._last_disk_io = psutil.disk_io_counters()
        self._last_time = time.time()

    def _add_history(self, history: List[float], value: float):
        """添加历史数据点，超出容量时移除最旧的"""
        history.append(value)
        if len(history) > self.history_size:
            history.pop(0)

    def get_cpu(self) -> CpuInfo:
        """采集 CPU 信息"""
        overall = psutil.cpu_percent(interval=0)
        per_core = psutil.cpu_percent(interval=0, percpu=True)
        freq = psutil.cpu_freq()

        info = CpuInfo(
            overall=overall,
            per_core=per_core,
            core_count=psutil.cpu_count(logical=True),
            freq_current=freq.current if freq else 0,
            freq_max=freq.max if freq else 0,
        )

        self._add_history(self.cpu_history, overall)
        return info

    def get_memory(self) -> MemoryInfo:
        """采集内存信息"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        info = MemoryInfo(
            total=mem.total,
            used=mem.used,
            available=mem.available,
            percent=mem.percent,
            swap_total=swap.total,
            swap_used=swap.used,
            swap_percent=swap.percent,
        )

        self._add_history(self.memory_history, mem.percent)
        return info

    def get_disk(self) -> DiskInfo:
        """采集磁盘信息"""
        # 分区信息
        partitions = []
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                partitions.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                })
            except PermissionError:
                continue

        # 计算读写速度
        now = time.time()
        elapsed = now - self._last_time
        if elapsed <= 0:
            elapsed = 1

        current_io = psutil.disk_io_counters()
        read_speed = (current_io.read_bytes - self._last_disk_io.read_bytes) / elapsed
        write_speed = (current_io.write_bytes - self._last_disk_io.write_bytes) / elapsed

        self._last_disk_io = current_io

        return DiskInfo(
            partitions=partitions,
            read_speed=read_speed,
            write_speed=write_speed,
        )

    def get_network(self) -> NetworkInfo:
        """采集网络信息"""
        now = time.time()
        elapsed = now - self._last_time
        if elapsed <= 0:
            elapsed = 1

        current_io = psutil.net_io_counters()
        upload_speed = (current_io.bytes_sent - self._last_net_io.bytes_sent) / elapsed
        download_speed = (current_io.bytes_recv - self._last_net_io.bytes_recv) / elapsed

        self._last_net_io = current_io
        self._last_time = now

        connections = len(psutil.net_connections(kind="inet"))

        info = NetworkInfo(
            bytes_sent=current_io.bytes_sent,
            bytes_recv=current_io.bytes_recv,
            upload_speed=upload_speed,
            download_speed=download_speed,
            connections=connections,
        )

        self._add_history(self.upload_history, upload_speed)
        self._add_history(self.download_history, download_speed)
        return info

    def get_processes(self, top_n: int = 30) -> List[ProcessInfo]:
        """
        获取进程列表（按内存使用排序）
        
        Args:
            top_n: 返回前 N 个进程
        """
        processes = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent",
                                          "memory_info", "status", "username"]):
            try:
                info = proc.info
                processes.append(ProcessInfo(
                    pid=info["pid"],
                    name=info["name"],
                    cpu_percent=info["cpu_percent"] or 0,
                    memory_percent=info["memory_percent"] or 0,
                    memory_mb=(info["memory_info"].rss / 1024 / 1024) if info["memory_info"] else 0,
                    status=info["status"],
                    username=info["username"] or "",
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # 按内存使用排序
        processes.sort(key=lambda p: p.memory_mb, reverse=True)
        return processes[:top_n]

    @staticmethod
    def kill_process(pid: int) -> bool:
        """终止指定进程"""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    @staticmethod
    def format_bytes(bytes_val: float) -> str:
        """将字节数格式化为人类可读的字符串"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if abs(bytes_val) < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} PB"
