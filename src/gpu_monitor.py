"""
系统监控工具 - GPU 实时监控模块

支持 NVIDIA 和 AMD 显卡的实时使用率、显存、温度监控。
NVIDIA 通过 nvidia-smi，AMD 通过 rocm-smi 或 WMI 回退。
"""
import subprocess
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class GpuStats:
    """GPU 实时状态数据"""
    name: str = ""
    gpu_usage: float = 0.0          # GPU 使用率 (%)
    memory_usage: float = 0.0       # 显存使用率 (%)
    memory_used: str = ""           # 已用显存
    memory_total: str = ""          # 总显存
    temperature: float = 0.0        # 温度 (°C)
    power: float = 0.0              # 功耗 (W)
    vendor: str = ""                # NVIDIA / AMD / Intel


class GpuMonitor:
    """
    GPU 实时监控器
    
    自动检测显卡类型，选择合适的命令行工具采集实时数据。
    """

    def __init__(self):
        self._vendor = self._detect_vendor()
        self._gpu_name = self._detect_name()

    @staticmethod
    def _run(cmd: list, timeout: int = 5) -> str:
        """执行命令并返回输出"""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout,
                creationflags=0x08000000,  # CREATE_NO_WINDOW
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def _detect_vendor(self) -> str:
        """检测显卡厂商"""
        # 检查 NVIDIA
        if self._run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"]):
            return "NVIDIA"
        # 检查 AMD
        if self._run(["rocm-smi", "--showproductname"]):
            return "AMD"
        # 回退到 WMI
        output = self._run([
            "powershell", "-Command",
            "Get-CimInstance Win32_VideoController | Select-Object Name | Format-List"
        ])
        if "NVIDIA" in output.upper():
            return "NVIDIA"
        elif "AMD" in output.upper() or "RADEON" in output.upper():
            return "AMD"
        return "Unknown"

    def _detect_name(self) -> str:
        """获取 GPU 名称"""
        if self._vendor == "NVIDIA":
            output = self._run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"])
            if output:
                return output.splitlines()[0].strip()
        elif self._vendor == "AMD":
            output = self._run(["rocm-smi", "--showproductname"])
            for line in output.splitlines():
                if "Card" in line or "GPU" in line:
                    return line.split(":", 1)[-1].strip()

        # 回退
        output = self._run([
            "powershell", "-Command",
            "Get-CimInstance Win32_VideoController | Select-Object -First 1 Name | Format-List"
        ])
        for line in output.splitlines():
            if line.strip().startswith("Name"):
                return line.split(":", 1)[-1].strip()
        return "未知显卡"

    def get_stats(self) -> GpuStats:
        """采集 GPU 实时状态"""
        if self._vendor == "NVIDIA":
            return self._get_nvidia_stats()
        elif self._vendor == "AMD":
            return self._get_amd_stats()
        else:
            return self._get_fallback_stats()

    def _get_nvidia_stats(self) -> GpuStats:
        """通过 nvidia-smi 采集 NVIDIA GPU 状态"""
        output = self._run([
            "nvidia-smi",
            "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw",
            "--format=csv,noheader,nounits"
        ])

        stats = GpuStats(name=self._gpu_name, vendor="NVIDIA")

        if output:
            # 取第一张显卡
            line = output.splitlines()[0]
            parts = [p.strip() for p in line.split(",")]

            if len(parts) >= 6:
                try:
                    stats.gpu_usage = float(parts[1])
                except ValueError:
                    pass

                try:
                    mem_used = float(parts[2])   # MiB
                    mem_total = float(parts[3])  # MiB
                    stats.memory_used = f"{mem_used:.0f} MiB"
                    stats.memory_total = f"{mem_total:.0f} MiB"
                    if mem_total > 0:
                        stats.memory_usage = (mem_used / mem_total) * 100
                except ValueError:
                    pass

                try:
                    stats.temperature = float(parts[4])
                except ValueError:
                    pass

                try:
                    stats.power = float(parts[5])
                except ValueError:
                    pass

        return stats

    def _get_amd_stats(self) -> GpuStats:
        """通过 rocm-smi 采集 AMD GPU 状态"""
        stats = GpuStats(name=self._gpu_name, vendor="AMD")

        # 使用率
        usage_output = self._run(["rocm-smi", "--showuse"])
        for line in usage_output.splitlines():
            if "GPU use" in line or "use" in line.lower():
                import re
                match = re.search(r"(\d+\.?\d*)\s*%", line)
                if match:
                    stats.gpu_usage = float(match.group(1))

        # 显存
        mem_output = self._run(["rocm-smi", "--showmeminfo", "vram"])
        for line in mem_output.splitlines():
            if "Total" in line:
                import re
                match = re.search(r"(\d+\.?\d*)\s*(\w+)", line)
                if match:
                    stats.memory_total = f"{match.group(1)} {match.group(2)}"
            elif "Used" in line or "InUse" in line:
                import re
                match = re.search(r"(\d+\.?\d*)\s*(\w+)", line)
                if match:
                    stats.memory_used = f"{match.group(1)} {match.group(2)}"

        # 温度
        temp_output = self._run(["rocm-smi", "-t"])
        for line in temp_output.splitlines():
            import re
            match = re.search(r"(\d+\.?\d*)\s*c", line, re.IGNORECASE)
            if match:
                stats.temperature = float(match.group(1))
                break

        return stats

    def _get_fallback_stats(self) -> GpuStats:
        """回退方案：通过 WMI 获取基本信息"""
        stats = GpuStats(name=self._gpu_name, vendor="Unknown")

        # 尝试从 WMI 获取负载
        output = self._run([
            "powershell", "-Command",
            "Get-CimInstance Win32_VideoController | "
            "Select-Object Name,LoadPercentage | Format-List"
        ])

        for line in output.splitlines():
            line = line.strip()
            if line.startswith("LoadPercentage") and ":" in line:
                val = line.split(":", 1)[1].strip()
                try:
                    stats.gpu_usage = float(val)
                except ValueError:
                    pass
            elif line.startswith("Name") and ":" in line:
                name = line.split(":", 1)[1].strip()
                if name:
                    stats.name = name

        return stats
