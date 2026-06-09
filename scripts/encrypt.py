#!/usr/bin/env python3
"""
Profile 加密脚本
将 profile/ 下的明文 .md 和 .json 文件加密为 .enc 文件。

用法：
    python scripts/encrypt.py                # 交互式输入口令
    python scripts/encrypt.py --delete       # 加密后删除明文
    python scripts/encrypt.py -p <password>  # 通过参数传入口令（注意 shell 历史）
"""

import argparse
import getpass
import os
import secrets
import struct
import sys
from pathlib import Path

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
except ImportError:
    print("错误：需要 cryptography 库。请运行：pip install cryptography")
    sys.exit(1)

MAGIC = b"PJENC001"
SALT_LEN = 32
NONCE_LEN = 12
KDF_ITERATIONS = 1_000_000


def derive_key(password: str, salt: bytes) -> bytes:
    """从口令派生 AES-256 密钥"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_data(password: str, plaintext: bytes) -> bytes:
    """加密数据，返回 MAGIC + salt + nonce + ciphertext"""
    salt = secrets.token_bytes(SALT_LEN)
    nonce = secrets.token_bytes(NONCE_LEN)
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return MAGIC + salt + nonce + ciphertext


def collect_files(profile_dir: Path) -> list[Path]:
    """收集需要加密的文件"""
    files = []
    # profile 根目录的 .md 和 .json
    for ext in ("*.md", "*.json"):
        files.extend(profile_dir.glob(ext))
    # profile/modules/ 下的 .md
    modules_dir = profile_dir / "modules"
    if modules_dir.is_dir():
        files.extend(modules_dir.glob("*.md"))
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(description="加密 profile 文件")
    parser.add_argument(
        "-p", "--password", help="加密口令（不推荐，会留在 shell 历史中）"
    )
    parser.add_argument(
        "--delete", action="store_true", help="加密后删除明文文件"
    )
    parser.add_argument(
        "-d", "--dir", default="profile", help="profile 目录路径（默认：profile）"
    )
    args = parser.parse_args()

    # 定位 profile 目录
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    profile_dir = project_root / args.dir

    if not profile_dir.is_dir():
        print(f"错误：目录不存在：{profile_dir}")
        sys.exit(1)

    # 获取口令
    if args.password:
        password = args.password
    else:
        password = getpass.getpass("请输入加密口令：")
        confirm = getpass.getpass("请再次输入口令：")
        if password != confirm:
            print("错误：两次口令不一致")
            sys.exit(1)

    if not password:
        print("错误：口令不能为空")
        sys.exit(1)

    files = collect_files(profile_dir)
    if not files:
        print("没有找到需要加密的文件")
        sys.exit(0)

    encrypted_count = 0
    skipped_count = 0

    for filepath in files:
        # 跳过已经是 .enc 的文件
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
            encrypted = encrypt_data(password, plaintext)
            enc_path.write_bytes(encrypted)
        except Exception as e:
            print(f"  失败 {filepath.relative_to(project_root)}：加密失败 ({e})")
            skipped_count += 1
            continue

        if args.delete:
            filepath.unlink()

        print(f"  加密 {filepath.relative_to(project_root)} -> {enc_path.name}")
        encrypted_count += 1

    print(f"\n完成：{encrypted_count} 个文件已加密", end="")
    if args.delete:
        print("（明文已删除）", end="")
    if skipped_count:
        print(f"，{skipped_count} 个跳过", end="")
    print()


if __name__ == "__main__":
    main()
