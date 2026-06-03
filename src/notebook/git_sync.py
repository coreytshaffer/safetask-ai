import subprocess
from pathlib import Path
from logger import logger

class GitSync:
    """Handles Git versioning for the Markdown field notes."""

    def __init__(self, notes_dir: str = "data/notes"):
        self.notes_dir = Path(notes_dir)
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        self._init_repo()

    def _run_git(self, args: list) -> subprocess.CompletedProcess:
        """Run a git command in the notes directory."""
        return subprocess.run(
            ["git"] + args,
            cwd=str(self.notes_dir),
            capture_output=True,
            text=True,
            check=False
        )

    def _init_repo(self):
        """Initializes the Git repository if it doesn't exist."""
        git_dir = self.notes_dir / ".git"
        if not git_dir.exists():
            logger.info("Initializing Git repository for field notes...")
            res = self._run_git(["init"])
            if res.returncode == 0:
                # Set up initial dummy config if needed (useful for local bot commits)
                self._run_git(["config", "user.name", "FieldAware Bot"])
                self._run_git(["config", "user.email", "bot@fieldaware.local"])
            else:
                logger.error(f"Failed to initialize git repo: {res.stderr}")

    def commit_note(self, filepath: Path, message: str = "Update field note"):
        """Adds and commits a specific note file."""
        # Add file
        res = self._run_git(["add", filepath.name])
        if res.returncode != 0:
            logger.error(f"Failed to git add {filepath.name}: {res.stderr}")
            return
            
        # Commit
        res = self._run_git(["commit", "-m", message])
        if res.returncode == 0:
            logger.info(f"Committed {filepath.name} to Git repository.")
        else:
            # Usually fails if there are no changes, which is fine
            if "nothing to commit" not in res.stdout:
                logger.error(f"Failed to git commit {filepath.name}: {res.stderr}")

    def sync(self, remote: str = "origin", branch: str = "main") -> bool:
        """Pulls and pushes to the remote repository. Useful for P2P sync."""
        logger.info(f"Syncing with remote {remote}/{branch}...")
        
        # Pull changes
        pull_res = self._run_git(["pull", "--rebase", remote, branch])
        if pull_res.returncode != 0:
            logger.error(f"Git pull failed: {pull_res.stderr}")
            return False
            
        # Push changes
        push_res = self._run_git(["push", remote, branch])
        if push_res.returncode != 0:
            logger.error(f"Git push failed: {push_res.stderr}")
            return False
            
        logger.info("Git sync complete.")
        return True
