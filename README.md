# Syncer

A lightweight OS-independent incremental file syncer for directories. Copies only changed files from source to target - a simplified, reliable alternative to rsync.

## Features

- **Incremental sync** - skips unchanged files, copies only what's new or modified
- **Two comparison modes** - fast metadata check (size + mtime) or content hash (MD5/SHA1)
- **Dry-run mode** - preview all planned actions without touching the filesystem
- **Safe by default** - no deletes unless explicitly enabled with `--delete --confirm`
- **Threading** - supports multi-threaded file operations
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
| `-x`, `--delete` | Delete extra files in target |
| `-w`, `--workers INT` | Use more CPU threads |
| `--hash` | Use hash comparison instead of metadata |
| `--exclude PATTERNS` | Pipe-separated exclude patterns |

### Examples

Preview what would be synced:

```bash
syncer "./source" "./target" -d
```

Sync with deletions, exclusions and threading:

```bash
syncer "./source" "./target" -x -c --exclude ".git|__pycache__|logs" --workers 4
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

- [x] Parallel copying with `concurrent.futures` (`--workers`)

## License

[MIT](LICENSE) - Denislav Dimitrov
