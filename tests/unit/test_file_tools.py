from utils.file_tools import create_text_file, remove_text_file


def test_create_text_file(tmp_path):
    target_path = tmp_path / 'data.txt'
    result = create_text_file(str(target_path))
    assert target_path.exists()
    assert target_path.read_text(encoding="utf-8") == \
        "username=SDET\npassword=secret_key"
    assert result == str(target_path)


def test_remove_existing_text_file(tmp_path):
    target_path = tmp_path / 'data.txt'
    target_path.write_text('anything you want')

    remove_text_file(str(target_path))
    assert not target_path.exists()


def test_remove_missing_file(tmp_path):
    target_path = tmp_path / 'data.txt'
    remove_text_file(str(target_path))
    assert not target_path.exists()
