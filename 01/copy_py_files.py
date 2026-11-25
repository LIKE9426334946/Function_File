"""
可以指定一个源目录，比如Stage_01_OxfordIIITPet/models这个目录
可以指定多个目标目录，会把源目录下面的所有py文件复制到目标目录下面
如果目标目录下面存在同名文件，就进行替换，不用提示
"""

import shutil
from pathlib import Path

# ==================== 配置区域 ====================

SOURCE_DIR = Path(r"D:\02_MyCode\Stage_01_OxfordIIITPet\models")

TARGET_DIRS = [
    Path(r"D:\02_MyCode\Stage_02_ACDC\models"),
    Path(r"D:\02_MyCode\Stage_03_VOC2012\models"),
]

# 是否递归遍历子目录
RECURSIVE = False

# ==================================================


def copy_py_files():

    if not SOURCE_DIR.is_dir():
        print(f"源目录不存在：{SOURCE_DIR}")
        return

    # 获取所有 py 文件
    if RECURSIVE:
        py_files = list(SOURCE_DIR.rglob("*.py"))
    else:
        py_files = list(SOURCE_DIR.glob("*.py"))

    if not py_files:
        print("没有找到 py 文件！")
        return

    total = 0

    for target_dir in TARGET_DIRS:

        target_dir.mkdir(parents=True, exist_ok=True)

        for src_file in py_files:

            # 保留相对目录结构
            relative_path = src_file.relative_to(SOURCE_DIR)

            dst_file = target_dir / relative_path
            dst_file.parent.mkdir(parents=True, exist_ok=True)

            # 直接复制，存在同名文件时自动覆盖
            shutil.copy2(src_file, dst_file)

            total += 1

        print(f"复制完成：{target_dir}")

    print("\n========== 全部完成 ==========")
    print(f"源文件数量：{len(py_files)}")
    print(f"目标目录数量：{len(TARGET_DIRS)}")
    print(f"总复制次数：{total}")


if __name__ == "__main__":
    copy_py_files()
