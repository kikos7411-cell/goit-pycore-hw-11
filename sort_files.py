import sys
import shutil
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import threading
import logging



copy_executor = ThreadPoolExecutor(max_workers=12)


def copy_file(file_path: Path, dist_dir: Path):

    ext = file_path.suffix.lower().lstrip(".")
    if not ext:
        ext = "no_extension"

    target_dir = dist_dir / ext
    target_dir.mkdir(parents=True, exist_ok=True)

    target_file = target_dir / file_path.name
    shutil.copy2(file_path, target_file)


def process_directory(src_dir: Path, dist_dir: Path):

    threads = []
    try:
        items = list(src_dir.iterdir())
    except PermissionError:
        return

    except OSError:
        return

    for item in items:
        if item.is_file():
            copy_executor.submit(copy_file, item, dist_dir)

        elif item.is_dir():
            t = threading.Thread(
                target=process_directory,
                args=(item, dist_dir),
                daemon=True
            )
            t.start()
            threads.append(t)

    for t in threads:
        t.join()


def main():
    if len(sys.argv) < 2:
        logging.error("Вкажіть шлях до директорії з файлами")
        sys.exit(1)


    src_path = Path(sys.argv[1])
    dist_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("dist")

    if not src_path.exists() or not src_path.is_dir():
        logging.error("Джерельна директорія не існує")
        sys.exit(1)


    dist_path.mkdir(parents=True, exist_ok=True)

    process_directory(src_path, dist_path)

    copy_executor.shutdown(wait=True)
    logging.info("Сортування завершено!")



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(threadName)s %(message)s")
    main()