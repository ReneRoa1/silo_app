# -*- coding: utf-8 -*-
from __future__ import annotations

import os
from pathlib import Path


APP_DIR_NAME = "SiloApp"


def get_app_base_dir() -> Path:
    """
    Retorna o diretório base do app.
    - Render (nuvem): define a variável de ambiente DATA_DIR apontando para o disco persistente (ex: /data).
    - Sem DATA_DIR no Linux/nuvem: usa /tmp/SiloApp (efêmero, dados perdidos ao reiniciar).
    - Windows local: usa ~/Documents/SiloApp para compatibilidade.
    """
    env_data_dir = os.environ.get("DATA_DIR")
    if env_data_dir:
        base = Path(env_data_dir) / APP_DIR_NAME
    elif os.name == "nt":  # Windows — desenvolvimento local
        base = Path.home() / "Documents" / APP_DIR_NAME
    else:  # Linux/nuvem sem DATA_DIR
        base = Path("/tmp") / APP_DIR_NAME
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
    # Sempre usa /tmp para arquivos temporários — nunca toca o disco persistente
    path = Path("/tmp") / APP_DIR_NAME / "temp"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_logs_dir() -> Path:
    path = get_app_base_dir() / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_db_path() -> Path:
    return get_data_dir() / "silo_app.db"
