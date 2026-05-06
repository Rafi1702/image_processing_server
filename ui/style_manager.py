# ui/style_manager.py
from .barrel import *

class StyleManager:
    _instance = None
    _provider = None
    _all_styles = ""

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

    @classmethod
    def add_from_string(cls, css_string: str, className: str, widget: Gtk.Widget):
        """Menghubungkan widget ke class CSS dan memuat style-nya"""
        
        # 1. Tambahkan class ke widget (hanya satu titik untuk selector CSS)
        widget.add_css_class(className)
        
        # 2. Format CSS yang benar (Gunakan satu titik '.' untuk class selector)
        # Tambahkan juga semicolon ';' jika lupa ditulis di parameter
        new_css = f".{className} {{ {css_string}; }}\n"
        
        # 3. Simpan ke buffer agar CSS dari widget lain tidak hilang
        cls._all_styles += new_css
        
        # 4. Muat ke provider
        cls._provider.load_from_data(cls._all_styles.encode())

    @classmethod
    def add_from_file(cls, file_path: str):
        """Add CSS from a specific file path"""
        cls._provider.load_from_path(file_path)

# Create the single instance
styles = StyleManager()
