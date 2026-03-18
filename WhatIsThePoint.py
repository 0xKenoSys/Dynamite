import datetime

def main():
    print("孰轻孰重？")
    important_thing = input("现在最该做什么？\n>")

    # 获取当前时间
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 将回答追加保存到同一目录下的txt文件
    with open("focus_log.txt", "a", encoding="utf-8") as file:
        file.write(f"[{now}]{important_thing}\n")

    print("\n已记录，去完成它吧！")

if __name__ == "__main__":
    main()