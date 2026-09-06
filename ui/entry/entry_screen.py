from ui.style_manager import StyleManager
from ..barrel import *
from ui.widgets.button import Button, ButtonParams
from ui.entry.side_bar import SideBar
from ui.entry.widgets.image_placeholder import ImagePlaceholder
import threading
from multiprocessing import Process
from data.datasource.history_data_source import history_data_source
from data.datasource.implementation.image_data_source_opencv_impl import ImageDataSourceOpenCvImpl
from image_processor.graph_util import GraphBuilderOpenCv
from image_processor.image_segmentation import GraphCutImageSegmentation, SegmentationBoundaryPoint
from ui.widgets.canvas import Canvas
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import traceback
import sys


image_path = "/Users/mbp/Desktop/OtherProjects/image_processing_server/image_processor/roblox.png"
# image_path = "/Users/mbp/Desktop/dummy_image.jpg"


def image_creation(image_data, fg_seeds, bg_seeds):
    fg_points = {SegmentationBoundaryPoint(x, y) for x, y in fg_seeds}
    bg_points = {SegmentationBoundaryPoint(x, y) for x, y in bg_seeds}

    return GraphCutImageSegmentation(
        image_data=image_data,
        fg_boundary_points=fg_points, 
        bg_boundary_points=bg_points,
    ).segmentation()

class EntryScreen(Gtk.ApplicationWindow):
    
    def __init__(self, image_data_source ,**kwargs,):
        super().__init__(**kwargs)
        self.worker = ProcessPoolExecutor(max_workers=1)
        self.images = []
        self._background_task = None
        self.set_size_request(400, 400)
        self.set_default_size(600, 500)
        self.image_data_source = image_data_source

        vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vertical_box.set_hexpand(True)
        vertical_box.set_vexpand(True)
            
        image_content_section = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, hexpand=True)
        button_action_section = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

        image_content_section.set_size_request(-1, 500) 

        outlined_button = Button(label = "Stop", style="Outlined")
        button_action_section.append(outlined_button)


        self.__process_button_label = "Process"
        self.process_button = Button(label = self.__process_button_label)
        self.process_button.connect("clicked", self.on_start_clicked)

        clear_button = Button(label="Clear")
        clear_button.connect("clicked", self.on_clear_button_clicked)

        canvas_value = ImagePlaceholder(image_path)
        self.canvas_value = Canvas(content=canvas_value.picture, image_path=image_path)

        canvas_value.set_child(self.canvas_value)

        button_action_section.append(self.process_button)
        button_action_section.append(clear_button)
        image_content_section.append(canvas_value)

        image_content_section.set_homogeneous(True)
        vertical_box.append(image_content_section)
        vertical_box.append(button_action_section)

        # Build the main layout
        main_layout = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)

        # Add sidebar to the left
        self.side_bar = SideBar()
        
        main_layout.append(self.side_bar)
        main_layout.append(vertical_box)

        self.set_child(main_layout)
        self.connect("unmap",self._on_widget_destroyed)


    def _cleanup_worker(self):
        if self.worker:
            # cancel_futures=True discards any pending work in the queue
            # wait=False stops Python from waiting on completion
            self.worker.shutdown(wait=False, cancel_futures=True)
            self.worker = None
    
    def _on_widget_destroyed(self):        
        return self._cleanup_worker

    def __del__(self):
        return self._cleanup_worker
    
    def on_clear_button_clicked(self, button):
        self.canvas_value.clear_all_scribles()


    def on_start_clicked(self, widget):
        button = self.process_button

        if self._background_task and self._background_task.is_alive():
            return


        if not button.get_sensitive():
            print("button is not sensitive")
            return

        fg_seeds = self.canvas_value.fg_seeds
        bg_seeds = self.canvas_value.bg_seeds

        # 1. Gather seeds coordinates from canvas
        if len(fg_seeds) == 0 or len(bg_seeds) == 0:
            print("Warning: Please scribble on both foreground (Left-Click) and background (Right-Click) before processing.")
            return

        # 2. Lock UI
        GLib.idle_add(button.set_sensitive, False)
        GLib.idle_add(button.set_state, ButtonParams(isLoading=True))

        #3. create new process
        try:
            # process = Process(target=self.long_task, args=(widget, fg_seeds, bg_seeds),)
            thread = threading.Thread(target=self.long_task, args=(widget, fg_seeds, bg_seeds), daemon=True)
            self._background_task = thread
            thread.start()    
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            

            tb = traceback.extract_tb(exc_traceback)[-1]
            print(f"Error on process: {e} line: {tb.lineno}")
        
        
    def long_task(self, button, fg_seeds, bg_seeds):
          # 1. Load image using opencv data source
        image_data = self.image_data_source.get_images(image_path)    

        future = self.worker.submit(
            image_creation, image_data, fg_seeds, bg_seeds
        )
        
        future.add_done_callback(self._on_future_completed)


    def _on_future_completed(self, future):
        updated_image = future.result() or "/Users/mbp/Desktop/output_image2.png"

        GLib.idle_add(self._on_ui_updated, updated_image)
    
    def _on_ui_updated(self, updated_image):
        self.canvas_value.update_image(updated_image)
        self.process_button.set_sensitive(True)
        self.process_button.set_state(ButtonParams(isLoading=False, label=self.__process_button_label)) # Or reset to original label state
        self.canvas_value.clear_all_scribles()     
    
         


