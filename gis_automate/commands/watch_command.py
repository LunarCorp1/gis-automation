import time
from pathlib import Path


def run_watch(
    directory: str,
    interval: int = 30,
    fmt: str = "pdf",
    recursive: bool = False,
):
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class ShpHandler(FileSystemEventHandler):
        def __init__(self):
            self._debounce: dict[str, float] = {}

        def on_created(self, event):
            if event.src_path.endswith(".shp"):
                self._process(event.src_path)

        def on_modified(self, event):
            if event.src_path.endswith(".shp"):
                self._process(event.src_path)

        def _process(self, path: str):
            now = time.time()
            if path in self._debounce and now - self._debounce[path] < 5:
                return
            self._debounce[path] = now
            from .batch_command import run_batch
            print(f"New shapefile detected: {path}")
            try:
                run_batch(str(Path(path).parent), fmt, recursive=recursive)
            except Exception as e:
                print(f"  ERROR: {e}")

    observer = Observer()
    handler = ShpHandler()
    observer.schedule(handler, directory, recursive=recursive)
    observer.start()
    print(f"Watching {directory} for shapefiles (every {interval}s)...")
    try:
        while True:
            time.sleep(interval)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
