# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path


APP_DIR_NAME = "SiloApp"


def get_user_documents_dir() -> Path:
    return Path.home() / "Documents"


def get_app_base_dir() -> Path:
    base = get_user_documents_dir() / APP_DIR_NAME
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_data_dir() -> Path:
    path = get_app_base_dir() / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_exports_dir() -> Path:
    path = get_app_base_dir() / "exports"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_temp_dir() -> Path:
    path = get_app_base_dir() / "temp"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_logs_dir() -> Path:
    path = get_app_base_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_db_path() -> Path:
    return get_data_dir() / "silo_app.db"