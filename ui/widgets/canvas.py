from ..barrel import *
from ..style_manager import StyleManager
import cairo

class Canvas(Gtk.Overlay):
    def __init__(self, content: Gtk.Widget = None, image_path: str = ""):
        super().__init__()
        self.set_child(content)
        self.image_path = image_path
        self.cv_image = None
        #Add Color to map on strokes
        self.strokes = []          # Completed strokes: [{'type': 'fg'/'bg', 'points': [(x, y)], 'color': (r, g, b)}]
        self.active_stroke = None  # Active stroke: {'type': 'fg'/'bg', 'points': [(x, y)], 'color': (r, g, b)}
        self.drag_start_x = 0.0
        self.drag_start_y = 0.0

        # Seed coordinates mapped to original image dimensions (for graph cut segmentation)
        self.fg_seeds = set()
        self.bg_seeds = set()

        # Load image via OpenCV to extract pixel color info
        if image_path:
            try:
                import cv2 as cv
                self.cv_image = cv.imread(image_path)
            except Exception as e:
                print(f"Error loading CV image in Canvas: {e}")

        # Create a DrawingArea overlay for rendering the green tint and the scribbles
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_hexpand(True)
        self.drawing_area.set_vexpand(True)
        self.drawing_area.set_halign(Gtk.Align.FILL)
        self.drawing_area.set_valign(Gtk.Align.FILL)
        self.drawing_area.set_draw_func(self.on_draw)
        self.add_overlay(self.drawing_area)

        # Foreground Gesture (Left-Click Drag)
        self.fg_drag = Gtk.GestureDrag()
        self.fg_drag.set_button(1)
        self.fg_drag.connect("drag-begin", self.on_drag_begin, "fg")
        self.fg_drag.connect("drag-update", self.on_drag_update, "fg")
        self.fg_drag.connect("drag-end", self.on_drag_end, "fg")
        self.drawing_area.add_controller(self.fg_drag)

        # Background Gesture (Right-Click Drag)
        self.bg_drag = Gtk.GestureDrag()
        self.bg_drag.set_button(3)
        self.bg_drag.connect("drag-begin", self.on_drag_begin, "bg")
        self.bg_drag.connect("drag-update", self.on_drag_update, "bg")
        self.bg_drag.connect("drag-end", self.on_drag_end, "bg")
        self.drawing_area.add_controller(self.bg_drag)

        # Click Gesture (Double-Click to Clear)
        self.click_gesture = Gtk.GestureClick()
        self.click_gesture.connect("released", self.on_click_released)
        self.drawing_area.add_controller(self.click_gesture)

    def on_drag_begin(self, gesture, start_x, start_y, stroke_type):
        width = self.drawing_area.get_width()
        height = self.drawing_area.get_height()
        if width > 0 and height > 0:
            self.drag_start_x = start_x
            self.drag_start_y = start_y
            nx = start_x / width
            ny = start_y / height
            self.active_stroke = {
                'type': stroke_type,
                'points': [(nx, ny)],
                'color': [] 
            }
            self.add_seed(nx, ny, stroke_type)

    def on_drag_update(self, gesture, offset_x, offset_y, stroke_type):
        if self.active_stroke:
            width = self.drawing_area.get_width()
            height = self.drawing_area.get_height()
            current_x = self.drag_start_x + offset_x
            current_y = self.drag_start_y + offset_y
            
            if width > 0 and height > 0:
                nx = current_x / width
                ny = current_y / height
                self.active_stroke['points'].append((nx, ny))
                self.add_seed(nx, ny, stroke_type)
                self.drawing_area.queue_draw()

    def on_drag_end(self, gesture, offset_x, offset_y, stroke_type):
        if self.active_stroke:
            self.strokes.append(self.active_stroke)
            print("Completed strokes:", self.strokes)
            self.active_stroke = None
            self.drawing_area.queue_draw()

    def on_click_released(self, n_press):
        if n_press == 2:  # Double click
            self.clear()



    def clear(self):
        self.strokes = []
        self.fg_seeds.clear()
        self.bg_seeds.clear()
        print("[Canvas] Cleared all scribbles.")
        self.drawing_area.queue_draw()


    def add_seed(self, nx, ny, stroke_type):
        if self.cv_image is not None:
            img_h, img_w, _ = self.cv_image.shape
            img_x = int(max(0, min(nx * img_w, img_w - 1)))
            img_y = int(max(0, min(ny * img_h, img_h - 1)))
            
            # Query color (BGR)
            color = self.cv_image[img_y, img_x]
            b, g, r = int(color[0]), int(color[1]), int(color[2])
            
            self.active_stroke['color'].append((r, g, b))
            
            # Log pixel mapping to console
            print(f"[{stroke_type.upper()} Scribble Point] Image: X={img_x}, Y={img_y} | RGB=({r}, {g}, {b})")

            # Save coordinates
            if stroke_type == "fg":
                self.fg_seeds.add((img_x, img_y))
            else:
                self.bg_seeds.add((img_x, img_y))

    def on_draw(self, drawing_area, cr, width, height):
        # 1. Draw the translucent green background overlay tint
        cr.set_source_rgba(0.0, 1.0, 0.0, 0.15)  # 15% opacity green
        cr.paint()

        # 2. Draw the outer green border boundary
        cr.set_source_rgba(0.0, 1.0, 0.0, 0.3)  # 30% opacity green
        cr.set_line_width(2)
        cr.rectangle(4, 4, width - 8, height - 8)
        cr.stroke()

        # Helper to draw a single stroke path
        def draw_stroke(stroke):
            points = stroke['points']
            if not points:
                return
            
            if stroke['type'] == 'fg':
                cr.set_source_rgba(0.9, 0.1, 0.1, 0.8)  # Semi-transparent red for foreground
            else:
                cr.set_source_rgba(0.1, 0.1, 0.9, 0.8)  # Semi-transparent blue for background
                
            cr.set_line_width(4)
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.set_line_join(cairo.LINE_JOIN_ROUND)

            x, y = points[0]
            cr.move_to(x * width, y * height)
            for x, y in points[1:]:
                cr.line_to(x * width, y * height)
            cr.stroke()

        # 3. Draw completed scribble strokes
        for stroke in self.strokes:
            draw_stroke(stroke)

        # 4. Draw active scribble stroke
        if self.active_stroke:
            draw_stroke(self.active_stroke)

        # 5. Draw a helper HUD in the corner of the canvas
        text = "L-Click Drag: Red (FG) | R-Click Drag: Blue (BG) | Double-Click: Clear"
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(10)
        extents = cr.text_extents(text)

        box_w = extents.width + 12
        box_h = extents.height + 8
        box_x = 10
        box_y = height - box_h - 10

        cr.set_source_rgba(0.0, 0.0, 0.0, 0.6)  # Dark semi-transparent HUD background
        cr.rectangle(box_x, box_y, box_w, box_h)
        cr.fill()

        cr.show_text(text)

    def clear_all_scribles(self):
        self.clear()
        
    def update_image(self, image_path: str):
        self.image_path = image_path
        try:
            import cv2 as cv
            self.cv_image = cv.imread(image_path)
            child = self.get_child()
            if isinstance(child, Gtk.Picture):
                child.set_filename(image_path)
        except Exception as e:
            print(f"Error updating image in Canvas: {e}")
        self.drawing_area.queue_draw()