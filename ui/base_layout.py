from .barrel import *

class BaseLayout(Gtk.Widget):
    def __init__(self):
        super().__init__()

        # FIX 1: Add a Layout Manager so this widget expands with its parent
        self.set_layout_manager(Gtk.BinLayout())

        # FIX 2: Create the internal box and set it to fill space
        self.main_layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.main_layout.set_hexpand(True)
        self.main_layout.set_vexpand(True)
        
        # Attach the box to this widget
        self.main_layout.set_parent(self)

    # FIX 3: Ensure this method is outside the __init__ scope
    def add_child(self, widget):
        self.main_layout.append(widget)

