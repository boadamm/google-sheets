"""File watcher module using watchdog library.

This module provides a Watcher class that monitors file system changes
for specified file patterns and triggers callbacks when files are created
or modified.
"""

import time
from pathlib import Path
from typing import Callable, Optional
import tomli
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, FileSystemEvent


class DebouncedPatternMatchingEventHandler(PatternMatchingEventHandler):
    """Event handler with debouncing to prevent duplicate events."""

    def __init__(
        self,
        callback: Callable[[Path], None],
        patterns: list[str],
        debounce_interval: float = 1.0,
        **kwargs
    ):
        """Initialize the debounced event handler.

        Args:
            callback: Function to call when a file event occurs
            patterns: List of file patterns to match
            debounce_interval: Time in seconds to debounce events
            **kwargs: Additional arguments for PatternMatchingEventHandler
        """
        super().__init__(patterns=patterns, **kwargs)
        self.callback = callback
        self.debounce_interval = debounce_interval
        self._last_events: dict[str, float] = {}

    def _should_process_event(self, event_path: str) -> bool:
        """Check if the event should be processed based on debouncing.

        Args:
            event_path: Path of the file that triggered the event

        Returns:
            True if the event should be processed, False otherwise
        """
        current_time = time.time()
        last_event_time = self._last_events.get(event_path, 0)

        if current_time - last_event_time > self.debounce_interval:
            self._last_events[event_path] = current_time
            return True
        return False

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events.

        Args:
            event: The file system event
        """
        if not event.is_directory and self._should_process_event(event.src_path):
            self.callback(Path(event.src_path).resolve())

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events.

        Args:
            event: The file system event
        """
        if not event.is_directory and self._should_process_event(event.src_path):
            self.callback(Path(event.src_path).resolve())


class Watcher:
    """File system watcher for monitoring file changes.

    Uses the watchdog library to monitor a specified folder for file changes
    matching given patterns and triggers callbacks when events occur.
    """

    def __init__(
        self,
        folder: Optional[Path] = None,
        patterns: Optional[list[str]] = None,
        poll_interval: int = 5,
    ):
        """Initialize the Watcher.

        Args:
            folder: Directory to monitor. If None, reads from config/settings.toml
            patterns: List of file patterns to match. If None, reads from config
            poll_interval: Polling interval in seconds. Defaults to config or 5
        """
        # Load defaults from config if parameters not provided
        if folder is None or patterns is None or poll_interval == 5:
            config = self._load_config()
            watcher_config = config.get("watcher", {})

            if folder is None:
                folder = Path(watcher_config.get("folder", "./watch"))
            if patterns is None:
                patterns = watcher_config.get("patterns", ["*.csv", "*.xlsx"])
            if poll_interval == 5:  # Using default value
                poll_interval = watcher_config.get("poll_interval", 5)

        self.folder = folder if isinstance(folder, Path) else Path(folder)
        self.patterns = patterns
        self.poll_interval = poll_interval

        # Internal state
        self._observer: Optional[Observer] = None
        self._event_handler: Optional[DebouncedPatternMatchingEventHandler] = None
        self._is_running = False

    def _load_config(self) -> dict:
        """Load configuration from settings.toml file.

        Returns:
            Dictionary containing configuration data
        """
        config_path = Path("config/settings.toml")
        try:
            with open(config_path, "rb") as f:
                return tomli.load(f)
        except (FileNotFoundError, tomli.TOMLDecodeError):
            return {}

    def start(self, callback: Callable[[Path], None]) -> None:
        """Start the file watcher in a non-blocking manner.

        Args:
            callback: Function to call when a matching file is created/modified

        Raises:
            RuntimeError: If the watcher is already running
        """
        if self._is_running:
            raise RuntimeError("Watcher is already running")

        # Create the directory if it doesn't exist
        self.folder.mkdir(parents=True, exist_ok=True)

        # Create event handler
        self._event_handler = DebouncedPatternMatchingEventHandler(
            callback=callback,
            patterns=self.patterns,
            ignore_directories=True,
            case_sensitive=False,
        )

        # Create and start observer
        self._observer = Observer()
        self._observer.schedule(self._event_handler, str(self.folder), recursive=False)
        self._observer.start()
        self._is_running = True

    def stop(self) -> None:
        """Stop the file watcher and clean up resources.

        This method safely stops the observer thread and waits for it to finish.
        """
        if self._is_running and self._observer is not None:
            self._observer.stop()
            self._observer.join()
            self._is_running = False
        elif not self._is_running:
            # Allow calling stop() on a non-running watcher without error
            pass
