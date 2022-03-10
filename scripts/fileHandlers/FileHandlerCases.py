import os


class case_no_file(object):
    """File or directory does not exist."""

    def test(self, handler):
        return not os.path.exists(handler.full_path)

    def act(self, handler):
        raise Exception("'{0}' not found".format(handler.path))


class case_existing_file(object):
    """File exists."""

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        handler.handle_file(handler.full_path)


class case_always_fail(object):
    """Base case if nothing else worked."""

    def test(self, handler):
        return True

    def act(self, handler):
        handler.list_dir(handler.full_path)


class case_directory_index_file(object):
    """Serve index.html page for a directory."""

    @staticmethod
    def index_path(handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
               os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.handle_file(self.index_path(handler))
