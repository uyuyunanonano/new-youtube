import os
import time
import yt_dlp
from flask import Flask, render_template, request, send_from_directory
import threading

app = Flask(__name__)

# 保存先ディレクトリ
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# yt-dlpのオプション
ydl_opts = {
    'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(id)s.%(ext)s'),
    'format': 'best',
}

# 動画のタイムスタンプ付きで保存する
def delete_old_files():
    while True:
        time.sleep(3600)  # 1時間ごとに確認
        current_time = time.time()
        for filename in os.listdir(DOWNLOAD_FOLDER):
            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                file_creation_time = os.path.getctime(file_path)
                if current_time - file_creation_time > 86400:  # 24時間(86400秒)以上経過
                    os.remove(file_path)
                    print(f"{filename} has been deleted (older than 24 hours).")

# バックグラウンドで削除処理を実行
threading.Thread(target=delete_old_files, daemon=True).start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    video_url = request.form['url']
    try:
        # yt-dlpで動画をダウンロード
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_title = info_dict.get('title', 'Untitled')
            video_id = info_dict.get('id')
            video_path = os.path.join(DOWNLOAD_FOLDER, f'{video_id}.mp4')
        return render_template('download.html', video_path=video_path, video_title=video_title)
    except Exception as e:
        return f"Error: {e}"

@app.route('/videos/<filename>')
def video(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
