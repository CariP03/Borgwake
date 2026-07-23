"""Parses raw repository configuration data into BackupJob instances."""

from pathlib import Path

from borgwake.borg.abstractions import BackupJob
from borgwake.errors import ConfigurationError

_REQUIRED_KEYS = ("repo_name", "script_name", "repo_passphrase")


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
