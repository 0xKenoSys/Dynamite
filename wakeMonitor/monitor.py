import time
import sys
from Foundation import NSObject, NSDistributedNotificationCenter
from AppKit import NSWorkspace, NSWorkspaceDidActivateApplicationNotification
from PyObjCTools import AppHelper

# --- 配置区 ---
LOG_FILE = "screen_logs.txt"


class ScreenObserver(NSObject):

    def start_monitoring(self):
        """手动初始化监听器"""
        self.last_app = None
        self.start_time = time.time()

        # 注册监听器
        nc = NSDistributedNotificationCenter.defaultCenter()
        ws = NSWorkspace.sharedWorkspace().notificationCenter()

        # ⚠️ 修改点1：这里名字变了，selector 必须和下面的函数名对应（Python加_，这里加:）

        # 1. 监听屏幕开关
        nc.addObserver_selector_name_object_(self, 'handleUnlock:', 'com.apple.screenIsUnlocked', None)
        nc.addObserver_selector_name_object_(self, 'handleLock:', 'com.apple.screenIsLocked', None)

        # 2. 监听软件切换
        ws.addObserver_selector_name_object_(self, 'handleAppSwitch:', NSWorkspaceDidActivateApplicationNotification,
                                             None)

    def _format_duration(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02d}时{int(m):02d}分{int(s):02d}秒"

    def _write_to_file(self, message):
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime())
        log_line = f"{timestamp} {message}\n"
        print(log_line.strip())
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_line)

    # ⚠️ 修改点2：函数名变成了 驼峰式 + 下划线 (Python里的下划线 = ObjC里的冒号)

    def handleLock_(self, notification):
        """屏幕锁定"""
        duration = time.time() - self.start_time
        readable = self._format_duration(duration)
        self._write_to_file(f"🔴 [STOP] Screen Locked (闭关) | 本次专注: {readable}")
        self.start_time = time.time()

    def handleUnlock_(self, notification):
        """屏幕解锁"""
        self.start_time = time.time()
        self._write_to_file(f"🟢 [START] Screen Unlocked (出关)")

    def handleAppSwitch_(self, notification):
        """软件切换"""
        try:
            app_info = notification.userInfo()
            if 'NSWorkspaceApplicationKey' in app_info:
                app = app_info['NSWorkspaceApplicationKey']
                app_name = app.localizedName()

                if app_name != self.last_app:
                    self._write_to_file(f"📱 [FOCUS] Switched to: {app_name}")
                    self.last_app = app_name
        except Exception as e:
            pass  # 只要不出错，就别吵我


if __name__ == "__main__":
    observer = ScreenObserver.alloc().init()
    observer.start_monitoring()

    print("\n" + "=" * 50)
    print("   KenoSys 全频段监控系统 v2.1 (稳定版)")
    print("   启动逻辑: 屏幕锁 + 应用追踪")
    print("   Waiting... (Ctrl+C to Stop)")
    print("=" * 50 + "\n")

    try:
        current_app = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName']
        observer._write_to_file(f"🚀 SYSTEM START / 初始应用: {current_app}")
    except:
        pass

    AppHelper.runConsoleEventLoop()
