# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SiloApp** is a Python/Streamlit web application for agricultural silo dimensioning. It helps farmers and engineers calculate optimal silo geometry for silage storage based on herd characteristics, diet composition, and operational parameters. The UI and domain logic are written entirely in Portuguese (Brazilian).

## Running the Application

```bash
# Recommended: uses run_app.py launcher (handles port 8501, opens browser automatically)
python run_app.py

# Direct Streamlit invocation
python -m streamlit run app/main.py
```

## Installing Dependencies

```bash
pip install -r requirements.txt
```

## Architecture

The codebase has two layers: root-level calculation modules and the `app/` package.

### Root-level Modules (pure calculation, no UI dependencies)

| File | Responsibility |
|---|---|
| `calculos.py` | Animal consumption, dry matter, total volume calculations. Classes: `Rebanho`, `Dieta`, `Forragem`, `Operacao` |
| `geometrias.py` | Cross-section area formulas for rectangular, trapezoidal, and oval silos |
| `otimizacao.py` | Optimization algorithms that generate ranked silo solutions via penalty function. Returns `SolucaoSilo` dataclasses |
| `visualizacao.py` | Plotly 3D mesh generation for silo rendering |
| `relatorio.py` | PDF report generation via ReportLab |

### `app/` Package

```
app/
├── config.py              # Path management (data, exports, temp, logs under ~/Documents/SiloApp/)
├── main.py                # Entry point, delegates to streamlit_app.py
├── ui/                    # Streamlit pages
│   ├── streamlit_app.py   # Navigation shell
│   ├── dimensionamento_page.py  # Core dimensioning form and results display
│   ├── projetos_page.py   # Project CRUD
│   ├── historico_page.py  # Simulation history
│   └── home_page.py / sobre_page.py
├── domain/
│   ├── models.py          # Dataclasses: Projeto, EntradaDimensionamento, SolucaoSilo, ResultadoDimensionamento
│   └── validacoes.py      # Input validation
├── services/
│   ├── dimensionamento_service.py  # Orchestrates calculos → otimizacao → alertas
│   ├── projeto_service.py          # Project/simulation CRUD logic
│   └── relatorio_service.py        # PDF generation wrapper
├── storage/
│   ├── sqlite_db.py           # DB init and connection (SQLite)
│   └── project_repository.py  # Repository pattern over SQLite
└── assets/                    # styles.css, logos, icons
```

### Data Flow

```
User form input (dimensionamento_page.py)
  → EntradaDimensionamento (dataclass)
  → dimensionamento_service.py
      ├─ calculos.py       (volume requirements)
      ├─ otimizacao.py     (geometry optimization)
      │    └─ geometrias.py
      └─ alertas generation
  → ResultadoDimensionamento
      ├─ UI (metrics + table)
      ├─ visualizacao.py   (Plotly 3D)
      └─ relatorio_service.py (PDF)
  → SQLite (~/Documents/SiloApp/data/silo_app.db)
```

### Database Schema

- **projects**: `id, nome, responsavel_tecnico, propriedade, observacoes, created_at, updated_at`
- **simulations**: `id, project_id (FK), nome_simulacao, dados_entrada_json, resultados_json, alertas_json, created_at`

## Supported Silo Types

- **Sections**: rectangular, trapezoidal, oval
- **Types**: surface (above-ground) and trench silos
- **Optimization**: penalty function ranks solutions by volume excess, operational length, height (≤3.5 m preferred), and tractor passes per width

## Key Paths at Runtime

- Data/DB: `~/Documents/SiloApp/data/silo_app.db`
- Exports (PDFs): `~/Documents/SiloApp/exports/`
- Temp files: `~/Documents/SiloApp/temp/`
