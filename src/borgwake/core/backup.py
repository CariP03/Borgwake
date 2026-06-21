import subprocess
import os
from pathlib import Path, PurePosixPath

from ip_finder import get_host_ip
from src.borgwake.utils.logger import logger, log_subprocess


# raised when unable to proceed with backup
class BackupError(Exception):
    pass


# build BORG_REPO dynamically
def __build_repo_env(repo_name):
    host = get_host_ip()
    if host is not None:
        # build environment variable
        username = os.getenv('SSH_USERNAME')
        full_path = PurePosixPath(os.getenv('BORG_REPOS_PATH')) / repo_name
        os.environ['BORG_REPO'] = f"ssh://{username}@{host}{full_path}"

        logger.debug(f"BORG_REPO set to {os.environ['BORG_REPO']}")

    else:
        logger.critical(f"Host not found. Failed to backup repo {repo_name}. Aborting all backups")
        raise BackupError(f"Host not found. Failed to backup repo {repo_name}. Aborting all backups")


def __execute_backup_subprocess(backup_script, repo_name):
    try:
        proc = subprocess.Popen(
            [str(backup_script)],
            env=os.environ,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        return_code = log_subprocess(proc, repo_name)

        if return_code == 0:
            logger.info(f"Backup for repo {repo_name} completed successfully")
            return return_code
        elif return_code == 1:
            logger.warning(f"Backup for repo {repo_name} completed with warnings")
            return return_code
        else:
            logger.critical(f"Backup for repo {repo_name} completed with errors. Aborting all backups")
            raise BackupError(f"Backup for repo {repo_name} completed with errors. Aborting all backups")

    except Exception as e:
        logger.critical(f"Backup for repo {repo_name} completed with errors. Aborting all backups")
        logger.critical(f"Unexpected exception during backup: {e}", exc_info=True)
        raise BackupError(f"Backup for repo {repo_name} completed with errors. Aborting all backups") from e


def __execute_backup(backup_script):
    repo_name = Path(backup_script).stem
    logger.info(f"Executing backup for {repo_name}")

    try:
        __build_repo_env(repo_name)
        return __execute_backup_subprocess(backup_script, repo_name)
    except BackupError as e:
        raise e


# cycle through scripts directory to execute all backups
def cycle_backups():
    base_dir = Path(__file__).resolve().parent  # /app/src
    script_dir = base_dir.parent / "scripts"  # /app/scripts
    if not script_dir.is_dir():
        raise FileNotFoundError("Script directory not found")

    overall_exit = 0
    for sh_file in script_dir.glob("*.sh"):
        logger.debug(f"Retrieved script {sh_file}")
        try:
            code = __execute_backup(sh_file)  # 0, 1 or BackupError
        except BackupError:
            return 2

        # keep the highest error code
        overall_exit = max(overall_exit, code)

    return overall_exit
