import logging
import shutil
import tempfile
import weakref
from pathlib import Path
from typing import Union, Tuple

import pandas as pd

log = logging.getlogger(__name__)


def _unpack_zip(path: Union[Path, str]) -> Path:
    tmpdir = tempfile.mkdtemp()
    shutil.unpack_archive(str(path), tmpdir)
    dir_loc = tmpdir / Path(path).stem

    def finalize() -> None:
        shutil.rmtree(tmpdir)

    # Lazy cleanup
    weakref.finalize(dir_loc, finalize)

    return dir_loc


def _fk_in_pk(pk: Union[pd.Series, list], fk: Union[pd.Series, list]) -> Tuple[bool, list]:
    if isinstance(fk, list):
        fk = pd.Series(fk)

    missing_flag = ~fk.isin(pk)

    if missing_flag.any():
        log.warning(
            f"Following keys referenced in {fk.name} but missing\
            in primary key table:\n{fk[missing_flag]} "
        )
        return False, fk[missing_flag].tolist()

    return True, []
