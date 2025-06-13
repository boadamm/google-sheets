"""Resources module for GUI icons and visual elements.

This module provides functions to get icons and visual resources for the GUI,
with fallback to emoji-based representations when native icons aren't available.
"""

from PySide6.QtGui import QIcon, QPixmap, QColor


def get_checkmark_icon(size: int = 16) -> str:
    """Get a checkmark icon representation.

    Args:
        size: Icon size in pixels (unused for emoji fallback)

    Returns:
        str: Unicode checkmark emoji
    """
    return "✅"


def get_cross_icon(size: int = 16) -> str:
    """Get a cross/error icon representation.

    Args:
        size: Icon size in pixels (unused for emoji fallback)

    Returns:
        str: Unicode cross mark emoji
    """
    return "❌"


def get_warning_icon(size: int = 16) -> str:
    """Get a warning icon representation.

    Args:
        size: Icon size in pixels (unused for emoji fallback)

    Returns:
        str: Unicode warning emoji
    """
    return "⚠️"


def get_info_icon(size: int = 16) -> str:
    """Get an info icon representation.

    Args:
        size: Icon size in pixels (unused for emoji fallback)

    Returns:
        str: Unicode info emoji
    """
    return "ℹ️"


def get_folder_icon(size: int = 16) -> str:
    """Get a folder icon representation.

    Args:
        size: Icon size in pixels (unused for emoji fallback)

    Returns:
        str: Unicode folder emoji
    """
    return "📁"


def get_file_icon(size: int = 16) -> str:
    """Get a file icon representation.

    Args:
        size: Icon size in pixels (unused for emoji fallback)

    Returns:
        str: Unicode file emoji
    """
    return "📄"


def get_sync_icon(size: int = 16) -> str:
    """Get a sync icon representation.

    Args:
        size: Icon size in pixels (unused for emoji fallback)

    Returns:
        str: Unicode sync emoji
    """
    return "🔄"


def get_watch_icon(size: int = 16) -> str:
    """Get a watch/monitor icon representation.

    Args:
        size: Icon size in pixels (unused for emoji fallback)

    Returns:
        str: Unicode watch emoji
    """
    return "👁️"


def create_simple_qicon(color: str, size: int = 16) -> QIcon:
    """Create a simple colored square QIcon.

    This is a fallback function for creating basic colored icons
    when native icons aren't available.

    Args:
        color: Color name or hex string (e.g., "green", "#00ff00")
        size: Icon size in pixels

    Returns:
        QIcon: Simple colored square icon
    """
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(color))

    return QIcon(pixmap)


def get_status_icon(status: str, size: int = 16) -> str:
    """Get an icon for a given status.

    Args:
        status: Status string ("success", "error", "warning", "info", etc.)
        size: Icon size in pixels (unused for emoji fallback)

    Returns:
        str: Unicode emoji for the status
    """
    status_map = {
        "success": get_checkmark_icon(size),
        "error": get_cross_icon(size),
        "warning": get_warning_icon(size),
        "info": get_info_icon(size),
        "folder": get_folder_icon(size),
        "file": get_file_icon(size),
        "sync": get_sync_icon(size),
        "watch": get_watch_icon(size),
    }

    return status_map.get(status.lower(), "⚪")  # Default to white circle


# Convenience constants for common icons
CHECKMARK = get_checkmark_icon()
CROSS = get_cross_icon()
WARNING = get_warning_icon()
INFO = get_info_icon()
FOLDER = get_folder_icon()
FILE = get_file_icon()
SYNC = get_sync_icon()
WATCH = get_watch_icon()
