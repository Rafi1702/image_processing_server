# ui/style_manager.py
from .barrel import *

class StyleManager:
    _instance = None
    _provider = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StyleManager, cls).__new__(cls)
            cls._provider = Gtk.CssProvider()
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(),
                cls._provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        return cls._instance

    def add_from_string(self, css_string: str):
        """Add raw CSS text to the application"""
        self._provider.load_from_data(css_string.encode())

    def add_from_file(self, file_path: str):
        """Add CSS from a specific file path"""
        self._provider.load_from_path(file_path)

# Create the single instance
styles = StyleManager()
