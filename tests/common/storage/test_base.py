from common.storage import base


class TestLocalStorage:
    def test_local_storage(self, tmp_path):
        test_file_name = "test_file"
        test_contents = "test contents"

        # Store a file locally
        base.LocalStorage().store_file(tmp_path, test_file_name, test_contents)

        # Read the file back
        assert (tmp_path / test_file_name).read_text() == test_contents
