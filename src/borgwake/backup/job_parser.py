"""Parses raw repository configuration data into BackupJob instances."""

import os
from pathlib import Path

from borgwake.backup.abstractions import BackupJob
from borgwake.errors import ConfigurationError
from borgwake.yaml_reader import load_yaml

_REQUIRED_KEYS = ("repo_name", "script_name", "repo_passphrase")


def load_backup_jobs() -> list[dict] | None:
    """Load the backup jobs from the repository.

    Returns None if BACKUP_JOBS_YAML_PATH is not set.
    """

    raw_jobs_yaml_path = os.getenv("BACKUP_JOBS_YAML_PATH")

    if raw_jobs_yaml_path is None:
        return None

    return load_yaml(Path(raw_jobs_yaml_path))


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
