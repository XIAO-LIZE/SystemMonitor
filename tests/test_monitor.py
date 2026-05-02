"""
系统信息采集模块测试

测试 SystemMonitor 类的各项数据采集功能。
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.monitor import SystemMonitor, CpuInfo, MemoryInfo, DiskInfo, NetworkInfo, ProcessInfo


class TestSystemMonitor(unittest.TestCase):
    """SystemMonitor 测试类"""

    def setUp(self):
        """测试前准备"""
        self.monitor = SystemMonitor(history_size=10)

    def test_get_cpu(self):
        """测试 CPU 信息采集"""
        cpu = self.monitor.get_cpu()
        self.assertIsInstance(cpu, CpuInfo)
        self.assertGreaterEqual(cpu.core_count, 1)
        self.assertGreaterEqual(cpu.overall, 0)
        self.assertLessEqual(cpu.overall, 100)
        self.assertEqual(len(cpu.per_core), cpu.core_count)

    def test_get_memory(self):
        """测试内存信息采集"""
        mem = self.monitor.get_memory()
        self.assertIsInstance(mem, MemoryInfo)
        self.assertGreater(mem.total, 0)
        self.assertGreaterEqual(mem.used, 0)
        self.assertGreater(mem.available, 0)
        self.assertGreaterEqual(mem.percent, 0)
        self.assertLessEqual(mem.percent, 100)

    def test_get_disk(self):
        """测试磁盘信息采集"""
        disk = self.monitor.get_disk()
        self.assertIsInstance(disk, DiskInfo)
        self.assertGreater(len(disk.partitions), 0)

        # 检查第一个分区的结构
        part = disk.partitions[0]
        self.assertIn("device", part)
        self.assertIn("mountpoint", part)
        self.assertIn("total", part)
        self.assertIn("percent", part)

    def test_get_network(self):
        """测试网络信息采集"""
        net = self.monitor.get_network()
        self.assertIsInstance(net, NetworkInfo)
        self.assertGreaterEqual(net.bytes_sent, 0)
        self.assertGreaterEqual(net.bytes_recv, 0)
        self.assertGreaterEqual(net.upload_speed, 0)
        self.assertGreaterEqual(net.download_speed, 0)

    def test_get_processes(self):
        """测试进程列表采集"""
        procs = self.monitor.get_processes(top_n=10)
        self.assertIsInstance(procs, list)
        self.assertGreater(len(procs), 0)
        self.assertLessEqual(len(procs), 10)

        # 检查进程信息结构
        proc = procs[0]
        self.assertIsInstance(proc, ProcessInfo)
        self.assertGreater(proc.pid, 0)
        self.assertNotEqual(proc.name, "")

    def test_cpu_history(self):
        """测试 CPU 历史数据记录"""
        self.monitor.get_cpu()
        self.monitor.get_cpu()
        self.monitor.get_cpu()
        self.assertEqual(len(self.monitor.cpu_history), 3)

    def test_memory_history(self):
        """测试内存历史数据记录"""
        self.monitor.get_memory()
        self.monitor.get_memory()
        self.assertEqual(len(self.monitor.memory_history), 2)

    def test_history_size_limit(self):
        """测试历史数据容量限制"""
        monitor = SystemMonitor(history_size=5)
        for _ in range(10):
            monitor.get_cpu()
        self.assertEqual(len(monitor.cpu_history), 5)

    def test_format_bytes(self):
        """测试字节数格式化"""
        self.assertEqual(SystemMonitor.format_bytes(0), "0.0 B")
        self.assertEqual(SystemMonitor.format_bytes(1024), "1.0 KB")
        self.assertEqual(SystemMonitor.format_bytes(1048576), "1.0 MB")
        self.assertEqual(SystemMonitor.format_bytes(1073741824), "1.0 GB")


if __name__ == "__main__":
    unittest.main()
