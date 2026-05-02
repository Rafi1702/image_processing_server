import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from ui.entry.entry_screen import on_activate

def main():
    # GTK 4 requires an Application context instead of Gtk.main()
    app = Gtk.Application(application_id="com.example.ImageProcessing")
    app.connect("activate", on_activate)
    app.run(None)

if __name__ == "__main__":
    main()
