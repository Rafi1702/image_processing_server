import gi
import asyncio
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio
from ui.entry.entry_screen import on_activate
from gi.events import GLibEventLoop

async def run_app():
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

def main():
    
    loop = GLibEventLoop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_app())
    finally:
        loop.close()

if __name__ == "__main__":
    main()
