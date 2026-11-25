#!/usr/bin/env python3
"""从 WordBook 的 words.json 按子目录导出例句。"""

"""
对words.json这个文件中的内容进行提取，比如说指定”常用短语/日常洗漱与个人卫生“，
就会把当前目录下的所有的单词例句提取出来，保存到一个txt文件中，不会提取括号内的中文。
每个例句占一行
"""

import json
import re
from pathlib import Path
from tempfile import NamedTemporaryFile

# 修改这里的目录和文件路径。默认读写脚本所在的文件夹。
SCRIPT_DIR = Path(__file__).resolve().parent
WORDS_FILE = SCRIPT_DIR / "file" / "words.json"
DIRECTORY_PATH = "常用短语/日常洗漱与个人卫生"
OUTPUT_FILE = SCRIPT_DIR / "file" / "article.txt"

HAN_CHARACTERS = re.compile(
    r"[\u3007\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff" r"\U00020000-\U0002fa1f\U00030000-\U000323af]"
)


def clean_example(example):
    """删除含中文的圆括号注释。支持全角、半角和嵌套括号。"""
    openings = []
    removed = []
    for index, character in enumerate(example):
        if character in "(（":
            openings.append(index)
        elif character in ")）" and openings:
            start = openings.pop()
            if HAN_CHARACTERS.search(example, start + 1, index):
                while removed and removed[-1][0] > start:
                    removed.pop()
                removed.append((start, index + 1))

    parts = []
    cursor = 0
    for start, end in removed:
        parts.append(example[cursor:start])
        cursor = end
    parts.append(example[cursor:])
    line = " ".join(" ".join(parts).split())
    return re.sub(r" (?=[,.!?;:])", "", line)


def find_subdirectory_id(directories, directory_path):
    names = [part.strip() for part in directory_path.replace("／", "/").split("/")]
    if len(names) != 2 or not all(names):
        raise ValueError("请将 DIRECTORY_PATH 填为「一级目录/子目录」。")
    parent_name, subdirectory_name = names

    for directory in directories:
        if directory["name"] == parent_name:
            for subdirectory in directory.get("subdirectories", []):
                if subdirectory["name"] == subdirectory_name:
                    return subdirectory["id"]
    raise ValueError(f"找不到目录「{directory_path}」，请检查目录名。")


def creation_order(word):
    # 新版 WordBook 用递增的短编号记录添加顺序。
    word_id = str(word.get("id", ""))
    if word_id.isdecimal():
        return (0, int(word_id))
    return (1, word.get("createdAt") or "")


def collect_examples(data, directory_path):
    if not isinstance(data, dict) or not all(isinstance(data.get(field), list) for field in ("directories", "words")):
        raise ValueError("请选择包含 directories 和 words 的 WordBook 数据文件。")

    subdirectory_id = find_subdirectory_id(data["directories"], directory_path)
    words = [word for word in data["words"] if word.get("subdirectoryId") == subdirectory_id]
    lines = []
    for word in sorted(words, key=creation_order):
        examples = word.get("examples") or []
        if isinstance(examples, str):
            examples = examples.splitlines()
        for example in examples:
            if isinstance(example, str):
                cleaned = clean_example(example)
                if cleaned:
                    lines.append(cleaned)
    return lines


def write_examples(output_file, examples):
    output_file.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = None
    try:
        with NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=output_file.parent, delete=False
        ) as stream:
            temporary_file = Path(stream.name)
            stream.writelines(f"{example}\n" for example in examples)
        temporary_file.replace(output_file)
    finally:
        if temporary_file is not None:
            temporary_file.unlink(missing_ok=True)


def main():
    try:
        if WORDS_FILE.resolve() == OUTPUT_FILE.resolve():
            raise ValueError("请将 OUTPUT_FILE 指向一个单独的 TXT 文件。")
        with WORDS_FILE.open(encoding="utf-8-sig") as stream:
            data = json.load(stream)
        examples = collect_examples(data, DIRECTORY_PATH)
        write_examples(OUTPUT_FILE, examples)
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"导出失败：{error}") from None
    print(f"已导出 {len(examples)} 条例句到 {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
