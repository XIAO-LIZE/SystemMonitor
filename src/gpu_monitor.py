"""
系统监控工具 - GPU 实时监控模块（多 GPU 支持）

支持 NVIDIA 和 AMD 显卡的实时使用率、显存、温度监控。
NVIDIA 通过 nvidia-smi，AMD 通过 rocm-smi 或 WMI 回退。
"""
import subprocess
from dataclasses import dataclass


@dataclass
class GpuStats:
    name: str = ""
    gpu_usage: float = 0.0
    memory_usage: float = 0.0
    memory_used: str = ""
    memory_total: str = ""
    temperature: float = 0.0
    power: float = 0.0
    vendor: str = ""


class GpuMonitor:
    """GPU 实时监控器（多 GPU 支持）"""

    def __init__(self):
        self._vendor = self._detect_vendor()
        self._gpu_names = self._detect_names()

    @property
    def gpu_count(self) -> int:
        return len(self._gpu_names)

    @property
    def vendor(self) -> str:
        return self._vendor

    @staticmethod
    def _run(cmd: list, timeout: int = 5) -> str:
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout,
                creationflags=0x08000000,
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def _detect_vendor(self) -> str:
        if self._run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"]):
            return "NVIDIA"
        if self._run(["rocm-smi", "--showproductname"]):
            return "AMD"
        output = self._run([
            "powershell", "-Command",
            "Get-CimInstance Win32_VideoController | Select-Object Name | Format-List"
        ])
        if "NVIDIA" in output.upper():
            return "NVIDIA"
        elif "AMD" in output.upper() or "RADEON" in output.upper():
            return "AMD"
        return "Unknown"

    def _detect_names(self) -> list:
        # Primary detection via vendor tool
        names = []
        if self._vendor == "NVIDIA":
            output = self._run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"])
            if output:
                names = [s.strip() for s in output.splitlines() if s.strip()]
        elif self._vendor == "AMD":
            output = self._run(["rocm-smi", "--showproductname"])
            for line in output.splitlines():
                if "Card" in line or "GPU" in line:
                    name = line.split(":", 1)[-1].strip()
                    if name:
                        names.append(name)

        # Supplement with WMI to catch all GPUs (e.g. Intel iGPU + NVIDIA dGPU)
        wmi_output = self._run([
            "powershell", "-Command",
            "Get-CimInstance Win32_VideoController | Select-Object Name | Format-List"
        ])
        wmi_names = []
        for line in wmi_output.splitlines():
            if line.strip().startswith("Name"):
                name = line.split(":", 1)[-1].strip()
                if name and name not in names:
                    wmi_names.append(name)
        # Prepend WMI-only GPUs (usually integrated) before tool-detected ones
        names = wmi_names + names
        return names or ["未知显卡"]

    def get_stats(self, gpu_index: int = 0) -> GpuStats:
        """采集指定 GPU 实时状态（0-indexed）"""
        all_stats = self.get_all_stats()
        if 0 <= gpu_index < len(all_stats):
            return all_stats[gpu_index]
        return GpuStats(name="Unknown", vendor=self._vendor)

    def get_all_stats(self) -> list:
        """采集所有 GPU 实时状态"""
        if self._vendor == "NVIDIA":
            raw_stats = self._get_nvidia_stats()
        elif self._vendor == "AMD":
            raw_stats = self._get_amd_stats()
        else:
            raw_stats = self._get_fallback_stats()

        # Align raw stats with _gpu_names order
        # Raw stats come from vendor tool (e.g. only NVIDIA), WMI may have extra GPUs
        stats_map = {}
        for s in raw_stats:
            for name in self._gpu_names:
                if name.lower() in s.name.lower() or s.name.lower() in name.lower():
                    stats_map[name] = s
                    break
            else:
                stats_map[s.name] = s

        result = []
        for name in self._gpu_names:
            if name in stats_map:
                result.append(stats_map[name])
            else:
                result.append(GpuStats(
                    name=name, vendor="Unknown",
                    gpu_usage=-1, memory_usage=-1, temperature=-1, power=-1))
        return result

    def _get_nvidia_stats(self) -> list:
        output = self._run([
            "nvidia-smi",
            "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw",
            "--format=csv,noheader,nounits"
        ])
        results = []
        if output:
            for line in output.splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) < 6:
                    continue
                stats = GpuStats(name=parts[0], vendor="NVIDIA")
                try:
                    stats.gpu_usage = float(parts[1])
                except ValueError:
                    pass
                try:
                    mem_used = float(parts[2])
                    mem_total = float(parts[3])
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
                results.append(stats)

        if not results and self._gpu_names:
            for name in self._gpu_names:
                results.append(GpuStats(name=name, vendor=self._vendor))
        return results

    def _get_amd_stats(self) -> list:
        results = []
        for i, name in enumerate(self._gpu_names):
            stats = GpuStats(name=name, vendor="AMD")
            import re
            usage_output = self._run(["rocm-smi", "--showuse"])
            for line in usage_output.splitlines():
                if "GPU use" in line or "use" in line.lower():
                    match = re.search(r"(\d+\.?\d*)\s*%", line)
                    if match:
                        stats.gpu_usage = float(match.group(1))
            mem_output = self._run(["rocm-smi", "--showmeminfo", "vram"])
            for line in mem_output.splitlines():
                if "Total" in line:
                    match = re.search(r"(\d+\.?\d*)\s*(\w+)", line)
                    if match:
                        stats.memory_total = f"{match.group(1)} {match.group(2)}"
                elif "Used" in line or "InUse" in line:
                    match = re.search(r"(\d+\.?\d*)\s*(\w+)", line)
                    if match:
                        stats.memory_used = f"{match.group(1)} {match.group(2)}"
            temp_output = self._run(["rocm-smi", "-t"])
            for line in temp_output.splitlines():
                match = re.search(r"(\d+\.?\d*)\s*c", line, re.IGNORECASE)
                if match:
                    stats.temperature = float(match.group(1))
                    break
            results.append(stats)
        return results or [GpuStats(name="Unknown", vendor="AMD")]

    def _get_fallback_stats(self) -> list:
        results = []
        output = self._run([
            "powershell", "-Command",
            "Get-CimInstance Win32_VideoController | "
            "Select-Object Name,LoadPercentage | Format-List"
        ])
        current_name = ""
        current_usage = 0.0
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("LoadPercentage") and ":" in line:
                val = line.split(":", 1)[1].strip()
                try:
                    current_usage = float(val)
                except ValueError:
                    current_usage = 0.0
            elif line.startswith("Name") and ":" in line:
                if current_name:
                    results.append(GpuStats(
                        name=current_name, gpu_usage=current_usage,
                        vendor="Unknown"))
                current_name = line.split(":", 1)[1].strip()
                current_usage = 0.0
        if current_name:
            results.append(GpuStats(
                name=current_name, gpu_usage=current_usage,
                vendor="Unknown"))
        return results or [GpuStats(name="Unknown", vendor="Unknown")]
