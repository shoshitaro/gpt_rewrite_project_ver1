# full_pipeline_openai.py（ocr_texts に依存しない簡潔版）
import os
import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# === ユーザー設定 ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

# === 設定ファイル読み込み ===
config_path = ".streamlit_temp_config_openai.txt"
config = {}
with open(config_path, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip() and "=" in line:
            key, value = line.strip().split("=", 1)
            config[key] = value

INTRO = config.get("INTRO", "")
ENDING = config.get("ENDING", "")
SPEAKER_PROMPT = config.get("SPEAKER_PROMPT", "")
VOICE = config.get("VOICE", "nova").lower()
OUTPUT_DIR = config.get("OUTPUT_DIR", "output_audio")
INPUT_FILE = config.get("INPUT_FILE", "uploaded/uploaded_text.txt")
CLEAR_OUTPUTS = config.get("CLEAR_OUTPUTS") == "1"

os.makedirs("rewritten_texts", exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ ファイルの存在チェック
if not os.path.isfile(INPUT_FILE):
    raise FileNotFoundError(f"❌ 入力ファイルが存在しません: {INPUT_FILE}")

# === 入力テキスト読み込み ===
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    text = f.read()

# === リライト処理 ===
def rewrite_text(text):
    prompt = f"{INTRO}\n\n{text}\n\n{ENDING}"
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "あなたはナレーションライターです。"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# === 音声合成処理 ===
def synthesize_audio(text, output_path):
    response = client.audio.speech.create(
        model="tts-1",
        voice=VOICE,
        input=text,
        response_format="mp3"
    )
    with open(output_path, "wb") as f:
        f.write(response.content)

# === 実行処理 ===
base_name = os.path.splitext(os.path.basename(INPUT_FILE))[0]
rewritten = rewrite_text(text)
rewritten_path = os.path.join("rewritten_texts", f"{base_name}_rewritten.txt")
with open(rewritten_path, "w", encoding="utf-8") as f:
    f.write(rewritten)

audio_path = os.path.join(OUTPUT_DIR, f"{base_name}.mp3")
synthesize_audio(rewritten, audio_path)

print("✅ 全ての処理が完了しました！")
