from ..barrel import *
from ..style_manager import styles



class Button(Gtk.Button):
    def __init__(self, label: str, style="None"):
        super().__init__(label= label)

        if(style == "Outlined"):
            styles.add_from_file("ui/widgets/button.css")
            self.add_css_class("btn-outline")
