#!/usr/bin/env python3
"""
Extra Action Handlers

Handles miscellaneous actions: debug, cursor, screenshots, etc.
"""

from typing import Dict, Any

from core.logger import get_logger
from runtime.action_handlers.base import (
    Parameters, Instance, HandlerContext,
    parse_int, parse_bool,
)

logger = get_logger(__name__)


def handle_set_cursor(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the mouse cursor sprite."""
    sprite = params.get("sprite", "")
    if ctx.game_runner:
        ctx.game_runner.cursor_sprite = sprite
    logger.debug(f"  🖱️ Set cursor sprite: '{sprite}'")


def handle_show_cursor(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Show or hide the mouse cursor."""
    visible = parse_bool(params.get("visible", True))
    if ctx.game_runner:
        ctx.game_runner.cursor_visible = visible
    logger.debug(f"  🖱️ Cursor visible: {visible}")


def handle_screenshot(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Take a screenshot."""
    filename = params.get("filename", "screenshot.png")
    if ctx.game_runner:
        ctx.game_runner.pending_screenshot = filename
    logger.debug(f"  📸 Screenshot requested: '{filename}'")


def handle_set_fps(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the target frames per second."""
    fps = parse_int(ctx, params.get("fps", 60), instance, default=60)
    if ctx.game_runner:
        ctx.game_runner.target_fps = fps
    logger.debug(f"  ⏱️ Set FPS: {fps}")


def handle_splash_show_text(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Show splash text (placeholder)."""
    text = params.get("text", "")
    logger.debug(f"  💬 Splash text: '{text[:30]}...'")


def handle_splash_show_image(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Show splash image (placeholder)."""
    image = params.get("image", "")
    logger.debug(f"  🖼️ Splash image: '{image}'")


def handle_splash_show_video(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Show splash video (placeholder)."""
    video = params.get("video", "")
    logger.debug(f"  🎬 Splash video: '{video}'")


def handle_splash_show_webpage(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Show webpage in splash (placeholder)."""
    url = params.get("url", "")
    logger.debug(f"  🌐 Splash webpage: '{url}'")


def handle_open_url(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Open a URL in the default browser."""
    import webbrowser
    url = params.get("url", "")
    if url:
        webbrowser.open(url)
    logger.debug(f"  🌐 Open URL: '{url}'")


def handle_execute_file(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Execute an external file (placeholder - security restricted)."""
    filename = params.get("filename", "")
    logger.debug(f"  📂 Execute file request (disabled): '{filename}'")


def handle_execute_shell(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Execute a shell command (placeholder - security restricted)."""
    command = params.get("command", "")
    logger.debug(f"  💻 Shell command request (disabled): '{command}'")


def handle_display_mouse(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Get or set mouse display state."""
    x = parse_int(ctx, params.get("x", None), instance, default=None)
    y = parse_int(ctx, params.get("y", None), instance, default=None)

    if ctx.game_runner and x is not None and y is not None:
        ctx.game_runner.set_mouse_position(x, y)
    logger.debug(f"  🖱️ Set mouse position: ({x}, {y})")


def handle_window_center(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Center the game window."""
    if ctx.game_runner:
        ctx.game_runner.center_window_flag = True
    logger.debug("  🪟 Center window requested")


def handle_window_set_size(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Set the window size."""
    width = parse_int(ctx, params.get("width", 640), instance, default=640)
    height = parse_int(ctx, params.get("height", 480), instance, default=480)

    if ctx.game_runner:
        ctx.game_runner.window_size = (width, height)
    logger.debug(f"  🪟 Set window size: {width}x{height}")


def handle_debug_message(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Print a debug message."""
    message = params.get("message", "")
    logger.info(f"🐛 DEBUG: {message}")


def handle_debug_show_value(ctx: HandlerContext, instance: Instance, params: Parameters) -> None:
    """Show a variable value for debugging."""
    variable = params.get("variable", "")
    if variable:
        value = ctx._parse_value(variable, instance)
        logger.info(f"🐛 {variable} = {value}")







# =============================================================================
# Handler Registry
# =============================================================================

EXTRA_HANDLERS: Dict[str, Any] = {
    "set_cursor": handle_set_cursor,
    "show_cursor": handle_show_cursor,
    "screenshot": handle_screenshot,
    "set_fps": handle_set_fps,
    "splash_show_text": handle_splash_show_text,
    "splash_show_image": handle_splash_show_image,
    "splash_show_video": handle_splash_show_video,
    "splash_show_webpage": handle_splash_show_webpage,
    "open_url": handle_open_url,
    "execute_file": handle_execute_file,
    "execute_shell": handle_execute_shell,
    "display_mouse": handle_display_mouse,
    "window_center": handle_window_center,
    "window_set_size": handle_window_set_size,
    "debug_message": handle_debug_message,
    "debug_show_value": handle_debug_show_value,
    # Additional handlers
}
