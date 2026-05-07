from ...barrel import *
from ui.widgets.button import Button, ButtonParams
from ui.entry.side_bar import SideBar
import asyncio
from ui.style_manager import StyleManager

class ImagePlaceholder(Gtk.Box):
    def __init__(self, imagePath: str = ""):
        super().__init__()
        self.set_size_request(200, 200)
        
        StyleManager.add_from_string(css_string="background-color: red", className="image-placeholder", widget=self)
        picture = Gtk.Picture.new_for_filename(imagePath)
        self.append(picture)
        self.show()
    
    
        
