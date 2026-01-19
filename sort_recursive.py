import argparse
import logging
from pathlib import Path
import shutil



parser = argparse.ArgumentParser(description="Sorting folder")
parser.add_argument("--source", "-s", help="Source folder", required=True)
parser.add_argument("--output", "-o", help="Output folder", default="dist")

args = vars(parser.parse_args())
source = Path(args.get("source"))
output = Path(args.get("output"))


def grabs_folder(path: Path) -> list[Path]:
    folders = []
    try:
        for el in path.iterdir():
            if el.is_dir():
                folders.append(el)
                folders.extend(grabs_folder(el))
    except PermissionError:
        logging.warning("No access (skip dir): %s", path)
    except OSError as err:
        logging.error("Scan failed: %s | %s", path, err)
    return folders



def copy_file(path: Path, output: Path) -> None:
    try:
        for el in path.iterdir():
            if el.is_file():
                ext = el.suffix.lower().lstrip(".")
                if not ext:
                    ext = "no_extension"

                ext_folder = output / ext
                ext_folder.mkdir(exist_ok=True, parents=True)

                shutil.copy2(el, ext_folder / el.name)

    except PermissionError:
        logging.warning("No access (skip dir): %s", path)
    except OSError as err:
        logging.error("Error in %s: %s", path, err)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if not source.exists() or not source.is_dir():
        logging.error("Source folder not found or not a directory: %s", source)
        raise SystemExit(1)

    output.mkdir(parents=True, exist_ok=True)

    logging.info("SRC : %s", source)
    logging.info("DIST: %s", output.resolve())

    folders = [source, *grabs_folder(source)]
    logging.info("Folders found: %d", len(folders))

    for folder in folders:
        copy_file(folder, output)

    logging.info("Sorting complete!")
