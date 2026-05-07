from build.lib.data import history_data_source
from ui.style_manager import StyleManager
from ..barrel import *
from ui.widgets.button import Button, ButtonParams
from ui.entry.side_bar import SideBar
from ui.entry.widgets.image_placeholder import ImagePlaceholder
import asyncio
from data.history_data_source import history_data_source

class EntryScreen(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.images = []
        self._background_task = None
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
        
        self.side_bar = SideBar()
        
        main_layout.append(self.side_bar)
        main_layout.append(vertical_box)

        self.set_child(main_layout)

    def on_start_clicked(self, widget):
        # 1. Cegah penumpukan task jika tombol diklik berkali-kali
        if self._background_task:
            return

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError: 
            loop = asyncio.get_event_loop()

        # 2. Buat task dan simpan referensinya
        task = loop.create_task(self.long_task(button=widget))
        self._background_task = task
        
        # 3. Bersihkan referensi saat selesai agar tidak memory leak
        task.add_done_callback(lambda t: setattr(self, '_background_task', None))

    async def long_task(self, button):
        original_label = button.get_label()
        
        try:
            # 4. Kunci UI agar user tahu proses sedang berjalan
            button.set_sensitive(False) 
            button.set_state(ButtonParams(isLoading=True))

            # Simulasi proses (Ganti dengan logika aiofiles atau I/O Anda)
            await asyncio.sleep(1)

            await history_data_source.read_file()
            
            for img in history_data_source.images:
                self.side_bar.add_image(img)
            
            
        except Exception as e:
            print(f"Error saat eksekusi: {e}")
            
        finally:
            button.set_state(ButtonParams(label=original_label, isLoading=False))
            button.set_sensitive(True)

    

def on_activate(app):
    # Create window
    win = EntryScreen(application=app)
    win.present()
     
