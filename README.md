# DAP1 Autotasks

Dieses Script lädt automatisch die DAP1-Praktikumsaufgaben vom Moodle der TU Dortmund herunter, speichert sie lokal als `.md` (Aufgabenbeschreibung) und `.cpp` (Coderahmen) und pusht sie direkt in ein GitHub-Repository. Um die Aufgaben anschließend zu bearbeiten, genügt ein einfacher `git pull`.

## Features

- Moodle-Login über SSO
- Extrahiert Aufgabenbeschreibung und C++-Code
- Speichert Dateien in `Wochennummer/Aufgabennummer`
- Git: `pull` vor der Verarbeitung, `add` → `commit` → `push` pro Aufgabe

## Installation

### Nix
```
git clone https://github.com/leander-ow/dap1-autotasks.git
cd dap1-autotasks
nix-shell
```

### pip
```
git clone https://github.com/leander-ow/dap1-autotasks.git
cd dap1-autotasks
python3 -m venv venv
source venv/bin/activate  # Windows (cringe): venv\Scripts\activate
pip install -r requirements.txt
```

## Setup

```
git clone <dein_dap1_repository>
```

Kopiere `.env.example` zu `.env` und passe die Werte an:

```env
SSO_USER=<dein_username>
SSO_PASS=<dein_passwort>
COURSE_ID=<kurs_id>
REPO=<dein_repository_name>
BASE=<Pfad_zum_Aufgabenordner_in_deinem_repository>
```

## Nutzung

```
python main.py
```
Am besten automatisch am Samstagmorgen ausführen.

## Struktur im DAP1 Repository

```
BASE/
└── 01/
    ├── 1.cpp
    ├── 1.md
    ├── 2.cpp
    └── 2.md
```
