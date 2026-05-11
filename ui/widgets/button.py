from ..barrel import *
from ..style_manager import styles
from enum import Enum

class ButtonStyle(Enum):
    OUTLINED = 1
    PRIMARY = 2


@dataclass
class ButtonParams():
    label: str = ""
    style: ButtonStyle = ButtonStyle.PRIMARY
    isLoading: bool = False
    isDisabled: bool = False   

class Button(Gtk.Button):
    def __init__(self, label:str, style: ButtonStyle = ButtonStyle.PRIMARY):
        super().__init__(label=label)
        
        styles.add_from_file("ui/widgets/button.css")

        if(style == ButtonStyle.OUTLINED):
            self.add_css_class("btn-outline")
        else:
            self.add_css_class("btn-primary")


    def set_state(self, params: ButtonParams):
        if(params.isLoading):   
            spinner = Gtk.Spinner()
            spinner.start()
            
            self.set_sensitive(False)
            self.set_child(spinner)
        else:
            self.set_child(Gtk.Label(label= params.label))
            self.set_sensitive(True)
            