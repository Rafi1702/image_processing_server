from image_processor.image_segmentation import GraphCutImageSegmentation, SegmentationBoundaryPoint
from multiprocessing import Pool
import gi
import asyncio
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio
from gi.events import GLibEventLoopPolicy
from ui.entry.entry_screen import on_activate
from data.datasource.implementation.image_data_source_opencv_impl import ImageDataSourceOpenCvImpl
from image_processor.graph_util import GraphBuilderOpenCv
from threading import Thread

async def run_app():

    # image_source = ImageDataSourceOpenCvImpl()

    # image_source.get_images("/Users/mbp/Desktop/image1.png")
    app = Gtk.Application(application_id="com.example.ImageProcessing", flags=Gio.ApplicationFlags.FLAGS_NONE)
    app.connect("activate", on_activate)
    
    # Register and activate the application without blocking
    app.register(None)
    app.activate()
    
    # Create an event to keep the asyncio loop running until all windows are closed
    stop_event = asyncio.Event()
    
    def on_window_removed(app, window):
        if not app.get_windows():
            stop_event.set()
            
    app.connect("window-removed", on_window_removed)
    
    # Keep the async loop alive until the stop_event is set
    await stop_event.wait()


async def async_range(count):
    for i in range(count):
        await asyncio.sleep(1)  # Simulate an async I/O operation
        yield i
               
def main():

    asyncio.set_event_loop_policy(GLibEventLoopPolicy())
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run_app())
    finally:
        loop.close()

    # loop = asyncio.get_event_loop()

    # image_source = ImageDataSourceOpenCvImpl()

    # image_data = image_source.get_images("/Users/mbp/Desktop/image1.png")    
    
    # graphBuilder = GraphBuilderOpenCv(image_width= image_data.width, image_height= image_data.height, source=image_data.image)

    # graphBuilder.build_graph()    

    # fg_points = {
    #     SegmentationBoundaryPoint(image_data.width - 2, image_data.height - 2),
    #     SegmentationBoundaryPoint(image_data.width - 3, image_data.height - 2),
    #     SegmentationBoundaryPoint(image_data.width - 2, image_data.height - 3),
    #     SegmentationBoundaryPoint(image_data.width - 3, image_data.height - 3)
    # }

    # Membuat seed background dengan beberapa titik di pojok kiri atas
    # offset = 5

    # bg_points = {   
    #     SegmentationBoundaryPoint(offset, offset),         
    #     SegmentationBoundaryPoint(image_data.width - offset, offset),     
    #     SegmentationBoundaryPoint(offset, image_data.height - offset),     
    #     SegmentationBoundaryPoint(image_data.width - offset, image_data.height - offset)  
    # }

    # graphBasedImageSegmentation = GraphCutImageSegmentation(graphBuilder, fg_boundary_points=fg_points, bg_boundary_points=bg_points)

    # print("fg_points: ", fg_points)
    # print("bg_points: ", bg_points)
    
    # graphBasedImageSegmentation.segmentation()    
    
     

if __name__ == "__main__":
    main()

    
    
  # image_source = ImageDataSourceOpenCvImpl()

    # image_data = image_source.get_images("/Users/mbp/Desktop/image1.png")    
    
    # graphBuilder = GraphBuilderOpenCv()
    
    
    # loop = asyncio.get_running_loop()
        
    # # 2. Spin up the graph builder on a completely separate CPU core
    # graph_task = loop.run_in_executor(
    #         pool, 
    #         graphBuilder.build_graph, 
    #         image_data.image, 
    #         image_data.width, 
    #         image_data.height
    #     )

    # # 3. This loop now runs unhindered on the main CPU core
    # async for value in async_range(30):
    #     print(f"Received: {value}")

    # # 4. Await the separate process execution to grab the final output
    # graph_result = await graph_task