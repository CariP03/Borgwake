"""Parses raw repository configuration data into BackupJob instances."""

import os
from dataclasses import dataclass
from pathlib import Path

from borgwake.backup.abstractions import BackupJob
from borgwake.errors import ConfigurationError
from borgwake.paths import validate_path_is_a_directory, validate_path_is_a_file
from borgwake.yaml_reader import load_yaml

_REQUIRED_KEYS = ("repo_name", "script_name", "repo_passphrase")


@dataclass
class BackupJobsLoadingSettings:
    jobs_file: Path
    scripts_dir: Path


def load_backup_jobs_loading_settings() -> BackupJobsLoadingSettings | None:
    """Loads backup jobs loading settings from the environment.

    Returns None if any of the settings is not set.
    """

    raw_jobs_file = os.getenv("BACKUP_JOBS_FILE")
    raw_scripts_dir = os.getenv("BACKUP_SCRIPTS_DIR")

    if raw_jobs_file is None or raw_scripts_dir is None:
        return None

    jobs_file = validate_path_is_a_file(Path(raw_jobs_file))
    scripts_dir = validate_path_is_a_directory(Path(raw_scripts_dir))

    return BackupJobsLoadingSettings(jobs_file, scripts_dir)


def load_backup_jobs(yaml_path: Path) -> list[dict] | None:
    """Load the backup jobs from the repository."""

    return load_yaml(yaml_path)


def parse_backup_jobs(repos_data: list[dict], scripts_dir: Path) -> list[BackupJob]:
    """Parse raw repository config entries into a list of BackupJob instances.

    Raises:
        ConfigurationError: if a missing required key is present in the entry
    """

    jobs = []
    for entry in repos_data:
        for key in _REQUIRED_KEYS:
            if key not in entry:
                raise ConfigurationError(
                    f"Missing required key {key!r} in entry: {entry}"
                )

        jobs.append(
            BackupJob(
                repo_name=entry["repo_name"],
                repo_passphrase=entry["repo_passphrase"],
                script_path=scripts_dir / entry["script_name"],
            )
        )

    return jobs
