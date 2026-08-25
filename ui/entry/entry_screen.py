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

image_path = "/Users/mbp/Desktop/roblox.png"


def image_creation(image_data, fg_seeds, bg_seeds):
    # original_label = button.get_label()
    # 4. Instantiate graph builder with parameters
    graphBuilder = GraphBuilderOpenCv(
        image_width=image_data.width, 
        image_height=image_data.height, 
        source=image_data.image
    )

        # 6. Convert coordinate seeds to SegmentationBoundaryPoint objects
    fg_points = {SegmentationBoundaryPoint(x, y) for x, y in fg_seeds}
    bg_points = {SegmentationBoundaryPoint(x, y) for x, y in bg_seeds}

        # 7. Perform Graph Cut segmentation (which trains GMM)
    segmentation_processor = GraphCutImageSegmentation(
        graph=graphBuilder, 
        fg_boundary_points=fg_points, 
        bg_boundary_points=bg_points
    )
    segmentation_processor.segmentation()

class EntryScreen(Gtk.ApplicationWindow):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.worker = ProcessPoolExecutor(max_workers=1)
        self.images = []
        self._background_task = None
        self.set_size_request(400, 400)
        self.set_default_size(600, 500)

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

        # canvas_input = ImagePlaceholder("/Users/mbp/Desktop/car.jpeg")
        canvas_value = ImagePlaceholder(image_path)

        # self.canvas_input = Canvas(content=canvas_input.picture, image_path="/Users/mbp/Desktop/car.jpeg")
        self.canvas_value = Canvas(content=canvas_value.picture, image_path=image_path)
        # canvas_input.set_child(self.canvas_input)
        canvas_value.set_child(self.canvas_value)

        button_action_section.append(self.process_button)
        button_action_section.append(clear_button)

        # image_content_section.append(canvas_input)
        image_content_section.append(canvas_value)
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

    
    def cleanup():
        #clean something
        raise NotImplementedError("This needs to be implemented")

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
            print(f"Error on process: {e}")
        

    def long_task(self, button, fg_seeds, bg_seeds):
        try:
            # 1. Load image using opencv data source
            image_source = ImageDataSourceOpenCvImpl()
            image_data = image_source.get_images(image_path)    

            future = self.worker.submit(
                image_creation, image_data, fg_seeds, bg_seeds
            )
            result = future.result()
            
            # # 2. Perform image creation / segmentation
            # self._image_creation(image_data, fg_seeds, bg_seeds)
            
            # 3. Refresh canvas_value to display result
            GLib.idle_add(self.canvas_value.update_image, image_path)

            self.canvas_value.clear_all_scribles()            
        except Exception as e:
            # GLib.idle_add(self._on_process_error, str(e))
            print(f"Error saat eksekusi: {e}")
            
        finally:
            GLib.idle_add(self.cleanup_ui_after_task, button)

    def cleanup_ui_after_task(self, button):
        """This runs back on the MAIN UI thread to refresh visuals."""
        # Refresh canvas_value to display result
        self.canvas_value.update_image(image_path)
    
        # Unlock UI elements
        button.set_sensitive(True)
        button.set_state(ButtonParams(isLoading=False, label=self.__process_button_label)) # Or reset to original label state
    
        return False # Returning False 

def on_activate(app):   
    # Create window
    win = EntryScreen(application=app)
    win.present()
     
