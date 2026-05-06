
from ui.style_manager import StyleManager
from ..barrel import *
from ui.widgets.button import Button, ButtonParams
from ui.entry.side_bar import SideBar
from ui.entry.widgets.image_placeholder import ImagePlaceholder
import asyncio

class EntryScreen(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_size_request(400, 400)
        self.set_default_size(600, 500)

        vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vertical_box.set_hexpand(True)
        vertical_box.set_vexpand(True)
            
        image_content_section = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10, vexpand=True, hexpand=True)
        button_action_section = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        outlined_button = Button(label = "Stop", style="Outlined")
        button_action_section.append(outlined_button)

        process_button = Button(label = "Process")
        process_button.connect("clicked", self.on_start_clicked)

        image_input_placeholder = ImagePlaceholder()
        image_value_placeholder = ImagePlaceholder()

        button_action_section.append(process_button)

        image_content_section.append(image_input_placeholder)
        image_content_section.append(image_value_placeholder)
        image_content_section.set_homogeneous(True)
        
        vertical_box.append(image_content_section)
        vertical_box.append(button_action_section)

        
        # Build the main layout
        main_layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        StyleManager.add_from_string(
            css_string="background-color: green", 
            className="green-content", 
            widget=image_content_section
        )   
        
        # Add sidebar to the left
        
        self.side_bar = SideBar(images=[
            "vacation_photo.png", 
            "profile_pic.jpg", 
            "screenshot_2023.png",
            "background_nature.jpeg",
            "logo_design.svg"
        ])
        main_layout.append(self.side_bar)
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
     
