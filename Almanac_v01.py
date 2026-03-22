from lunar_python import Solar
from datetime import datetime

def show_today_almanac():
    # 1.获取当前系统公历时间
    now = datetime.now()
    solar = Solar.fromYmd(now.year, now.month, now.day)

    # 2.转换为农历对象
    lunar = solar.getLunar()

    # 3.提取并打印万年历核心数据
    print("="*30)
    print("今日万年历")
    print("="*30)

    print(f"【公历】{solar.getYear()}年{solar.getMonth()}月{solar.getDay()}日 星期{solar.getWeekInChinese()}")
    print(f"【农历】{lunar.getYearInChinese()}年 {lunar.getMonthInChinese()}月 {lunar.getDayInChinese()}日")
    print(f"【干支】{lunar.getYearInGanZhi()}年 {lunar.getMonthInGanZhi()}月 {lunar.getDayInGanZhi()}日")

    # 获取黄历宜忌
    day_yi = ",".join(lunar.getDayYi())
    day_ji = ",".join(lunar.getDayJi())

    print("-"*30)
    print(f"【宜】{day_yi if day_yi else '无'}")
    print(f"【忌】{day_ji if day_ji else '无'}")
    print("="*30)

if __name__ == "__main__": show_today_almanac() # 这一行不能缩进到函数内部
