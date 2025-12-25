import os
import warnings

class ConsoleLogger:
    """Simple, clean console logger for the IDE"""

    def __init__(self, debug_mode: bool = False):
        self.debug_mode = debug_mode
        self.last_asset = None
        self.repeat_count = 0

    def info(self, message: str):
        """Clean info message"""
        print(f"ℹ️  {message}")

    def debug(self, message: str):
        """Debug message - only shows in debug mode"""
        if self.debug_mode:
            print(f"🔍 {message}")

    def warning(self, message: str):
        """Warning message"""
        print(f"⚠️  {message}")

    def error(self, message: str):
        """Error message"""
        print(f"❌ {message}")

    def asset_selected(self, asset_name: str, asset_type: str):
        """Smart asset selection logging - reduces spam"""
        current_asset = f"{asset_name}:{asset_type}"

        if current_asset == self.last_asset:
            self.repeat_count += 1
            if self.repeat_count == 1:  # Only log first repeat
                self.debug(f"Asset still selected: {asset_name}")
            # Suppress further repeats
        else:
            self.repeat_count = 0
            self.last_asset = current_asset
            self.info(f"Selected {asset_type[:-1]}: {asset_name}")

    def editor_opened(self, asset_name: str, asset_type: str):
        """Clean editor opening message"""
        self.info(f"Opened {asset_type[:-1]} editor: {asset_name}")

# Global logger instance
logger = ConsoleLogger()

def set_debug_mode(enabled: bool):
    """Enable/disable debug mode"""
    logger.debug_mode = enabled
    if enabled:
        logger.info("Debug mode enabled")
    else:
        logger.info("Debug mode disabled")

def suppress_startup_noise():
    """Suppress noisy startup messages"""
    # Hide pygame welcome message
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

    # Suppress Qt warnings about signals
    warnings.filterwarnings("ignore", category=RuntimeWarning,
                          message="Failed to disconnect.*from signal.*")

    # Suppress QToolBar warnings
    warnings.filterwarnings("ignore", message=".*objectName.*not set for QToolBar.*")
