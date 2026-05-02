# 系统监控工具 v1.0

一个基于 Python + tkinter 的实时系统资源监控桌面工具。

## 功能特性

### CPU 监控
- 实时显示总体 CPU 使用率
- 每个核心独立使用率显示
- CPU 频率监控
- 使用率趋势图

### 内存监控
- 物理内存使用率、已用、可用、总量
- 交换区使用情况
- 可视化进度条
- 使用率趋势图

### 磁盘监控
- 所有磁盘分区信息（设备、容量、使用率）
- 实时读写速度显示
- 分区详情表格

### 显卡监控
- 自动检测显卡型号（NVIDIA / AMD / Intel）
- GPU 使用率实时监控
- 显存使用率、已用/总量
- 温度监控
- 功耗监控
- 使用率趋势图

### 网络监控
- 上传/下载速度实时显示
- 总流量统计
- 上传/下载速度趋势图
- 活跃连接数

### 进程管理
- 进程列表（按内存排序）
- 显示 PID、名称、CPU%、内存%、状态、用户
- 支持终止指定进程

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行程序

```bash
python main.py
```

## 项目结构

```
SystemMonitor/
├── main.py              # 程序入口
├── requirements.txt     # 依赖列表
├── LICENSE              # MIT 许可证
├── src/
│   ├── monitor.py       # 系统信息采集模块
│   ├── hardware.py      # 硬件信息采集模块
│   ├── gpu_monitor.py   # GPU 实时监控模块
│   ├── gui.py           # GUI 主窗口
│   └── charts.py        # 实时图表组件
└── tests/
    └── test_monitor.py  # 单元测试
```

## 技术栈

- **Python 3.8+**
- **psutil** - 跨平台系统信息采集
- **matplotlib** - 图表绘制
- **tkinter** - GUI 界面（Python 内置）

## 许可证

[MIT License](LICENSE)
