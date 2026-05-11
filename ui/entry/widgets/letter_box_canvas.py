from ...barrel import *

class LetterBoxCanvas(Gtk.DrawingArea):
    def __init__(self, image_path: str):
        super().__init__()
        # self.pixel_information = GdkPixBuf.new_from_file(image_path)
        # self.set_draw_func(self.on_draw)    
    
    def on_draw(self, drawing_area, cr, width, height):
        pass