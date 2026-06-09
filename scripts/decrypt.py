#!/usr/bin/env python3
"""
Profile 解密脚本
将 profile/ 下的 .enc 文件解密还原为明文。

用法：
    python scripts/decrypt.py           # 解密（不覆盖已有明文）
    python scripts/decrypt.py --force   # 强制覆盖
"""

import argparse
import sys
from pathlib import Path

from crypto import load_key, decrypt, collect_enc, get_project_root


def main():
    parser = argparse.ArgumentParser(description="解密 profile 文件")
    parser.add_argument(
        "--force", action="store_true", help="强制覆盖已有的明文文件"
    )
    parser.add_argument(
        "-d", "--dir", default="profile", help="profile 目录路径（默认：profile）"
    )
    args = parser.parse_args()

    project_root = get_project_root()
    profile_dir = project_root / args.dir

    if not profile_dir.is_dir():
        print(f"错误：目录不存在：{profile_dir}")
        sys.exit(1)

    key = load_key()
    files = collect_enc(profile_dir)

    if not files:
        print("没有找到 .enc 文件")
        sys.exit(0)

    decrypted_count = 0
    skipped_count = 0
    failed_count = 0

    for enc_path in files:
        orig_name = enc_path.name.removesuffix(".enc")
        orig_path = enc_path.parent / orig_name

        if orig_path.exists() and not args.force:
            print(f"  跳过 {orig_path.relative_to(project_root)}：明文已存在")
            skipped_count += 1
            continue

        try:
            encrypted = enc_path.read_bytes()
        except Exception as e:
            print(f"  跳过 {enc_path.relative_to(project_root)}：读取失败 ({e})")
            skipped_count += 1
            continue

        try:
            plaintext = decrypt(key, encrypted)
        except Exception as e:
            print(f"  失败 {enc_path.relative_to(project_root)}：解密失败 — {e}")
            failed_count += 1
            continue

        try:
            orig_path.write_bytes(plaintext)
        except Exception as e:
            print(f"  失败 {orig_path.relative_to(project_root)}：写入失败 ({e})")
            failed_count += 1
            continue

        print(f"  解密 {enc_path.name}")
        decrypted_count += 1

    print(f"\n完成：{decrypted_count} 个文件已解密", end="")
    if skipped_count:
        print(f"，{skipped_count} 个跳过", end="")
    if failed_count:
        print(f"，{failed_count} 个失败", end="")
    print()


if __name__ == "__main__":
    main()
