import tempfile
import shutil
import weakref
from pathlib import Path
from typing import Union


def _unpack_zip(path: Union[Path, str]) -> Path:
    tmpdir = tempfile.mkdtemp()
    shutil.unpack_archive(str(path), tmpdir)
    dir_loc = tmpdir / Path(path).stem

    def finalize() -> None:
        shutil.rmtree(tmpdir)

    # Lazy cleanup
    weakref.finalize(dir_loc, finalize)

    return dir_loc
