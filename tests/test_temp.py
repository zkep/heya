from __future__ import annotations

import os

from heya.shared.temp import OutputFileManager, TempFileManager, create_output_path


class TestTempFileManager:
    def test_create_temp_dir(self) -> None:
        manager = TempFileManager()
        temp_dir = manager.create_temp_dir()
        assert os.path.isdir(temp_dir)
        assert manager.temp_dir == temp_dir
        manager.cleanup()
        assert not os.path.exists(temp_dir)

    def test_create_temp_file(self) -> None:
        manager = TempFileManager()
        temp_file = manager.create_temp_file("test content", "test.html")
        assert os.path.isfile(temp_file)
        assert temp_file.endswith("test.html")
        with open(temp_file) as f:
            assert f.read() == "test content"
        manager.cleanup()
        assert not os.path.exists(temp_file)

    def test_cleanup(self) -> None:
        manager = TempFileManager()
        manager.create_temp_file("test", "test.txt")
        assert manager.temp_dir is not None
        manager.cleanup()
        assert manager.temp_dir is None


class TestOutputFileManager:
    def test_create_output_path(self) -> None:
        manager = OutputFileManager()
        path = manager.create_output_path()
        assert path.endswith(".pdf")
        assert "heya_" in path

    def test_custom_extension(self) -> None:
        manager = OutputFileManager()
        path = manager.create_output_path(extension="html")
        assert path.endswith(".html")

    def test_custom_prefix(self) -> None:
        manager = OutputFileManager()
        path = manager.create_output_path(prefix="custom")
        assert "custom_" in path


def test_create_output_path_function() -> None:
    path = create_output_path()
    assert path.endswith(".pdf")
    assert "heya_" in path
