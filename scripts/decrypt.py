#!/usr/bin/env python3
"""
Profile 解密脚本
将 profile/ 下的 .enc 文件解密还原为明文。

用法：
    python scripts/decrypt.py                # 交互式输入口令
    python scripts/decrypt.py --force        # 强制覆盖已有的明文
    python scripts/decrypt.py -p <password>  # 通过参数传入口令（注意 shell 历史）
"""

import argparse
import getpass
import os
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


def decrypt_data(password: str, data: bytes) -> bytes:
    """解密数据，输入为 MAGIC + salt + nonce + ciphertext"""
    if len(data) < 8 + SALT_LEN + NONCE_LEN + 16:
        raise ValueError("文件过短，不是有效的加密文件")

    magic = data[:8]
    if magic != MAGIC:
        raise ValueError("文件格式无效（magic 不匹配）")

    salt = data[8 : 8 + SALT_LEN]
    nonce = data[8 + SALT_LEN : 8 + SALT_LEN + NONCE_LEN]
    ciphertext = data[8 + SALT_LEN + NONCE_LEN :]

    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)


def collect_enc_files(profile_dir: Path) -> list[Path]:
    """收集所有 .enc 文件"""
    files = []
    files.extend(profile_dir.glob("*.enc"))
    modules_dir = profile_dir / "modules"
    if modules_dir.is_dir():
        files.extend(modules_dir.glob("*.enc"))
    return sorted(files)


def main():
    parser = argparse.ArgumentParser(description="解密 profile 文件")
    parser.add_argument(
        "-p", "--password", help="解密口令（不推荐，会留在 shell 历史中）"
    )
    parser.add_argument(
        "--force", action="store_true", help="强制覆盖已有的明文文件"
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
        password = getpass.getpass("请输入解密口令：")

    if not password:
        print("错误：口令不能为空")
        sys.exit(1)

    files = collect_enc_files(profile_dir)
    if not files:
        print("没有找到 .enc 文件")
        sys.exit(0)

    decrypted_count = 0
    skipped_count = 0
    failed_count = 0

    for enc_path in files:
        # 还原原始文件名
        orig_name = enc_path.name.removesuffix(".enc")
        orig_path = enc_path.parent / orig_name

        # 检查明文是否已存在
        if orig_path.exists() and not args.force:
            print(f"  跳过 {orig_path.relative_to(project_root)}：明文已存在（用 --force 覆盖）")
            skipped_count += 1
            continue

        try:
            encrypted = enc_path.read_bytes()
        except Exception as e:
            print(f"  跳过 {enc_path.relative_to(project_root)}：读取失败 ({e})")
            skipped_count += 1
            continue

        try:
            plaintext = decrypt_data(password, encrypted)
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

        print(f"  解密 {enc_path.name} -> {orig_path.relative_to(project_root)}")
        decrypted_count += 1

    print(f"\n完成：{decrypted_count} 个文件已解密", end="")
    if skipped_count:
        print(f"，{skipped_count} 个跳过", end="")
    if failed_count:
        print(f"，{failed_count} 个失败", end="")
    print()


if __name__ == "__main__":
    main()
