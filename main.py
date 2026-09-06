from image_processor.image_segmentation import GraphCutImageSegmentation, SegmentationBoundaryPoint
import gi
import sys
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio
from gi.events import GLibEventLoopPolicy
from ui.entry.entry_screen import EntryScreen
from data.datasource.implementation.image_data_source_opencv_impl import ImageDataSourceOpenCvImpl, ImageDataSourcePilImpl

from threading import Thread

def run_app():
    app = Gtk.Application(application_id="com.example.ImageProcessing")
    app.connect("activate", on_activate)
    return app.run(sys.argv)
               
def main():
    try: 
        run_app()
    except Exception as e: 
        print(f"Failed to start app {e}")
    

def on_activate(app):   
    # Create window
    win = app.get_active_window()
    if not win:
        win = EntryScreen(
            application=app, image_data_source=ImageDataSourcePilImpl()
        )

    win.present()
     
    
if __name__ == "__main__":
    sys.exit(main())    