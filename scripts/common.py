#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""通用工具函数：配置加载与审计日志。

该模块不依赖任何第三方库，可被本 Skill 下的所有脚本复用。
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def get_skill_root() -> Path:
    """返回当前 Skill 根目录（包含 SKILL.md 的目录）。"""
    return Path(__file__).resolve().parents[1]


def get_logs_dir() -> Path:
    """确保 logs/ 目录存在并返回其路径。"""
    logs_dir = get_skill_root() / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir


def write_audit_log(
    action: str,
    payload: Dict[str, Any],
    status: str = "success",
    message: Optional[str] = None,
) -> Path:
    """将一次操作写入 logs/audit.log（JSON Lines），便于审计与回溯。

    日志格式示例：
    {
        "timestamp": "2026-03-10T12:00:00Z",
        "action": "vecloud.create_instance",
        "status": "success",
        "message": "dry_run only",
        "payload": { ... }
    }
    """
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "action": action,
        "status": status,
        "message": message,
        "payload": payload,
    }
    log_file = get_logs_dir() / "audit.log"
    with log_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return log_file


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """加载统一配置。

    优先级：
    1. 显式传入的 config_path（JSON 文件，结构参考 config_schema.json）
    2. 环境变量（仅用于最小化示例），如 VE_AK / VE_SK / VE_REGION

    TODO：根据实际接入方式扩展（例如从安全配置中心或密钥管理系统拉取）。
    """
    config: Dict[str, Any] = {}

    if config_path:
        path = Path(config_path).expanduser().resolve()
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                try:
                    config = json.load(f)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"配置文件解析失败: {path}") from exc

    credentials = config.get("credentials", {})
    if not credentials:
        # 尝试从环境变量兜底，仅作为示例
        ak = os.getenv("VE_AK")
        sk = os.getenv("VE_SK")
        region = os.getenv("VE_REGION")
        if ak and sk and region:
            credentials = {
                "ve_ak": ak,
                "ve_sk": sk,
                "ve_region": region,
            }
            config["credentials"] = credentials

    return config
