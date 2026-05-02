# 系统监控工具 v2.0 / System Monitor v2.0

一个基于 Python + tkinter 的实时系统资源监控桌面工具。支持中英文界面切换。

A real-time system resource monitoring desktop tool built with Python + tkinter. Supports Chinese/English UI.

## 功能特性 / Features

### CPU 监控 / CPU Monitor
- 实时显示总体 CPU 使用率 / Real-time overall CPU usage
- 每个核心独立使用率显示 / Per-core usage display
- CPU 频率监控 / CPU frequency monitoring
- 使用率趋势图 / Usage trend chart

### 内存监控 / Memory Monitor
- 物理内存使用率、已用、可用、总量 / Physical memory usage, used, available, total
- 交换区使用情况 / Swap usage
- 可视化进度条 / Visual progress bar
- 使用率趋势图 / Usage trend chart

### 磁盘监控 / Disk Monitor
- 所有磁盘分区信息（设备、容量、使用率）/ All partition info (device, capacity, usage)
- 实时读写速度显示 / Real-time read/write speed
- 分区详情表格 / Partition details table

### 显卡监控 / GPU Monitor
- 自动检测显卡型号（NVIDIA / AMD / Intel）/ Auto-detect GPU vendor
- GPU 使用率实时监控 / Real-time GPU usage
- 显存使用率、已用/总量 / VRAM usage, used/total
- 温度监控 / Temperature monitor
- 功耗监控 / Power monitor
- 使用率趋势图 / Usage trend chart

### 网络监控 / Network Monitor
- 上传/下载速度实时显示 / Real-time upload/download speed
- 总流量统计 / Total traffic statistics
- 上传/下载速度趋势图 / Speed trend chart

### 进程管理 / Process Manager
- 进程列表（按内存排序）/ Process list (sorted by memory)
- 显示 PID、名称、CPU%、内存%、状态、用户 / Show PID, name, CPU%, MEM%, status, user
- 支持终止指定进程 / Kill process support

### 硬件信息 / Hardware Info
- CPU 型号、核心数、频率、缓存 / CPU model, cores, frequency, cache
- 内存型号、频率、插槽信息 / Memory type, frequency, slot info
- 磁盘型号、容量、接口类型 / Disk model, capacity, interface
- 显卡型号、显存 / GPU model, VRAM

### 多语言 / Multi-Language
- 支持中文/英文界面切换 / Chinese/English UI switch
- 右上角一键切换 / One-click switch at top-right corner

## 快速开始 / Quick Start

### 安装依赖 / Install Dependencies

```bash
pip install -r requirements.txt
```

### 运行程序 / Run

```bash
python main.py
```

或双击 / Or double-click `start.bat`

## 项目结构 / Project Structure

```
SystemMonitor/
├── main.py              # 程序入口 / Entry point
├── start.bat            # 一键启动脚本 / Quick start script
├── requirements.txt     # 依赖列表 / Dependencies
├── LICENSE              # MIT 许可证
├── README.md
├── src/
│   ├── monitor.py       # 系统信息采集 / System info collector
│   ├── hardware.py      # 硬件信息采集 / Hardware info collector
│   ├── gpu_monitor.py   # GPU 实时监控 / GPU real-time monitor
│   ├── gui.py           # GUI 主窗口 / Main window
│   ├── charts.py        # 实时图表组件 / Real-time chart widget
│   └── i18n.py          # 国际化模块 / Internationalization
└── tests/
    └── test_monitor.py  # 单元测试 / Unit tests
```

## 技术栈 / Tech Stack

- **Python 3.8+**
- **psutil** - 跨平台系统信息采集 / Cross-platform system info
- **matplotlib** - 图表绘制 / Chart rendering
- **tkinter** - GUI 界面（Python 内置）/ GUI framework (built-in)
- **nvidia-smi** - NVIDIA 显卡监控 / NVIDIA GPU monitoring
- **rocm-smi** - AMD 显卡监控 / AMD GPU monitoring

## 许可证 / License

[MIT License](LICENSE)
