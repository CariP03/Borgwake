import logging
from datetime import datetime, date
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from threading import Thread

# create logger object
logger = logging.getLogger("backup")
logger.setLevel(logging.DEBUG)

BASE_DIR = Path(__file__).resolve().parent  # /app/src
log_dir = BASE_DIR.parent / "logs"  # /app/logs
LOG_FILE = log_dir / "backup.log"
log_dir.mkdir(parents=True, exist_ok=True)

# configure file handler
fh = TimedRotatingFileHandler(LOG_FILE, when='D', backupCount=7)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(levelname)-8s %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

# force rotation for container
if LOG_FILE.exists():
    # last edit date
    edit_time = datetime.fromtimestamp(LOG_FILE.stat().st_mtime).date()
    today = date.today()
    if edit_time < today:
        fh.doRollover()

# configure console logger
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)
logger.addHandler(sh)


def __stream_reader(pipe, log_fn, prefix, repo_name):
    with pipe:
        for line in pipe:
            log_fn(f"[{repo_name} {prefix}] {line.rstrip()}")


def log_subprocess(proc, repo_name):
    t_out = Thread(
        target=__stream_reader,
        args=(proc.stdout, logger.info, "STDOUT", repo_name),
        daemon=True
    )
    t_err = Thread(
        target=__stream_reader,
        args=(proc.stderr, logger.warning, "STDERR", repo_name),
        daemon=True
    )
    t_out.start()
    t_err.start()

    # wait for process end
    return_code = proc.wait()

    # consume buffer
    t_out.join()
    t_err.join()

    return return_code
