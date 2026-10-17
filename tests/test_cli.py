import pytest

from mp3tools import cli


def test_parser_reads_merge_arguments():
    args = cli.build_parser().parse_args(
        ["merge-mp3", ".", "yes", "foobar.exe", "-1"]
    )

    assert args.command == "merge-mp3"
    assert args.dir == "."
    assert args.subdir_mode is True
    assert args.legacy_foobar_path == "foobar.exe"
    assert args.autowaittime == -1


def test_parser_reads_executable_paths_before_and_after_subcommand():
    args = cli.build_parser().parse_args(
        [
            "--mp3tag-path",
            "mp3tag-before.exe",
            "merge-mp3",
            "--foobar-path",
            "foobar.exe",
        ]
    )

    assert args.foobar_path == "foobar.exe"
    assert args.mp3tag_path == "mp3tag-before.exe"


def test_parser_reads_pack_arguments():
    args = cli.build_parser().parse_args(
        ["pack-subdirs", "4", ".", ".mp3", "no"]
    )

    assert args.group_size == 4
    assert args.dir == "."
    assert args.file_filter == ".mp3"
    assert args.copy_mode is False


def test_parser_rejects_invalid_values():
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(["pack-subdirs", "0"])

    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(["merge-mp3", ".", "sometimes"])


@pytest.mark.parametrize(
    ("command", "expected_help"),
    [
        ("merge-mp3", "omitted: ask"),
        ("pack-subdirs", "default: 15"),
        ("unpack-subdirs", "default: 'subdir-'"),
        ("wait", "use -1 to disable"),
    ],
)
def test_command_help_explains_argument_defaults_and_behavior(
    command, expected_help, capsys
):
    with pytest.raises(SystemExit) as exc_info:
        cli.build_parser().parse_args([command, "--help"])

    assert exc_info.value.code == 0
    help_text = " ".join(capsys.readouterr().out.split())
    assert expected_help in help_text
    assert "path to the foobar2000 executable" in help_text
    assert "path to the Mp3tag executable" in help_text


def test_top_level_help_directs_users_to_command_specific_help():
    help_text = cli.build_parser().format_help()

    assert "mp3tools merge-mp3 --help" in help_text
    assert "mp3tools pack-subdirs --help" in help_text
    assert "mp3tools unpack-subdirs --help" in help_text
    assert "mp3tools wait --help" in help_text
    assert "--foobar-path PATH" in help_text
    assert "--mp3tag-path PATH" in help_text


def test_main_passes_pack_arguments_to_operation(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(cli, "packsubdirs", lambda *args: calls.append(args))

    cli.main(["pack-subdirs", "4", str(tmp_path), ".mp3", "true"])

    assert calls == [(4, str(tmp_path), ".mp3", True)]


def test_main_passes_unpack_directory_to_operation(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(cli, "unpackdirs", lambda *args: calls.append(args))

    cli.main(
        [
            "unpack-subdirs",
            str(tmp_path),
            "subdir-",
            ".mp3",
            "false",
            "false",
        ]
    )

    assert calls == [(str(tmp_path), "subdir-", ".mp3", False, False)]


def test_main_uses_configured_foobar_path(monkeypatch):
    calls = []
    monkeypatch.setattr(cli, "foobarpath", "default-foobar.exe")
    monkeypatch.setattr(cli, "mp3tagpath", "default-mp3tag.exe")
    monkeypatch.setattr(cli, "mergemp3", lambda *args: calls.append(args))

    cli.main(
        [
            "merge-mp3",
            ".",
            "true",
            "--foobar-path",
            "custom-foobar.exe",
            "--mp3tag-path",
            "custom-mp3tag.exe",
        ]
    )

    assert calls == [
        (cli.workingdir, True, "custom-foobar.exe", cli.autowaittime)
    ]
    assert cli.mp3tagpath == "custom-mp3tag.exe"


def test_main_keeps_legacy_wait_syntax(monkeypatch):
    selected = []
    monkeypatch.setattr(cli, "autowaittime", 5)
    monkeypatch.setattr(cli, "selectsubprogram", lambda: selected.append(True))

    cli.main(["wait=12"])

    assert cli.autowaittime == 12
    assert selected == [True]


def test_unpackdirs_uses_requested_working_directory(tmp_path, monkeypatch):
    working_dir = tmp_path / "requested"
    subdir = working_dir / "subdir-1"
    subdir.mkdir(parents=True)
    source = subdir / "track.mp3"
    source.write_bytes(b"audio")
    monkeypatch.chdir(tmp_path)

    cli.unpackdirs(str(working_dir), "subdir-", ".mp3", False, False)

    assert (working_dir / "track.mp3").read_bytes() == b"audio"
    assert not source.exists()
