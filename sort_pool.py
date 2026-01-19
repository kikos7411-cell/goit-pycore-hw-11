import argparse
import logging
from pathlib import Path
import shutil
import os
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor


parser = argparse.ArgumentParser(description="Sorting folder (threads, no recursion)")
parser.add_argument("--source", "-s", help="Source folder", required=True)
parser.add_argument("--output", "-o", help="Output folder", default="dist")

args = vars(parser.parse_args())
source = Path(args.get("source"))
output = Path(args.get("output"))


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


def worker(dir_queue: Queue, output: Path) -> None:

    while True:
        try:
            current_dir: Path = dir_queue.get(timeout=0.3)
        except Empty:
            return

        try:

            copy_file(current_dir, output)


            for el in current_dir.iterdir():
                if el.is_dir():
                    dir_queue.put(el)

        except PermissionError:
            logging.warning("No access (skip dir): %s", current_dir)
        except OSError as err:
            logging.error("Scan failed in %s: %s", current_dir, err)
        finally:
            dir_queue.task_done()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(threadName)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if not source.exists() or not source.is_dir():
        logging.error("Source folder not found or not a directory: %s", source)
        raise SystemExit(1)

    output.mkdir(parents=True, exist_ok=True)

    logging.info("SRC : %s", source)
    logging.info("DIST: %s", output.resolve())


    WORKERS = os.cpu_count() or 4

    dir_queue = Queue()
    dir_queue.put(source)

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = [executor.submit(worker, dir_queue, output) for _ in range(WORKERS)]


        dir_queue.join()


        for f in futures:
            f.result()

    logging.info("Sorting complete!")
