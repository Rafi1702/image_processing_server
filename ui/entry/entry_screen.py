from ..barrel import *
from ui.base_layout import BaseLayout
from ui.widgets.button import Button

class EntryScreen(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vertical_box = BaseLayout()
            
        content_section = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_action_section = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_action_section.append(Gtk.Button(label="Scan"))
        button_action_section.append(Gtk.Button(label="Stop"))
        outlined_button = Button(label = "Outlined", style="Outlined")
        button_action_section.append(outlined_button)
        
        content_section.append(Gtk.Label(label="Content"))
        content_section.append(Gtk.Label(label="123"))

        vertical_box.add_child(content_section)
        vertical_box.add_child(button_action_section)

        self.set_child(vertical_box)   
     

def on_activate(app):
    # Create window
    win = EntryScreen(application=app)
    win.present()
     
