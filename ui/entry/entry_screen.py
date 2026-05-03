
from ..barrel import *
from ui.widgets.button import Button, ButtonParams
from ui.entry.side_bar import SideBar
import asyncio

class EntryScreen(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vertical_box.set_hexpand(True)
        vertical_box.set_vexpand(True)
            
        content_section = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        button_action_section = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        outlined_button = Button(label = "Stop", style="Outlined")
        button_action_section.append(outlined_button)

        process_button = Button(label = "Process")
        process_button.connect("clicked", self.on_start_clicked)

        button_action_section.append(process_button)    
        content_section.append(Gtk.Label(label="Content"))
        content_section.append(Gtk.Label(label="123"))

        vertical_box.append(content_section)
        vertical_box.append(button_action_section)

        
        # Build the main layout
        main_layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        # Add sidebar to the left
        
        self.side_bar = SideBar(images=[
            "vacation_photo.png", 
            "profile_pic.jpg", 
            "screenshot_2023.png",
            "background_nature.jpeg",
            "logo_design.svg"
        ])
        main_layout.append(self.side_bar)
        
        # Add the existing vertical content layout to the right
        vertical_box.set_hexpand(True)
        main_layout.append(vertical_box)

        self.set_child(main_layout)

    def on_start_clicked(self, widget):
        loop = asyncio.get_event_loop()
        # Keep a strong reference to the task to prevent it from being garbage collected
        self._background_task = loop.create_task(self.long_task(button=widget))

    async def long_task(self, button):
        label = button.get_label()
        button.set_state(ButtonParams(isLoading=True))
        await asyncio.sleep(3)
        button.set_state(ButtonParams(label=label, isLoading=False))

def on_activate(app):
    # Create window
    win = EntryScreen(application=app)
    win.present()
     
