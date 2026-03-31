import matplotlib.pyplot as plt
import matplotlib as mpl  # <-- 新增这一行
import re
from datetime import datetime
import os

# --- 配置区 ---
LOG_FILE = "screen_logs.txt"
THEME_COLOR = '#00FF7F'
BAR_COLOR = '#8A2BE2'
BG_COLOR = '#1e1e1e'
TEXT_COLOR = '#d4d4d4'

# ✅ 新增：设置中文字体（macOS专用）
mpl.rcParams['font.family'] = ['Heiti TC'] # 使用系统自带的黑体
mpl.rcParams['axes.unicode_minus'] = False # 解决负号显示问题

# ... (后面的代码保持不变) ...


import matplotlib.pyplot as plt
import re
from datetime import datetime
import os

# --- 配置区 ---
LOG_FILE = "screen_logs.txt"
THEME_COLOR = '#00FF7F'  # 极客绿
BAR_COLOR = '#8A2BE2'  # 赛博紫 (BlueViolet) 用来区分 App
BG_COLOR = '#1e1e1e'  # 深色背景
TEXT_COLOR = '#d4d4d4'  # 浅灰文字


def parse_app_usage():
    if not os.path.exists(LOG_FILE):
        print("❌ 没找到日志文件，先去跑一会儿监控吧！")
        return {}

    app_stats = {}  # { "Chrome": 120.5, "PyCharm": 60.0 }
    current_app = "Unknown"
    last_time = None

    # 正则提取时间戳
    time_pattern = re.compile(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]")

    print("正在解剖日志...")
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        match = time_pattern.search(line)
        if not match: continue

        timestamp_str = match.group(1)
        current_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

        # 计算上一段的时间
        if last_time:
            duration = (current_time - last_time).total_seconds() / 60  # 分钟

            # 只有在屏幕点亮且非休眠状态下，才计入 App 时间
            # 如果上一行是 STOP，说明这段时间是锁屏，不计入任何 App
            if duration > 0 and current_app != "Screen Locked" and current_app != "Unknown":
                app_stats[current_app] = app_stats.get(current_app, 0) + duration

        # 更新状态
        if "[FOCUS]" in line:
            # 提取 App 名字: 📱 [FOCUS] Switched to: WeChat
            parts = line.split("Switched to: ")
            if len(parts) > 1:
                current_app = parts[1].strip()

        elif "[STOP]" in line:
            current_app = "Screen Locked"  # 标记为锁屏状态

        elif "[START]" in line:
            current_app = "Unknown"  # 刚解锁还没切换软件，暂时未知

        elif "初始应用" in line:
            parts = line.split("初始应用: ")
            if len(parts) > 1:
                current_app = parts[1].strip()

        last_time = current_time

    return app_stats


def plot_usage(stats):
    if not stats:
        print("⚠️ 数据不足，还没监测到 App 切换记录。")
        return

    # 排序：把用得最多的排在上面
    sorted_apps = sorted(stats.items(), key=lambda x: x[1], reverse=False)  # 从小到大排，画图时大的在上面
    names = [x[0] for x in sorted_apps]
    times = [x[1] for x in sorted_apps]

    print(f"统计完成！监测到 {len(names)} 个应用。")

    # 开始画图
    fig, ax = plt.subplots(figsize=(10, 6))

    # 极客配色
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.spines['bottom'].set_color(TEXT_COLOR)
    ax.spines['left'].set_color(TEXT_COLOR)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors=TEXT_COLOR)

    # 画水平条形图
    bars = ax.barh(names, times, color=BAR_COLOR, height=0.6)

    # 在柱子旁边标上具体分钟数
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height() / 2,
                f'{int(width)} min',
                ha='left', va='center', color=THEME_COLOR, fontsize=10)

    plt.title("KenoSys Application Usage (Minutes)", color=THEME_COLOR, fontsize=14, pad=20)
    plt.xlabel("Duration (mins)", color=TEXT_COLOR)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    stats = parse_app_usage()
    plot_usage(stats)
