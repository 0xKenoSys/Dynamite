from youtube_transcript_api import YouTubeTranscriptApi
video_id = "03RJ0eFQYYo"

try:
    # transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en',' zh-Hans', 'zh-Hant'])
    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch(video_id, languages=['en', 'zh-Hans', 'zh-Hant'])

    full_text = ""
    for line in transcript:
        # full_text += line['text'] + "\n"
        full_text += line.text + "\n"

    file_name = f"{video_id}_subtitle.txt"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(full_text)

    print(f"抓取成功，文件[{file_name}]已保存到当前目录。")

except Exception as e:
    print(f"报错了，错误信息是：{e}")