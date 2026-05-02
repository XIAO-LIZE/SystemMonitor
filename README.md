# 系统监控工具 v2.0 / System Monitor v2.0

一个基于 Python + tkinter 的实时系统资源监控桌面工具。支持中英文界面切换。

A real-time system resource monitoring desktop tool built with Python + tkinter. Supports Chinese/English UI.

## 功能介绍 / Features

### 操作系统信息 / System Info
- 主机名、操作系统版本、架构、运行时间
- 主板制造商、型号
- BIOS 制造商、版本、日期
- 网络适配器列表（网卡名、MAC、速率）
- 左右两列布局，信息一目了然

### CPU 监控 / CPU Monitor
- 实时显示总体 CPU 使用率
- 每核心的独立使用率显示
- CPU 频率监测
- 使用率趋势图

### 内存监控 / Memory Monitor
- 物理内存使用率、已用、可用、总量
- 虚拟内存使用率
- 可视化进度条
- 使用率趋势图

### 磁盘监控 / Disk Monitor
- 所有分区信息（设备、容量、使用率）
- 实时读写速度显示（/秒）
- 分区详情表格

### 显卡监控 / GPU Monitor
- 自动识别显卡型号（NVIDIA / AMD / Intel）
- GPU 使用率实时监控
- 显存使用率、已用/总量
- 温度监控
- 功耗监控
- 使用率趋势图

### 网络监控 / Network Monitor
- 上传/下载速度实时显示（/秒）
- 总流量统计
- 上传/下载速度趋势图

### 进程管理 / Process Manager
- 进程列表（按内存排序）
- 显示 PID、名称、CPU%、内存%、状态、用户
- 支持结束指定进程

### 多语言 / Multi-Language
- 支持中文/英文界面切换
- 右上角一键切换
- 所有标签、表头、单位均随语言切换

## 快速开始 / Quick Start

### 安装依赖 / Install Dependencies

```bash
pip install -r requirements.txt
```

### 运行 / Run

```bash
python main.py
```

或双击 `start.bat`

## 项目结构 / Project Structure

```
SystemMonitor/
├── main.py              # 入口文件 / Entry point
├── start.bat            # 一键启动脚本 / Quick start script
├── requirements.txt     # 依赖列表 / Dependencies
├── LICENSE              # MIT 开源证书
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
- **matplotlib** - 图表渲染 / Chart rendering
- **tkinter** - GUI 框架（Python 内置）/ GUI framework (built-in)
- **nvidia-smi** - NVIDIA 显卡监控 / NVIDIA GPU monitoring
- **rocm-smi** - AMD 显卡监控 / AMD GPU monitoring

## 开源证书 / License

[MIT License](LICENSE)
