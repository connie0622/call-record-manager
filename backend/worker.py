import os
import subprocess
import openai
from pathlib import Path
from some_db import update_call_status, save_transcript_and_summary

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in environment")

openai.api_key = OPENAI_API_KEY

def ffmpeg_to_wav(src_path: str, dst_path: str):
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        src_path,
        "-ac",
        "1",
        "-ar",
        "16000",
        dst_path,
    ]
    subprocess.check_call(cmd)


def process_call(call_id: str, file_path: str, metadata: dict):
    try:
        update_call_status(call_id, "processing")
        base = Path(file_path)
        wav_path = str(base.with_suffix(".wav"))
        # Convert to WAV
        ffmpeg_to_wav(file_path, wav_path)
        # Transcribe via OpenAI Whisper
        with open(wav_path, "rb") as af:
            resp = openai.Audio.transcribe("whisper-1", af)
        transcript = resp.get("text", "")
        # Create prompt for summary
        prompt = (
            "你是通話紀錄摘要專家，請用繁體中文把以下逐字稿整理成 JSON，欄位包含: title, tldr, key_points (array), keywords (array), action_items (array of {task, owner, due}), timestamps (array of {time, note}).\n"
            f"逐字稿:\n{transcript}\n"
            "請僅回傳 JSON 並且不要有其他附加文字。"
        )
        chat_resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role":"system","content":"你是通話摘要專家，輸出繁體中文與 JSON 格式"},{"role":"user","content":prompt}],
            max_tokens=800,
        )
        summary_text = chat_resp["choices"][0]["message"]["content"].strip()
        save_transcript_and_summary(call_id, transcript, summary_text)
    except Exception as e:
        update_call_status(call_id, "error")
        # store a minimal summary explaining error
        save_transcript_and_summary(call_id, "", f"ERROR: {str(e)}")
        raise
