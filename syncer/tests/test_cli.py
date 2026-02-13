import pytest

from syncer.main import create_parser, main
from syncer.scanner import Strategy

def test_parser_defaults():
    parser = create_parser()
    args = parser.parse_args(['tmp/source', 'tmp/target'])

    assert args.source == 'tmp/source'
    assert args.target == 'tmp/target'
    assert args.dry_run is False
    assert args.confirm is False
    assert args.delete is False
    assert args.hash is None
    assert args.exclude == ''
    assert args.workers is None

def test_parser_flags():
    parser = create_parser()
    # Simulate: syncer src tgt --dry-run --delete --workers 4
    args = parser.parse_args(['src', 'tgt', '-d', '-x', '-w', '4'])

    assert args.dry_run is True
    assert args.delete is True
    assert args.workers == 4

def test_parser_hash_strategy():
    parser = create_parser()
    args = parser.parse_args(['src', 'tgt', '--hash'])
    assert args.hash == Strategy.HASH

def test_parser_missings_args(capsys):
    parser = create_parser()

    with pytest.raises(SystemExit):
        parser.parse_args([])

    captured = capsys.readouterr()
    assert 'following arguments are required: source, target' in captured.err

# integration-style test
def test_main_invalid_directory(tmp_path, caplog):
    invalid_path = str(tmp_path / 'non_existent') # Path implicitly imported from pytest
    
    with pytest.raises(SystemExit) as exc:
        main([str(tmp_path), invalid_path])

    assert 'must be a valid directory path' in caplog.text
