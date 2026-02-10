# Syncer

A lightweight incremental file syncer for directories. Copies only changed files from source to target - a simplified, reliable alternative to rsync.

## Features

- **Incremental sync** - skips unchanged files, copies only what's new or modified
- **Two comparison modes** - fast metadata check (size + mtime) or content hash (MD5/SHA1)
- **Dry-run mode** - preview all planned actions without touching the filesystem
- **Safe by default** - no deletes unless explicitly enabled with `--delete --confirm`
- **Exclusion patterns** - skip files/directories matching given patterns
- **Logging** - all actions logged to stderr and `logs/logfile.log`

## Installation

Requires Python >= 3.11.

```bash
.\venvsyncer\Scripts\activate # Windows
source venvsyncer/bin/activate # Linux/Mac
pip install -e .
```

## Usage

```bash
syncer <source-dir> <target-dir> [options]
```

### Options

| Flag | Description |
|---|---|
| `-d`, `--dry-run` | List planned actions without modifying files |
| `-c`, `--confirm` | Confirm replacing existing files |
| `-x`, `--delete` | Delete extra files in target (requires `--confirm`) |
| `--hash` | Use hash comparison instead of metadata |
| `--exclude PATTERNS` | Pipe-separated exclude patterns |

### Examples

Preview what would be synced:

```bash
syncer "C:\source" "C:\target" -d
```

Sync with deletions and exclusions:

```bash
syncer "C:\source" "C:\target" -x -c --exclude ".git|__pycache__|logs"
```

## Project Structure

```
syncer/
├── syncer/
│   ├── main.py          # CLI entry point
│   ├── scanner.py       # Directory scanning & comparison
│   ├── handler.py       # File operation handlers
│   └── tests/           # Unit & integration tests
├── pyproject.toml
├── LICENSE
└── README.md
```

## Running Tests

```bash
pytest
```

## Roadmap

- [ ] Parallel copying with `concurrent.futures` (`--workers`)

## License

[MIT](LICENSE) - Denislav Dimitrov
