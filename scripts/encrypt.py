#!/usr/bin/env python3
"""
Profile 加密脚本
将 profile/ 下的明文 .md 和 .json 文件加密为 .enc 文件。

用法：
    python scripts/encrypt.py --gen-key     # 首次：生成密钥
    python scripts/encrypt.py               # 加密（保留明文）
    python scripts/encrypt.py --delete      # 加密后删除明文
"""

import argparse
import sys
from pathlib import Path

from crypto import gen_key, load_key, encrypt, collect_plaintext, get_project_root


def main():
    parser = argparse.ArgumentParser(description="加密 profile 文件")
    parser.add_argument(
        "--gen-key", action="store_true", help="生成新的加密密钥（首次使用）"
    )
    parser.add_argument(
        "--delete", action="store_true", help="加密后删除明文文件"
    )
    parser.add_argument(
        "-d", "--dir", default="profile", help="profile 目录路径（默认：profile）"
    )
    args = parser.parse_args()

    project_root = get_project_root()

    # 生成密钥模式
    if args.gen_key:
        key_hex = gen_key()
        print(f"密钥已生成：scripts/.key")
        print(f"密钥（hex）：{key_hex[:8]}...{key_hex[-8:]}")
        print("请妥善保管，丢失后加密文件将无法解密！")
        return

    # 加密模式
    profile_dir = project_root / args.dir
    if not profile_dir.is_dir():
        print(f"错误：目录不存在：{profile_dir}")
        sys.exit(1)

    key = load_key()
    files = collect_plaintext(profile_dir)

    if not files:
        print("没有找到需要加密的文件")
        sys.exit(0)

    encrypted_count = 0
    skipped_count = 0

    for filepath in files:
        if filepath.suffix == ".enc":
            continue

        enc_path = filepath.with_suffix(filepath.suffix + ".enc")

        try:
            plaintext = filepath.read_bytes()
        except Exception as e:
            print(f"  跳过 {filepath.relative_to(project_root)}：读取失败 ({e})")
            skipped_count += 1
            continue

        try:
            encrypted = encrypt(key, plaintext)
            enc_path.write_bytes(encrypted)
        except Exception as e:
            print(f"  失败 {filepath.relative_to(project_root)}：加密失败 ({e})")
            skipped_count += 1
            continue

        if args.delete:
            filepath.unlink()

        print(f"  加密 {filepath.relative_to(project_root)}")
        encrypted_count += 1

    print(f"\n完成：{encrypted_count} 个文件已加密", end="")
    if args.delete:
        print("（明文已删除）", end="")
    if skipped_count:
        print(f"，{skipped_count} 个跳过", end="")
    print()


if __name__ == "__main__":
    main()
