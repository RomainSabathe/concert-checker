"""Docker/Podman build and run helper script for concert-checker."""

import os
import subprocess
import sys
from pathlib import Path

DOCKER_EXECUTABLE = "podman"
IMAGE_NAME = "concert-checker"
DOCKERFILE = "Dockerfile"


def build_image() -> bool:
    """Build the Docker/Podman image.

    Returns:
        bool: True if build succeeded, False otherwise.
    """
    print(f"Building {IMAGE_NAME} image...")
    result = subprocess.run(
        [DOCKER_EXECUTABLE, "build", "-t", IMAGE_NAME, "-f", DOCKERFILE, "."],
        check=False,
    )

    if result.returncode != 0:
        print(
            f"Error: Build failed with exit code {result.returncode}", file=sys.stderr
        )
        return False

    print("Build succeeded!")
    return True


def run_container() -> int:
    """Run the Docker/Podman container with an interactive shell.

    Returns:
        int: Exit code from the container.
    """
    print(f"Running {IMAGE_NAME} container with interactive shell...")

    # Get current working directory
    cwd = Path.cwd()

    # Get OpenAI API key from environment
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai_key:
        print("Warning: OPENAI_API_KEY not set in environment", file=sys.stderr)

    # Use os.execvp to replace current process with the container shell
    # This gives you a proper interactive shell experience
    os.execvp(
        DOCKER_EXECUTABLE,
        [
            DOCKER_EXECUTABLE,
            "run",
            "--rm",
            "-it",  # Changed to -it for interactive + TTY
            "-v",
            f"{cwd}:/code:z",
            "-v",
            "$HOME/.logfire:/root/.logfire:z",
            "-e",
            f"OPENAI_API_KEY={openai_key}",
            IMAGE_NAME,
            "/bin/bash",
        ],
    )


def main() -> int:
    """Main entry point.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """
    # Build the image
    if not build_image():
        return 1

    # Run the container (this will replace the current process)
    # execvp doesn't return, so the code below will never execute
    run_container()

    # This line will never be reached
    return 0


if __name__ == "__main__":
    sys.exit(main())
