from ...barrel import *
from ui.widgets.button import Button, ButtonParams
from ui.entry.side_bar import SideBar
import asyncio
from ui.style_manager import StyleManager
from ui.widgets.canvas import Canvas

class ImagePlaceholder(Gtk.AspectFrame):
    def __init__(self, imagePath: str = ""):
        super().__init__()
        # self.set_size_request(200, 200)  
        # self.set_size_request(-1, 2000)
        self.set_ratio(16/9)
        self.set_xalign(0.5)
        self.set_yalign(0.5)
        self.set_obey_child(False)  
        StyleManager.add_from_string(css_string="background-color: red", className="image-placeholder", widget=self)
        picture = Gtk.Picture.new_for_filename(imagePath)
        picture.set_content_fit(Gtk.ContentFit.COVER)
        picture.set_hexpand(True)

        self.picture = picture
        

    
    
        
