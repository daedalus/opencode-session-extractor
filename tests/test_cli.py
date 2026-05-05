"""Tests for cli/commands.py."""

import argparse
from unittest.mock import patch, MagicMock

from openode_session_extractor.cli.commands import list_sessions, main, DB_PATH


class TestListSessions:
    """Tests for list_sessions function."""

    def test_list_sessions(self, temp_db, capsys):
        """Test listing sessions."""
        list_sessions(temp_db, limit=10)
        captured = capsys.readouterr()
        assert "ID" in captured.out
        assert "Title" in captured.out


class TestMain:
    """Tests for main function."""

    def test_main_list(self, temp_db):
        """Test main with --list flag."""
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = argparse.Namespace(
                db=temp_db,
                list=True,
                search=None,
                limit=20,
                session=None,
                all=False,
                output_dir="./exports",
                format="all",
            )
            result = main()
            assert result == 0

    def test_main_no_args_shows_list(self, temp_db):
        """Test main with no args shows list."""
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = argparse.Namespace(
                db=temp_db,
                list=False,
                search=None,
                limit=20,
                session=None,
                all=False,
                output_dir="./exports",
                format="all",
            )
            result = main()
            assert result == 0

    def test_main_nonexistent_db(self):
        """Test main with nonexistent database."""
        with patch("argparse.ArgumentParser.parse_args") as mock_args:
            mock_args.return_value = argparse.Namespace(
                db="/nonexistent/db.db",
                list=True,
                search=None,
                limit=20,
                session=None,
                all=False,
                output_dir="./exports",
                format="all",
            )
            result = main()
            assert result == 1
