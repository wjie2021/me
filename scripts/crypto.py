#!/usr/bin/env python3
"""
Profile 加密核心模块
提供密钥管理、AES-256-GCM 加解密、文件收集等基础功能。
"""

import secrets
import sys
from pathlib import Path

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError:
    print("错误：需要 cryptography 库。请运行：pip install cryptography")
    sys.exit(1)

MAGIC = b"PJENC002"
NONCE_LEN = 12
KEY_HEX_LEN = 64  # 32 bytes = 64 hex chars


def get_project_root() -> Path:
    """获取项目根目录（scripts/ 的上级）"""
    return Path(__file__).resolve().parent.parent


def get_key_path() -> Path:
    """获取密钥文件路径"""
    return get_project_root() / "scripts" / ".key"


def gen_key() -> str:
    """生成 256-bit 随机密钥，写入 .key 文件，返回 hex 字符串"""
    key_hex = secrets.token_hex(32)
    key_path = get_key_path()
    key_path.parent.mkdir(parents=True, exist_ok=True)
    key_path.write_text(key_hex, encoding="utf-8")
    return key_hex


def load_key() -> bytes:
    """从 .key 文件读取密钥，返回 bytes"""
    key_path = get_key_path()
    if not key_path.exists():
        print(f"错误：密钥文件不存在：{key_path}")
        print("请先运行：python scripts/encrypt.py --gen-key")
        sys.exit(1)

    key_hex = key_path.read_text(encoding="utf-8").strip()
    if len(key_hex) != KEY_HEX_LEN:
        print(f"错误：密钥格式无效（长度 {len(key_hex)}，期望 {KEY_HEX_LEN}）")
        sys.exit(1)

    try:
        return bytes.fromhex(key_hex)
    except ValueError:
        print("错误：密钥不是有效的 hex 字符串")
        sys.exit(1)


def encrypt(key: bytes, plaintext: bytes) -> bytes:
    """AES-256-GCM 加密。返回 MAGIC + nonce + ciphertext+tag"""
    nonce = secrets.token_bytes(NONCE_LEN)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return MAGIC + nonce + ciphertext


def decrypt(key: bytes, data: bytes) -> bytes:
    """AES-256-GCM 解密。输入为 MAGIC + nonce + ciphertext+tag"""
    min_len = 8 + NONCE_LEN + 16
    if len(data) < min_len:
        raise ValueError("文件过短，不是有效的加密文件")

    magic = data[:8]
    if magic != MAGIC:
        raise ValueError("文件格式无效（magic 不匹配，可能使用了旧版口令加密）")

    nonce = data[8 : 8 + NONCE_LEN]
    ciphertext = data[8 + NONCE_LEN :]

    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)


def collect_plaintext(profile_dir: Path) -> list[Path]:
    """收集 profile 下需要加密的明文文件"""
    files = []
    for ext in ("*.md", "*.json"):
        files.extend(profile_dir.glob(ext))
    modules_dir = profile_dir / "modules"
    if modules_dir.is_dir():
        files.extend(modules_dir.glob("*.md"))
    return sorted(files)


def collect_enc(profile_dir: Path) -> list[Path]:
    """收集 profile 下所有 .enc 文件"""
    files = []
    files.extend(profile_dir.glob("*.enc"))
    modules_dir = profile_dir / "modules"
    if modules_dir.is_dir():
        files.extend(modules_dir.glob("*.enc"))
    return sorted(files)
