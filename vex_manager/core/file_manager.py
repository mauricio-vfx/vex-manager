from pathlib import Path
import logging
import glob
import os

import vex_manager.utils as utils


logger = logging.getLogger(f"vex_manager.{__name__}")

FILE_EXTENSION = ".vfl"


def create_new_vex_file(parent_path: str, name: str = "") -> str:
    vex_file_path = os.path.join(parent_path, f"{name}{FILE_EXTENSION}")

    if os.path.exists(vex_file_path):
        logger.warning(f"{name} already exists.")
        return vex_file_path

    open(vex_file_path, "w").close()

    logger.debug(f"{vex_file_path!r} created.")

    return vex_file_path


def rename_vex_file(file_path: str, new_name: str) -> str:
    if not new_name.endswith(FILE_EXTENSION):
        new_name = f"{new_name}{FILE_EXTENSION}"

    if not utils.is_valid_file_name(new_name):
        new_file_path = file_path

        logger.error(f"{new_name!r} is not a valid file name.")
    elif not os.path.exists(file_path):
        new_file_path = file_path

        logger.error(f"{file_path!r} does not exit.")
    elif not os.path.isfile(file_path):
        new_file_path = file_path

        logger.error(f"{file_path!r} is a directory.")
    else:
        library_path = os.path.dirname(file_path)

        for file in glob.glob(os.path.join(library_path, "*")):
            if new_name == Path(file).stem:
                logger.error(f"{file_path!r} already exists.")

        new_file_path = os.path.join(library_path, new_name)

        if os.path.normpath(new_file_path) == os.path.normpath(file_path):
            new_file_path = file_path

            logger.debug(f"{new_file_path!r} is the same name.")
        elif os.path.exists(new_file_path):
            new_file_path = file_path

            logger.error(f"{new_file_path!r} already exists.")
        else:
            os.rename(file_path, new_file_path)

            logger.debug(f"Renamed file {file_path!r} -> {new_file_path!r}")

    return new_file_path
