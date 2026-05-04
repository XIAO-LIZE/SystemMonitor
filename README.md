# 系统监控工具 v2.2 / System Monitor v2.2

一个基于 Python + tkinter 的实时系统资源监控桌面工具。支持中英文界面切换，支持多显卡切换监控。

A real-time system resource monitoring desktop tool built with Python + tkinter. Supports Chinese/English UI and multi-GPU monitoring.

## 功能介绍 / Features

### 系统信息 / System Info
- 主机名、操作系统版本、架构、运行时间
- CPU、内存、磁盘、显卡、主板、BIOS 详细信息
- 网络适配器列表（网卡名、MAC、速率）
- 网络 IP 信息（IP 地址、网关、DNS，实时刷新）

### CPU 监控 / CPU Monitor
- 实时总体使用率 + 每核心独立使用率
- CPU 频率监测、核心数
- CPU 温度监控（绿/橙/红 颜色编码）
- 使用率趋势图

### 显卡监控 / GPU Monitor
- 多显卡自动识别（NVIDIA / AMD / Intel 集显）
- 多显卡切换选择器
- GPU 使用率、显存、温度、功耗实时监控
- 显存进度条（已用/总量）
- GPU + 显存使用率趋势图

### 内存监控 / Memory Monitor
- 物理内存使用率、已用、可用、总量
- 可视化进度条 + 使用率趋势图

### 磁盘监控 / Disk Monitor
- 所有分区信息（设备、挂载点、文件系统、容量、使用率）
- 实时读写速度

### 网络监控 / Network Monitor
- 上传/下载速度实时显示 + 总流量统计
- 上传/下载速度趋势图

### 进程管理 / Process Manager
- 进程列表（按内存排序），PID/名称/CPU%/内存%/状态/用户
- 支持终止选中进程

### 多语言 / Multi-Language
- 中文 / 英文一键切换
- 所有标签、表头、单位、图表坐标轴均随语言切换

## 更新日志 / Changelog

### v2.2
- CPU 温度监控
- 多显卡切换选择器
- 系统信息页新增网络 IP 区域
- 图表 X 轴中英切换
- 图表字体放大

### v2.0
- 首次发布

## 快速开始 / Quick Start

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行

```bash
python main.py
```

或双击 `start.bat`

## 项目结构 / Project Structure

```
├── main.py              # 入口
├── start.bat            # 启动脚本
├── requirements.txt     # 依赖
├── LICENSE              # MIT 开源证书
├── README.md
└── src/
    ├── monitor.py       # 系统信息采集
    ├── hardware.py      # 硬件信息采集
    ├── gpu_monitor.py   # GPU 实时监控
    ├── gui.py           # GUI 主窗口
    ├── charts.py        # 实时图表组件
    └── i18n.py          # 国际化
```

## 技术栈 / Tech Stack

- **Python 3.8+**
- **psutil** — 跨平台系统信息采集
- **matplotlib** — 图表渲染
- **tkinter** — GUI 框架（Python 内置）
- **nvidia-smi** — NVIDIA 显卡监控
- **WMI / PowerShell CIM** — 硬件信息查询

## 开源证书 / License

[MIT License](LICENSE)
