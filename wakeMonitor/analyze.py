import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import re
import os

# --- 配置区 ---
LOG_FILE = "screen_logs.txt"
THEME_COLOR = '#00FF7F'  # 极客绿 (SpringGreen)
BG_COLOR = '#1e1e1e'  # IDE 深色背景
TEXT_COLOR = '#d4d4d4'  # 浅灰文字


def parse_logs():
    """解析日志，提取所有的 (开始时间, 持续时长) 片段"""
    intervals = []
    current_start = None

    if not os.path.exists(LOG_FILE):
        print(f"❌ 找不到日志文件: {LOG_FILE}")
        return []

    print("正在读取档案库...")
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 正则提取时间戳
    # 格式: [2026-02-04 16:04:51]
    time_pattern = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]")

    for line in lines:
        match = time_pattern.search(line)
        if not match:
            continue

        timestamp_str = match.group(1)
        current_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

        # 逻辑判断
        if "[START]" in line or "Hardware Wake" in line or "Screen Unlocked" in line:
            # 如果已经有一个开始时间没闭合，说明上一次可能异常退出了，重置为新的开始
            current_start = current_time

        elif "[STOP]" in line or "Hardware Sleep" in line or "Screen Locked" in line:
            if current_start:
                # 找到了一对完整的 (Start -> Stop)
                duration = (current_time - current_start).total_seconds() / 60  # 转为分钟
                # 只有时长合理的才记录 (过滤掉小于1秒的抖动)
                if duration > 0.01:
                    intervals.append((current_start, duration))
                current_start = None

    # 如果最后还在运行（只有 Start 没有 Stop），假设它运行到现在（或者图表绘制时刻）
    if current_start:
        duration = (datetime.now() - current_start).total_seconds() / 60
        intervals.append((current_start, duration))

    return intervals


def plot_timeline(intervals):
    if not intervals:
        print("⚠️ 没有提取到有效数据，可能是日志太少或格式不对。")
        return

    print(f"提取到 {len(intervals)} 个活跃片段，正在渲染...")

    fig, ax = plt.subplots(figsize=(12, 4))

    # 设置暗黑主题
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.spines['bottom'].set_color(TEXT_COLOR)
    ax.spines['top'].set_color(BG_COLOR)
    ax.spines['left'].set_color(BG_COLOR)
    ax.spines['right'].set_color(BG_COLOR)
    ax.tick_params(axis='x', colors=TEXT_COLOR)
    ax.tick_params(axis='y', colors=BG_COLOR)  # 隐藏Y轴刻度

    # 绘制核心数据 (Broken Barh)
    # matplotlib 需要的数据格式: [(start_time_float, duration_float), ...]
    # 我们需要把 datetime 转换为 matplotlib 的内部 float 格式

    chart_data = []
    for start_time, duration_mins in intervals:
        # 转换 duration 从分钟到天 (matplotlib x轴是天)
        duration_days = duration_mins / (24 * 60)
        chart_data.append((mdates.date2num(start_time), duration_days))

    # yRange (10, 5) 代表条形的高度和位置
    ax.broken_barh(chart_data, (10, 5), facecolors=THEME_COLOR, edgecolors='none')

    # X轴格式化
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))  # 每2小时一个刻度
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

    # 标题和标签
    plt.title("KenoSys Daily Activity Stream", color=TEXT_COLOR, fontsize=14, pad=20)
    plt.yticks([])  # 隐藏Y轴

    # 计算总时长
    total_mins = sum(duration for _, duration in intervals)
    hours = int(total_mins // 60)
    mins = int(total_mins % 60)

    # 在图表下方显示统计
    plt.xlabel(f"Total Active Time: {hours}h {mins}m", color=THEME_COLOR, fontsize=12)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    data = parse_logs()
    plot_timeline(data)
