"""Tests for prosaic.utils module."""

from prosaic import utils


class TestReadText:
    """Tests for read_text()."""

    def test_reads_utf8(self, tmp_path):
        """Reads UTF-8 encoded files correctly."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello world", encoding="utf-8")
        result = utils.read_text(test_file)
        assert result == "Hello world"

    def test_reads_unicode_characters(self, tmp_path):
        """Reads Unicode characters including emojis and accents."""
        test_file = tmp_path / "unicode.txt"
        content = "Hello 🎉 café résumé 日本語 中文"
        test_file.write_text(content, encoding="utf-8")
        result = utils.read_text(test_file)
        assert result == content

    def test_reads_multiline_unicode(self, tmp_path):
        """Reads multi-line files with Unicode."""
        test_file = tmp_path / "multiline.md"
        content = "# Título\n\n¡Hola mundo! 🌍\n\n## Sección"
        test_file.write_text(content, encoding="utf-8")
        result = utils.read_text(test_file)
        assert result == content


class TestWriteText:
    """Tests for write_text()."""

    def test_writes_utf8(self, tmp_path):
        """Writes files with UTF-8 encoding."""
        test_file = tmp_path / "test.txt"
        utils.write_text(test_file, "Hello world")
        result = test_file.read_text(encoding="utf-8")
        assert result == "Hello world"

    def test_writes_unicode_characters(self, tmp_path):
        """Writes Unicode characters including emojis and accents."""
        test_file = tmp_path / "unicode.txt"
        content = "Hello 🎉 café résumé 日本語 中文"
        utils.write_text(test_file, content)
        result = test_file.read_text(encoding="utf-8")
        assert result == content

    def test_writes_special_markdown(self, tmp_path):
        """Writes markdown with special characters."""
        test_file = tmp_path / "special.md"
        content = "# Title™\n\n© 2026 – Author • €100\n\n→ bullet"
        utils.write_text(test_file, content)
        result = test_file.read_text(encoding="utf-8")
        assert result == content

    def test_roundtrip_preserves_content(self, tmp_path):
        """Write then read preserves exact content."""
        test_file = tmp_path / "roundtrip.md"
        content = "# Prosaic 📝\n\nWriting with émojis 🎨 and spëcial çharacters"
        utils.write_text(test_file, content)
        result = utils.read_text(test_file)
        assert result == content
