"""
系统监控工具 - 硬件信息采集模块

采集 CPU、内存、磁盘、显卡、主板等硬件的型号和规格信息。
通过 PowerShell CIM 查询实现，兼容 Windows 10/11。
"""
import platform
import subprocess
import psutil
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class CpuDetail:
    """CPU 详细信息"""
    name: str = ""
    architecture: str = ""
    physical_cores: int = 0
    logical_cores: int = 0
    max_freq: float = 0.0
    current_freq: float = 0.0
    l2_cache: str = ""
    l3_cache: str = ""


@dataclass
class MemoryDetail:
    """内存详细信息"""
    total: int = 0
    slots: List[Dict] = field(default_factory=list)
    speed: str = ""
    type: str = ""


@dataclass
class DiskDetail:
    """磁盘详细信息"""
    model: str = ""
    serial: str = ""
    interface: str = ""
    size: int = 0
    media_type: str = ""


@dataclass
class GpuDetail:
    """显卡详细信息"""
    name: str = ""
    memory: str = ""


@dataclass
class SystemInfo:
    """系统整体信息"""
    hostname: str = ""
    os_name: str = ""
    os_version: str = ""
    os_arch: str = ""
    machine: str = ""
    processor: str = ""
    uptime: str = ""             # 开机时长
    uptime_days: int = 0
    uptime_hours: int = 0
    uptime_minutes: int = 0
    uptime_seconds: int = 0


@dataclass
class MotherboardInfo:
    """主板信息"""
    manufacturer: str = ""       # 制造商
    product: str = ""            # 型号


@dataclass
class BiosInfo:
    """BIOS 信息"""
    manufacturer: str = ""       # 制造商
    version: str = ""            # 版本
    date: str = ""               # 日期


@dataclass
class NetworkAdapterInfo:
    """网络适配器信息"""
    name: str = ""               # 名称
    mac: str = ""                # MAC 地址
    speed: str = ""              # 速度


