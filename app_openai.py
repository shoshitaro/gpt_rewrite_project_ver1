# Streamlit版：フルパイプラインUI（OpenAI音声API専用）
import streamlit as st
import subprocess
from dotenv import load_dotenv
load_dotenv()
import os
import time
import re

# VOICE選択肢（OpenAI TTS）
VOICE_OPTIONS = {
    "Alloy": "落ち着いたトーン、聞き取りやすい（解説、ナレーション）",
    "Echo": "明るくフレンドリー、親しみやすい（案内、カジュアルトーク）",
    "Fable": "優しく温かみあり、やや高め（物語、子供向け）",
    "Onyx": "低音で力強く落ち着いた印象（プレゼン、ビジネス）",
    "Nova": "明瞭でエネルギッシュ（ニュース、情報提供）",
    "Shimmer": "軽快で明るいポップな声（エンタメ、CM）",
    "Ash": "クールで落ち着いた声（ドキュメンタリー）",
    "Ballad": "感情豊かで表現力あり（感動ストーリー）",
    "Coral": "柔らかく優しいトーン（リラクゼーション）",
    "Sage": "知的で信頼感あり（教育、講義）",
    "Verse": "詩的で静かな表現（詩の朗読、文学）"
}

st.set_page_config(page_title="リライト＆音声化パイプライン（OpenAI版）", layout="centered")
st.markdown("""
## 📚 本の原稿→リライト→音声化ツール
<span style='font-size: 16px;'>〜原稿を入れれば一括でChatGPTでリライト、OpenAI TTSで音声化〜</span>
""", unsafe_allow_html=True)

st.markdown("----")

# === 入力：テキストファイルアップロード ===
st.markdown("### 📁 テキストファイルをアップロード")
uploaded_file = st.file_uploader(".txt ファイルを選択", type="txt")

st.markdown("----")

# === 入力：リライトプロンプト編集欄 ===
st.markdown("### 📝 リライトスタイルを選択")
style_default = "YouTuberの一人語り風ナレーション"
custom_style = st.text_input("🔹 ナレーションスタイル", value=style_default)
ending_default = "文末は「〜なんですよ」「〜なんです」「〜って思いませんか？」など、やさしく語りかけるスタイルにしてください。"
custom_ending = st.text_area("🔹 文末・語尾・口調のスタイル指示", value=ending_default, height=80)

st.markdown("----")

# === OpenAI音声スタイル ===
st.markdown("### 🎤 話者のスタイルを選ぶ（OpenAI TTS向け）")
selected_voice = st.selectbox("🔸 TTSボイスを選択", list(VOICE_OPTIONS.keys()))
st.caption(f"📝 特徴：{VOICE_OPTIONS[selected_voice]}")

with st.expander("💡 プロンプト作成のガイド（ChatGPTに入力して活用）"):
    st.markdown("""
以下のプロンプトをChatGPTに入力すると、精度の高い指示が得られます。
```text
以下のTTSプロンプトを完成させるために、私に対して必要な情報を引き出す質問を順番にしてください。
...（省略）...
```""")

openai_voice_prompt = st.text_area("🎙️ 話し方のスタイル指示文（ChatGPTで出力された内容を貼り付けてください）", "", height=160)

st.markdown("----")

# === 出力先フォルダ：新規作成のみ ===
st.markdown("### 📂 音声の出力先フォルダを新規作成")
project_base_dir = "projects"
os.makedirs(project_base_dir, exist_ok=True)

custom_output_dir = None
new_project_name = st.text_input("作成する音声データのファイル名を入力（projectsに保存されます）", "")
if new_project_name:
    new_project_name = new_project_name.strip()
    if not re.match(r"^[\w\-]+$", new_project_name):
        st.warning("⚠️ 半角英数字とハイフン以外の文字は使えません。")
    else:
        custom_output_dir = os.path.join(project_base_dir, new_project_name)
        os.makedirs(custom_output_dir, exist_ok=True)

clear_outputs = st.checkbox("🧹 実行前に前回の出力を削除する")

st.markdown("----")

# === 実行ボタン ===
if st.button("🚀 リライト＋音声化を実行（OpenAI）"):
    status_placeholder = st.empty()
    if uploaded_file is None:
        st.warning("⚠️ テキストファイルをアップロードしてください。")
    elif not custom_output_dir:
        st.warning("⚠️ 出力フォルダが未設定です。")
    elif not openai_voice_prompt.strip():
        st.warning("⚠️ 音声スタイル指示文が入力されていません。")
    elif not selected_voice:
        st.warning("⚠️ TTSボイスが未選択です。")
    else:
        if clear_outputs:
            for folder in ["rewritten_texts", "rewritten_texts_split"]:
                if os.path.exists(folder):
                    for f in os.listdir(folder):
                        os.remove(os.path.join(folder, f))
            if os.path.exists(custom_output_dir):
                for f in os.listdir(custom_output_dir):
                    os.remove(os.path.join(custom_output_dir, f))

        os.makedirs("uploaded", exist_ok=True)  # ✅ フォルダがなければ作成
        input_file_path = os.path.join("uploaded", uploaded_file.name)
        with open(input_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        status_placeholder.info("⏳ full_pipeline_openai.py を実行中...")

        intro_text = f"以下の書籍原稿を、{custom_style}にリライトしてください。"
        with open(".streamlit_temp_config_openai.txt", "w", encoding="utf-8") as f:
            f.write(f"INTRO={intro_text}\n")
            f.write(f"ENDING={custom_ending}\n")
            f.write(f"SPEAKER_PROMPT={openai_voice_prompt}\n")
            f.write(f"VOICE={selected_voice}\n")
            f.write(f"OUTPUT_DIR={custom_output_dir}\n")
            f.write(f"INPUT_FILE={input_file_path}\n")
            if clear_outputs:
                f.write("CLEAR_OUTPUTS=1\n")

        script_path = os.path.join(os.path.dirname(__file__), "full_pipeline_openai.py")
        env = os.environ.copy()
        env["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
        result = subprocess.run(["python3", script_path], capture_output=True, text=True, env=env)
        if result.returncode == 0:
            status_placeholder.success("✅ 実行が完了しました！")
            st.code(result.stdout)
        else:
            status_placeholder.error("❌ エラーが発生しました")
            st.text(result.stderr)

st.markdown("----")

# === 出力表示：MP3ファイル ===
if custom_output_dir:
    audio_files = sorted(os.listdir(custom_output_dir))
    if audio_files:
        st.markdown("### 🎵 出力されたMP3ファイル")
        for file in audio_files:
            if file.endswith(".mp3"):
                file_path = os.path.join(custom_output_dir, file)
                with open(file_path, "rb") as audio:
                    st.audio(audio.read(), format="audio/mp3")
                with open(file_path, "rb") as audio:
                    st.download_button("⬇️ MP3をダウンロード", data=audio, file_name=file)
