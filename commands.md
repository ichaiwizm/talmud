# Commandes CLI - Torah Names Extraction

## Setup

```bash
# IMPORTANT: Toujours activer l'environnement d'abord !
source .venv/bin/activate

# Initialiser la base de donnees
python -m src.cli.main init-db
```

> **Note:** Toutes les commandes ci-dessous supposent que l'environnement est activé.
> Si `python` n'est pas trouvé, lancez d'abord `source .venv/bin/activate`

## Import Torah (Sefaria)

```bash
# Importer tous les 5 livres (~5800 versets)
python -m src.cli.main import-torah

# Importer un seul livre
python -m src.cli.main import-torah --book Genesis

# Verifier le statut d'import
python -m src.cli.main import-status
```

## Extraction des noms

### Mode Bulk (recommande)

```bash
# Extraction bulk sequentielle (50 versets/requete, Sonnet)
python -m src.cli.main extract-names --bulk

# Avec limite
python -m src.cli.main extract-names --bulk --limit 100

# Changer la taille des batches
python -m src.cli.main extract-names --bulk --batch-size 100

# Mode parallele (jusqu'a 10 workers)
python -m src.cli.main extract-names --bulk --parallel --workers 5

# Combinaison complete
python -m src.cli.main extract-names --bulk --batch-size 50 --parallel --workers 10 --limit 500
```

### Options

| Option | Court | Description |
|--------|-------|-------------|
| `--bulk` | `-b` | Mode bulk (plusieurs versets par requete) |
| `--batch-size` | `-s` | Versets par requete (defaut: 50) |
| `--parallel` | `-p` | Activer la parallelisation |
| `--workers` | `-w` | Nombre de workers (max 10 pour bulk) |
| `--limit` | `-l` | Limite de versets a traiter |
| `--model` | `-m` | Modele Claude (defaut: sonnet) |

## Statut et monitoring

```bash
# Voir le statut d'extraction
python -m src.cli.main extraction-status

# Exemple de sortie:
# Total verses: 5846
# Processed: 110 (1.88%)
# Pending: 5736
# With errors: 0
# Unique names: 25
# Total occurrences: 139
```

## Reset et maintenance

```bash
# Reset complet (supprime tous les noms et occurrences)
python -m src.cli.main reset-extraction --confirm

# Relancer les versets en erreur
python -m src.cli.main retry-errors
python -m src.cli.main retry-errors --limit 50
```

## Estimations de temps

| Mode | Versets/sec | 5800 versets |
|------|-------------|--------------|
| Bulk sequentiel (50/req) | ~1.8/sec | ~55 min |
| Bulk parallele 5 workers | ~9/sec | ~11 min |
| Bulk parallele 10 workers | ~18/sec | ~5 min |

## Configuration

Fichier: `src/config/settings.py`

```python
claude_model: str = "sonnet"    # Modele Claude
claude_timeout: int = 300       # Timeout en secondes
bulk_size: int = 50             # Versets par requete bulk
```

Variables d'environnement (`.env`):
```
CLAUDE_MODEL=sonnet
CLAUDE_TIMEOUT=300
BULK_SIZE=50
```