class HardwareCollector:
    """
    硬件信息采集器
    
    使用 PowerShell CIM 查询采集硬件型号、规格等详细信息。
    """

    @staticmethod
    def _run_ps(command: str) -> str:
        """执行 PowerShell 命令并返回输出"""
        try:
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True, text=True, timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return result.stdout.strip()
        except Exception:
            return ""

    @staticmethod
    def _parse_list(output: str) -> List[Dict]:
        """
        解析 PowerShell Format-List 输出
        
        将类似这样的输出解析为字典列表：
            Name  : Intel CPU
            Cores : 24
            
            Name  : Another CPU
            Cores : 8
        """
        items = []
        current = {}
        for line in output.splitlines():
            line = line.strip()
            if not line:
                if current:
                    items.append(current)
                    current = {}
                continue
            if ":" in line:
                key, _, val = line.partition(":")
                current[key.strip()] = val.strip()
        if current:
            items.append(current)
        return items

    def get_system_info(self) -> SystemInfo:
        """采集操作系统信息"""
        os_name = platform.system()
        os_version = platform.version()

        # Windows 11 检测（build >= 22000 就是 Win11，但 platform 会报告为 Windows 10）
        if os_name == "Windows":
            import sys
            ver = sys.getwindowsversion()
            if ver.major == 10 and ver.build >= 22000:
                os_name = "Windows 11"
                os_version = f"{ver.major}.{ver.minor}.{ver.build}"
            else:
                os_name = f"Windows {ver.major}"
                os_version = f"{ver.major}.{ver.minor}.{ver.build}"

        # 计算开机时长
        uptime_sec = psutil.boot_time()
        import datetime
        boot_time = datetime.datetime.fromtimestamp(uptime_sec)
        delta = datetime.datetime.now() - boot_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days = delta.days
        if days > 0:
            uptime_str = f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            uptime_str = f"{hours}h {minutes}m"
        else:
            uptime_str = f"{minutes}m {seconds}s"

        return SystemInfo(
            hostname=platform.node(),
            os_name=os_name,
            os_version=os_version,
            os_arch=platform.machine(),
            machine=platform.machine(),
            processor=platform.processor(),
            uptime=uptime_str,
            uptime_days=days,
            uptime_hours=hours,
            uptime_minutes=minutes,
            uptime_seconds=seconds,
        )

    def get_cpu_detail(self) -> CpuDetail:
        """采集 CPU 详细信息"""
        physical_cores = psutil.cpu_count(logical=False) or 0
        logical_cores = psutil.cpu_count(logical=True) or 0
        freq = psutil.cpu_freq()

        # 通过 PowerShell 获取 CPU 型号和缓存
        output = self._run_ps(
            "Get-CimInstance Win32_Processor | "
            "Select-Object Name,MaxClockSpeed,L2CacheSize,L3CacheSize | Format-List"
        )

        name = platform.processor()
        max_freq = freq.max if freq else 0
        l2 = ""
        l3 = ""

        for line in output.splitlines():
            line = line.strip()
            if line.startswith("Name") and ":" in line:
                val = line.split(":", 1)[1].strip()
                if val:
                    name = val
            elif line.startswith("MaxClockSpeed") and ":" in line:
                try:
                    max_freq = float(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif line.startswith("L2CacheSize") and ":" in line:
                val = line.split(":", 1)[1].strip()
                if val and val != "0":
                    l2 = f"{int(val) // 1024} MB"
            elif line.startswith("L3CacheSize") and ":" in line:
                val = line.split(":", 1)[1].strip()
                if val and val != "0":
                    l3 = f"{int(val) // 1024} MB"

        return CpuDetail(
            name=name,
            architecture=platform.machine(),
            physical_cores=physical_cores,
            logical_cores=logical_cores,
            max_freq=max_freq,
            current_freq=freq.current if freq else 0,
            l2_cache=l2,
            l3_cache=l3,
        )

    def get_memory_detail(self) -> MemoryDetail:
        """采集内存详细信息"""
        mem = psutil.virtual_memory()

        output = self._run_ps(
            "Get-CimInstance Win32_PhysicalMemory | "
            "Select-Object Capacity,Speed,MemoryType,Manufacturer,PartNumber,"
            "DeviceLocator | Format-List"
        )

        slots = []
        current_slot = {}

        for line in output.splitlines():
            line = line.strip()
            if not line:
                if current_slot:
                    slots.append(current_slot)
                    current_slot = {}
                continue

            if ":" in line:
                key, _, val = line.partition(":")
                val = val.strip()
                key = key.strip()

                if key == "Capacity" and val:
                    try:
                        current_slot["capacity"] = int(val)
                    except ValueError:
                        pass
                elif key == "Speed" and val:
                    current_slot["speed"] = val + " MHz"
                elif key == "MemoryType" and val:
                    # MemoryType: 0=Unknown, 20=DDR, 21=DDR2, 24=DDR3, 26=DDR4, 34=DDR5
                    # 新版 Windows 可能返回 0，用 SMBIOSMemoryType 也可以
                    type_map = {"20": "DDR", "21": "DDR2", "24": "DDR3", "26": "DDR4", "34": "DDR5"}
                    current_slot["type"] = type_map.get(val, "")
                elif key == "Manufacturer":
                    current_slot["manufacturer"] = val
                elif key == "PartNumber":
                    current_slot["part_number"] = val
                elif key == "DeviceLocator":
                    current_slot["slot"] = val

        if current_slot:
            slots.append(current_slot)

        # 尝试获取内存类型（如果 MemoryType 返回 0）
        speed = slots[0].get("speed", "") if slots else ""
        mem_type = slots[0].get("type", "") if slots else ""

        if not mem_type:
            # 尝试用 SMBIOSMemoryType 获取
            type_output = self._run_ps(
                "Get-CimInstance Win32_PhysicalMemory | "
                "Select-Object SMBIOSMemoryType | Format-List"
            )
            smbios_map = {"20": "DDR", "21": "DDR2", "24": "DDR3", "26": "DDR4", "34": "DDR5"}
            for line in type_output.splitlines():
                if "SMBIOSMemoryType" in line and ":" in line:
                    val = line.split(":", 1)[1].strip()
                    mem_type = smbios_map.get(val, "")
                    if mem_type:
                        for slot in slots:
                            slot["type"] = mem_type
                        break

        return MemoryDetail(
            total=mem.total,
            slots=slots,
            speed=speed,
            type=mem_type,
        )

    def get_disk_details(self) -> List[DiskDetail]:
        """采集磁盘详细信息"""
        output = self._run_ps(
            "Get-CimInstance Win32_DiskDrive | "
            "Select-Object Model,SerialNumber,InterfaceType,Size,MediaType | Format-List"
        )

        disks = []
        current = {}
        for line in output.splitlines():
            line = line.strip()
            if not line:
                if current:
                    disks.append(DiskDetail(**current))
                    current = {}
                continue
            if ":" in line:
                key, _, val = line.partition(":")
                val = val.strip()
                key = key.strip()

                if key == "Model":
                    current["model"] = val
                elif key == "SerialNumber":
                    current["serial"] = val
                elif key == "InterfaceType":
                    current["interface"] = val
                elif key == "Size" and val:
                    try:
                        current["size"] = int(val)
                    except ValueError:
                        pass
                elif key == "MediaType":
                    current["media_type"] = val

        if current:
            disks.append(DiskDetail(**current))

        return disks

    def get_motherboard(self) -> MotherboardInfo:
        """采集主板信息"""
        output = self._run_ps(
            "Get-CimInstance Win32_BaseBoard | "
            "Select-Object Manufacturer,Product | Format-List"
        )
        info = MotherboardInfo()
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("Manufacturer") and ":" in line:
                info.manufacturer = line.split(":", 1)[1].strip()
            elif line.startswith("Product") and ":" in line:
                info.product = line.split(":", 1)[1].strip()
        return info

    def get_bios(self) -> BiosInfo:
        """采集 BIOS 信息"""
        output = self._run_ps(
            "Get-CimInstance Win32_BIOS | "
            "Select-Object Manufacturer,SMBIOSBIOSVersion,ReleaseDate | Format-List"
        )
        info = BiosInfo()
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("Manufacturer") and ":" in line:
                info.manufacturer = line.split(":", 1)[1].strip()
            elif line.startswith("SMBIOSBIOSVersion") and ":" in line:
                info.version = line.split(":", 1)[1].strip()
            elif line.startswith("ReleaseDate") and ":" in line:
                info.date = line.split(":", 1)[1].strip()[:10]
        return info

    def get_network_adapters(self) -> List[NetworkAdapterInfo]:
        """采集物理网络适配器信息"""
        output = self._run_ps(
            "Get-CimInstance Win32_NetworkAdapter | "
            "Where-Object {$_.PhysicalAdapter -eq $true} | "
            "Select-Object Name,MACAddress,Speed | Format-List"
        )
        adapters = []
        current = {}
        for line in output.splitlines():
            line = line.strip()
            if not line:
                if current:
                    adapters.append(NetworkAdapterInfo(**current))
                    current = {}
                continue
            if ":" in line:
                key, _, val = line.partition(":")
                key = key.strip()
                val = val.strip()
                if key == "Name":
                    current["name"] = val
                elif key == "MACAddress" and val:
                    current["mac"] = val
                elif key == "Speed" and val:
                    try:
                        speed_bps = int(val)
                        if speed_bps >= 1000000000:
                            current["speed"] = f"{speed_bps // 1000000000} Gbps"
                        elif speed_bps >= 1000000:
                            current["speed"] = f"{speed_bps // 1000000} Mbps"
                        else:
                            current["speed"] = f"{speed_bps} bps"
                    except ValueError:
                        pass
        if current:
            adapters.append(NetworkAdapterInfo(**current))
        return adapters

    def get_gpu_details(self) -> List[GpuDetail]:
        """采集显卡详细信息"""
        output = self._run_ps(
            "Get-CimInstance Win32_VideoController | "
            "Select-Object Name,AdapterRAM | Format-List"
        )

        gpus = []
        current = {}
        for line in output.splitlines():
            line = line.strip()
            if not line:
                if current:
                    gpus.append(GpuDetail(**current))
                    current = {}
                continue
            if ":" in line:
                key, _, val = line.partition(":")
                key = key.strip()
                val = val.strip()

                if key == "Name":
                    current["name"] = val
                elif key == "AdapterRAM" and val:
                    try:
                        ram_bytes = int(val)
                        if ram_bytes > 0:
                            current["memory"] = f"{ram_bytes // 1024 // 1024} MB"
                    except ValueError:
                        pass

        if current:
            gpus.append(GpuDetail(**current))

        # 尝试用 nvidia-smi 获取真实显存（AdapterRAM 是 32 位，超过 4GB 会溢出）
        nvidia_info = self._run_ps(
            "nvidia-smi --query-gpu=name,memory.total --format=csv,noheader"
        )
        if nvidia_info:
            nvidia_map = {}
            for line in nvidia_info.splitlines():
                if "," in line:
                    name_part, _, mem_part = line.partition(",")
                    name_part = name_part.strip()
                    mem_part = mem_part.strip()  # e.g. "8151 MiB"
                    nvidia_map[name_part] = mem_part

            # 替换 NVIDIA 显卡的显存信息
            for gpu in gpus:
                for nvidia_name, nvidia_mem in nvidia_map.items():
                    if "NVIDIA" in gpu.name.upper() and nvidia_name in gpu.name:
                        gpu.memory = nvidia_mem
                        break

        return gpus

    @staticmethod
    def format_bytes(bytes_val: int) -> str:
        """格式化字节数"""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if abs(bytes_val) < 1024:
                return f"{bytes_val:.1f} {unit}"
            bytes_val /= 1024
        return f"{bytes_val:.1f} PB"
