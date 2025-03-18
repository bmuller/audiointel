import importlib.resources


def get_datafile_path(fname):
    with importlib.resources.path("audiointel.data", fname) as fspath:
        return str(fspath)
