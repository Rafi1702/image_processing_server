from ..barrel import *
from gi.repository import Pango
class SideBar(Gtk.Box):
    def __init__(self, images: list[str] = []):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_size_request(200, -1)
        self.set_hexpand(False)
        self.is_collapsed = False
        
        # Header Box for Title and Toggle Button
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header_box.set_margin_top(15)
        header_box.set_margin_bottom(15)
        header_box.set_margin_start(10)
        header_box.set_margin_end(10)
        
        
        # Toggle Button
        self.toggle_btn = Gtk.Button(icon_name="go-previous-symbolic")
        self.toggle_btn.set_has_frame(False) # Flat style
        self.toggle_btn.connect("clicked", self.on_toggle_clicked)
        header_box.append(self.toggle_btn)
        
        # Title
        self.title = Gtk.Label(label="Picked Images")
        self.title.set_hexpand(True)
        self.title.set_halign(Gtk.Align.START)
        header_box.append(self.title)
        
        self.append(header_box)
        
        # Add Image Button
        image_button_content = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        image_button_content.set_hexpand(True)
        image_button_content.append(Gtk.Label(label="Add Image"))
        image_button_content.append(Gtk.Box(hexpand=True))
        image_button_content.append(Gtk.Image.new_from_icon_name("document-save-symbolic"))
    

        add_image_button = Gtk.Button()
        add_image_button.set_child(image_button_content)
        add_image_button.connect("clicked", self.find_image_from_file_system)
        self.append(add_image_button)

        # Scrolled window for content
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_vexpand(True)
        self.append(self.scrolled_window)
        
        # List box for the images
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        
        # Placeholder when empty
        empty_label = Gtk.Label(label="No images picked yet")
        empty_label.set_margin_top(20)
        empty_label.add_css_class("dim-label") # Uses standard GTK dimmed style
        self.list_box.set_placeholder(empty_label)
        
        self.scrolled_window.set_child(self.list_box)
        
        # Add some mock data to visualize
        for image in images:
            self.add_image(image)
            
    def on_toggle_clicked(self, widget):
        self.is_collapsed = not self.is_collapsed
        
        if self.is_collapsed:
            self.title.set_visible(False)
            self.scrolled_window.set_visible(False)
            self.set_size_request(50, -1)
            self.toggle_btn.set_icon_name("go-next-symbolic")
        else:
            self.title.set_visible(True)
            self.scrolled_window.set_visible(True)
            self.set_size_request(200, -1)
            self.toggle_btn.set_icon_name("go-previous-symbolic")

    def find_image_from_file_system(self, image_path: str):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a folder",
            action=Gtk.FileChooserAction.OPEN,
            transient_for=self.get_root()
        )
        dialog.add_buttons(
            "Cancel", Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK
        )
        dialog.set_default_size(800, 400)

        filter_img = Gtk.FileFilter()
        filter_img.set_name("Semua Gambar")
        filter_img.add_pattern("*.jpg")
        filter_img.add_pattern("*.jpeg")
        filter_img.add_pattern("*.png")
        filter_img.add_pattern("*.JPG")
        filter_img.add_pattern("*.PNG")
        dialog.add_filter(filter_img)

        dialog.connect("response", self.handle_folder_selection)
        dialog.show()
        

    def handle_folder_selection(self, dialog, response_id):
        if response_id == Gtk.ResponseType.OK:
            path = dialog.get_file().get_path()
            print(f"Selected: {path}")
        dialog.destroy()
        

    def add_image(self, filename: str):
        list_row = Gtk.ListBoxRow()
        
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.set_margin_start(10)
        row.set_margin_end(10)
        row.set_margin_top(5)
        row.set_margin_bottom(5)
        
        icon = Gtk.Image.new_from_icon_name("image-x-generic")
        label = Gtk.Label(label=filename)
        
        # Prevent long filenames from pushing the sidebar width past 200px
      
        label.set_ellipsize(Pango.EllipsizeMode.END)
        label.set_max_width_chars(15)
        
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        
        # Delete Button
        delete_icon = Gtk.Button.new_from_icon_name("user-trash-symbolic")
        delete_icon.set_has_frame(False)
        delete_icon.add_css_class("destructive-action") # Optional style hint
        
        # Remove the list row when clicked
        delete_icon.connect("clicked", lambda btn: self.list_box.remove(list_row))

        row.append(icon)
        row.append(label)
        row.append(spacer)
        row.append(delete_icon)
        
        list_row.set_child(row)
        self.list_box.append(list_row)
        
        return list_row