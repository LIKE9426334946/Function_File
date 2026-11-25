# 用来把英文转为音频


import asyncio
import edge_tts
from pathlib import Path

VOICE = "en-US-JennyNeural"


async def main():
    BASE_DIR = Path(__file__).resolve().parent

    with open(BASE_DIR / "article.txt", "r", encoding="utf-8") as f:
        text = f.read()

    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
    )

    await communicate.save(BASE_DIR / "mp4" / "article.mp3")


if __name__ == "__main__":
    asyncio.run(main())
