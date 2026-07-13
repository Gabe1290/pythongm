import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
import json
import os
import pygame
from PIL import Image, ImageTk

class RoomEditorWindow(tk.Toplevel):
    def __init__(self, master, room_file_path, project_data):
        super().__init__(master)
        self.transient(master)
        
        pygame.display.init()
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
        print("RoomEditor created its own dummy Pygame display.")

        self.room_file_path = room_file_path
        self.project_data = project_data
        self.room_data = None
        self.is_running = True

        self.load_room_data()
        self.title(f"Room Editor - {os.path.basename(room_file_path)}")
        self.geometry("900x700")

        self.canvas_width = self.room_data.get('settings', {}).get('width', 800)
        self.canvas_height = self.room_data.get('settings', {}).get('height', 600)
        self.pygame_surface = pygame.Surface((self.canvas_width, self.canvas_height))
        
        self.sprite_cache = {}
        self.active_object_name = None
        self.grid_size = 32
        self.edit_mode = "Settings"
        self.active_tile_id = 0
        self.tileset_for_ui = None
        self.tileset_for_pygame = None
        self.background_image = None

        self.room_width_var = tk.IntVar(value=self.canvas_width)
        self.room_height_var = tk.IntVar(value=self.canvas_height)

        self.create_widgets()
        self.load_assets()
        self.update_pygame_canvas()
        
        self.after(10, self.grab_set)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        print("Closing room editor, shutting down its Pygame display.")
        self.is_running = False
        pygame.display.quit()
        self.destroy()

    def load_room_data(self):
        try:
            with open(self.room_file_path, 'r') as f:
                self.room_data = json.load(f)
            if "settings" not in self.room_data: self.room_data["settings"] = {}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Failed to load room data: {e}", parent=self)
            self.on_close()

    def create_widgets(self):
        v_pane = ttk.PanedWindow(self, orient=tk.VERTICAL); v_pane.pack(fill=tk.BOTH, expand=True)
        top_content_frame = ttk.Frame(v_pane); v_pane.add(top_content_frame, weight=1)
        bottom_button_frame = ttk.Frame(v_pane, height=40, padding=(5,5)); v_pane.add(bottom_button_frame, weight=0); bottom_button_frame.pack_propagate(False)
        h_pane = ttk.PanedWindow(top_content_frame, orient=tk.HORIZONTAL); h_pane.pack(fill=tk.BOTH, expand=True)
        left_frame = ttk.Frame(h_pane, width=250); h_pane.add(left_frame, weight=0)
        self.canvas_frame = tk.Frame(h_pane); h_pane.add(self.canvas_frame, weight=1)
        self.notebook = ttk.Notebook(left_frame); self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5); self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        settings_tab = ttk.Frame(self.notebook, padding=5); self.notebook.add(settings_tab, text="Settings")
        settings_frame = ttk.LabelFrame(settings_tab, text="Room Dimensions", padding=5); settings_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(settings_frame, text="Width:").grid(row=0, column=0, sticky="w", padx=5); ttk.Entry(settings_frame, textvariable=self.room_width_var).grid(row=0, column=1, sticky="ew")
        ttk.Label(settings_frame, text="Height:").grid(row=1, column=0, sticky="w", padx=5); ttk.Entry(settings_frame, textvariable=self.room_height_var).grid(row=1, column=1, sticky="ew")
        ttk.Button(settings_frame, text="Apply Size", command=self.on_apply_size).grid(row=2, column=0, columnspan=2, pady=5); settings_frame.columnconfigure(1, weight=1)

        objects_tab = ttk.Frame(self.notebook); self.notebook.add(objects_tab, text="Objects")
        ttk.Label(objects_tab, text="L-Click: Place\nR-Click: Remove").pack(pady=5, padx=5)
        objects_frame = ttk.LabelFrame(objects_tab, text="Object List"); objects_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5); self.object_listbox = tk.Listbox(objects_frame); self.object_listbox.pack(fill=tk.BOTH, expand=True)
        for obj_res in self.project_data['resources'].get('objects', []): self.object_listbox.insert(tk.END, obj_res['name'])
        self.object_listbox.bind("<<ListboxSelect>>", self.on_object_selected)
        
        tiles_tab = ttk.Frame(self.notebook); self.notebook.add(tiles_tab, text="Tiles")
        tileset_frame = ttk.LabelFrame(tiles_tab, text="Tileset"); tileset_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5); self.tileset_canvas = tk.Canvas(tileset_frame, background="gray"); self.tileset_canvas.pack(); self.tileset_canvas.bind("<Button-1>", self.on_tileset_click)
        
        background_tab = ttk.Frame(self.notebook); self.notebook.add(background_tab, text="Background")
        bg_image_names = ["None"] + [b['name'] for b in self.project_data['resources'].get('backgrounds', [])]
        self.bg_image_var = tk.StringVar(value=self.room_data['settings'].get('background_image', "None"))
        bg_image_frame = ttk.LabelFrame(background_tab, text="Image", padding=5); bg_image_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(bg_image_frame, text="Image:").grid(row=0, column=0, sticky="w"); self.bg_image_combo = ttk.Combobox(bg_image_frame, textvariable=self.bg_image_var, values=bg_image_names, state="readonly"); self.bg_image_combo.grid(row=0, column=1, sticky="ew"); self.bg_image_combo.bind("<<ComboboxSelected>>", self.on_bg_image_selected); bg_image_frame.columnconfigure(1, weight=1)
        self.bg_mode_var = tk.StringVar(value=self.room_data['settings'].get('background_mode', 'Tiled'))
        bg_mode_frame = ttk.LabelFrame(background_tab, text="Display Mode", padding=5); bg_mode_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Radiobutton(bg_mode_frame, text="Tiled", variable=self.bg_mode_var, value="Tiled").pack(anchor="w"); ttk.Radiobutton(bg_mode_frame, text="Fixed", variable=self.bg_mode_var, value="Fixed").pack(anchor="w"); ttk.Radiobutton(bg_mode_frame, text="Stretched", variable=self.bg_mode_var, value="Stretched").pack(anchor="w")
        self.bg_scroll_x_var = tk.DoubleVar(value=self.room_data['settings'].get('background_scroll_x', 1.0)); self.bg_scroll_y_var = tk.DoubleVar(value=self.room_data['settings'].get('background_scroll_y', 1.0))
        bg_scroll_frame = ttk.LabelFrame(background_tab, text="Scrolling Speed", padding=5); bg_scroll_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(bg_scroll_frame, text="X Speed:").grid(row=0, column=0, sticky="w"); ttk.Entry(bg_scroll_frame, textvariable=self.bg_scroll_x_var).grid(row=0, column=1, sticky="ew"); ttk.Label(bg_scroll_frame, text="Y Speed:").grid(row=1, column=0, sticky="w"); ttk.Entry(bg_scroll_frame, textvariable=self.bg_scroll_y_var).grid(row=1, column=1, sticky="ew"); bg_scroll_frame.columnconfigure(1, weight=1)
        bg_color_frame = ttk.LabelFrame(background_tab, text="Background Color", padding=5); bg_color_frame.pack(fill=tk.X, padx=5, pady=5); self.bg_color_button = ttk.Button(bg_color_frame, text="Choose Color...", command=self.choose_bg_color); self.bg_color_button.pack(pady=2)

        self.canvas_frame.grid_rowconfigure(0, weight=1); self.canvas_frame.grid_columnconfigure(0, weight=1)
        self.pygame_canvas_widget = tk.Canvas(self.canvas_frame, bg="black", scrollregion=(0, 0, self.canvas_width, self.canvas_height))
        hbar = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.pygame_canvas_widget.xview); vbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.pygame_canvas_widget.yview)
        self.pygame_canvas_widget.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)
        self.pygame_canvas_widget.grid(row=0, column=0, sticky='nsew'); hbar.grid(row=1, column=0, sticky='ew'); vbar.grid(row=0, column=1, sticky='ns')
        self.pygame_canvas_widget.bind("<B1-Motion>", self.on_mouse_drag); self.pygame_canvas_widget.bind("<Button-1>", self.on_mouse_drag)
        self.pygame_canvas_widget.bind("<B3-Motion>", self.on_mouse_drag_right); self.pygame_canvas_widget.bind("<Button-3>", self.on_mouse_drag_right)
        
        ttk.Button(bottom_button_frame, text="Save & Close", command=self.save_and_close).pack(side=tk.RIGHT, padx=(0,5))
        ttk.Button(bottom_button_frame, text="Cancel", command=self.on_close).pack(side=tk.RIGHT)

    def on_apply_size(self):
        try:
            new_width = self.room_width_var.get(); new_height = self.room_height_var.get()
            if new_width < 100 or new_height < 100: messagebox.showwarning("Invalid Size", "Width and Height must be at least 100.", parent=self); return
            self.canvas_width = new_width; self.canvas_height = new_height
            self.pygame_canvas_widget.config(scrollregion=(0, 0, self.canvas_width, self.canvas_height))
            self.pygame_surface = pygame.Surface((self.canvas_width, self.canvas_height))
            messagebox.showinfo("Size Updated", "Room size updated. Don't forget to save!", parent=self)
        except tk.TclError: messagebox.showerror("Invalid Input", "Please enter valid numbers.", parent=self)

    def choose_bg_color(self):
        rgb_color = self.room_data['settings'].get('background_color', [0,0,0])
        hex_color = f'#{rgb_color[0]:02x}{rgb_color[1]:02x}{rgb_color[2]:02x}'
        color_code = colorchooser.askcolor(title="Choose Background Color", initialcolor=hex_color, parent=self)
        if color_code and color_code[0]: self.room_data['settings']['background_color'] = [int(c) for c in color_code[0]]

    def on_bg_image_selected(self, event=None):
        image_name = self.bg_image_var.get()
        self.room_data['settings']['background_image'] = image_name
        if image_name == "None": self.background_image = None; return
        for img_info in self.project_data['resources'].get('backgrounds', []):
            if img_info['name'] == image_name:
                try: self.background_image = pygame.image.load(os.path.join(self.master.project_root, img_info['path'])).convert_alpha()
                except Exception as e: print(f"Error loading background image: {e}"); self.background_image = None
                return
    
    def get_or_create_tile_layer(self):
        if 'tile_layers' not in self.room_data: self.room_data['tile_layers'] = []
        if not self.room_data['tile_layers']:
            cols = self.canvas_width // self.grid_size; rows = self.canvas_height // self.grid_size
            self.room_data['tile_layers'].append({"tileset": "ts_world1", "depth": 10000, "tiles": [[-1] * cols for _ in range(rows)]})
        return self.room_data['tile_layers'][0]

    def update_pygame_canvas(self):
        if not self.is_running: return
        
        if self.background_image:
            mode = self.bg_mode_var.get()
            if mode == "Stretched": self.pygame_surface.blit(pygame.transform.scale(self.background_image, (self.canvas_width, self.canvas_height)), (0, 0))
            elif mode == "Tiled":
                bw, bh = self.background_image.get_size()
                if bw > 0 and bh > 0:
                    for x in range(0, self.canvas_width, bw):
                        for y in range(0, self.canvas_height, bh): self.pygame_surface.blit(self.background_image, (x, y))
            else: self.pygame_surface.blit(self.background_image, (0, 0))
        else: self.pygame_surface.fill(self.room_data['settings'].get('background_color', (0,0,0)))
            
        if self.tileset_for_pygame:
            tile_layer = self.get_or_create_tile_layer()
            ts_image = self.tileset_for_pygame['pygame_image']; tw = self.tileset_for_pygame['tile_width']; th = self.tileset_for_pygame['tile_height']
            ts_width_in_tiles = ts_image.get_width() // tw
            for r, row_data in enumerate(tile_layer['tiles']):
                for c, tile_id in enumerate(row_data):
                    if tile_id != -1:
                        tile_x = (tile_id % ts_width_in_tiles) * tw; tile_y = (tile_id // ts_width_in_tiles) * th
                        self.pygame_surface.blit(ts_image, (c * self.grid_size, r * self.grid_size), (tile_x, tile_y, tw, th))

        grid_surface = pygame.Surface((self.canvas_width, self.canvas_height), pygame.SRCALPHA); grid_color = (100, 100, 100, 128)
        for x in range(0, self.canvas_width, self.grid_size): pygame.draw.line(grid_surface, grid_color, (x, 0), (x, self.canvas_height))
        for y in range(0, self.canvas_height, self.grid_size): pygame.draw.line(grid_surface, grid_color, (0, y), (self.canvas_width, y))
        self.pygame_surface.blit(grid_surface, (0, 0))

        for instance_data in self.room_data.get('instances', []):
            obj_name, x, y = instance_data.get('object'), instance_data.get('x', 0), instance_data.get('y', 0)
            if sprite_image := self.sprite_cache.get(obj_name): self.pygame_surface.blit(sprite_image, (x, y))
        
        raw_pixels = pygame.image.tostring(self.pygame_surface, 'RGB'); pil_image = Image.frombytes('RGB', (self.canvas_width, self.canvas_height), raw_pixels); tk_photo = ImageTk.PhotoImage(pil_image)
        self.pygame_canvas_widget.create_image(0, 0, image=tk_photo, anchor="nw"); self.pygame_canvas_widget.image = tk_photo
        self.after(16, self.update_pygame_canvas)

    def load_assets(self):
        object_names_in_room = {inst['object'] for inst in self.room_data.get('instances', [])}
        for obj_name in object_names_in_room:
            for obj_res in self.project_data['resources']['objects']:
                if obj_res['name'] == obj_name:
                    try:
                        with open(os.path.join(self.master.project_root, obj_res['definition_file']), 'r') as f: obj_data = json.load(f)
                        if sprite_name := obj_data.get('sprite'):
                            for sprite_res in self.project_data['resources']['sprites']:
                                if sprite_res['name'] == sprite_name:
                                    full_sprite_path = os.path.join(self.master.project_root, sprite_res['path'])
                                    self.sprite_cache[obj_name] = pygame.image.load(full_sprite_path).convert_alpha()
                                    break
                    except Exception as e: print(f"Error loading sprite for {obj_name}: {e}")
                    break
        self.on_bg_image_selected()
        tile_layer = self.get_or_create_tile_layer()
        if tileset_name := tile_layer.get('tileset'):
            for ts_info in self.project_data['resources'].get('tilesets', []):
                if ts_info['name'] == tileset_name:
                    self.tileset_for_ui = ts_info
                    full_path = os.path.join(self.master.project_root, ts_info['path'])
                    try:
                        pil_img = Image.open(full_path)
                        self.tileset_canvas.config(width=pil_img.width, height=pil_img.height)
                        self.tileset_for_ui['photo_image'] = ImageTk.PhotoImage(pil_img)
                        self.tileset_canvas.create_image(0, 0, image=self.tileset_for_ui['photo_image'], anchor="nw", tags="image")
                        self.tileset_for_pygame = ts_info.copy()
                        self.tileset_for_pygame['pygame_image'] = pygame.image.load(full_path).convert_alpha()
                    except Exception as e: print(f"Error loading tileset for UI: {e}")
                    break

    def save_and_close(self):
        self.room_data['settings']['background_image'] = self.bg_image_var.get(); self.room_data['settings']['background_mode'] = self.bg_mode_var.get()
        self.room_data['settings']['background_scroll_x'] = self.bg_scroll_x_var.get(); self.room_data['settings']['background_scroll_y'] = self.bg_scroll_y_var.get()
        self.room_data['settings']['width'] = self.room_width_var.get(); self.room_data['settings']['height'] = self.room_height_var.get()
        try:
            with open(self.room_file_path, 'w') as f: json.dump(self.room_data, f, indent=4, sort_keys=True)
            self.master.refresh_project_data(); self.on_close()
        except Exception as e: messagebox.showerror("Save Error", f"Could not save room: {e}", parent=self)
    
    def on_tab_changed(self, event): self.edit_mode = self.notebook.tab(self.notebook.select(), "text")
    def on_tileset_click(self, event):
        if not self.tileset_for_ui: return
        tw, th = self.tileset_for_ui['tile_width'], self.tileset_for_ui['tile_height']
        col, row = event.x // tw, event.y // th
        self.tileset_canvas.delete("highlight")
        x1, y1, x2, y2 = col * tw, row * th, (col + 1) * tw, (row + 1) * th
        self.tileset_canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2, tags="highlight")
        self.active_tile_id = (row * (self.tileset_canvas.winfo_width() // tw)) + col
    def on_object_selected(self, event):
        selection = self.object_listbox.curselection()
        self.active_object_name = self.object_listbox.get(selection[0]) if selection else None
    
    def on_mouse_drag(self, event):
        world_x, world_y = self.pygame_canvas_widget.canvasx(event.x), self.pygame_canvas_widget.canvasy(event.y)
        if 0 <= world_x < self.canvas_width and 0 <= world_y < self.canvas_height:
            grid_x, grid_y = int(world_x // self.grid_size) * self.grid_size, int(world_y // self.grid_size) * self.grid_size
            if self.edit_mode == "Objects" and self.active_object_name: self.place_object(grid_x, grid_y)
            elif self.edit_mode == "Tiles": self.place_tile(grid_x, grid_y)
            
    def on_mouse_drag_right(self, event):
        world_x, world_y = self.pygame_canvas_widget.canvasx(event.x), self.pygame_canvas_widget.canvasy(event.y)
        if 0 <= world_x < self.canvas_width and 0 <= world_y < self.canvas_height:
            grid_x, grid_y = int(world_x // self.grid_size) * self.grid_size, int(world_y // self.grid_size) * self.grid_size
            if self.edit_mode == "Objects": self.remove_object_at_pos(grid_x, grid_y)
            elif self.edit_mode == "Tiles": self.place_tile(grid_x, grid_y, empty=True)
            
    def place_object(self, x, y):
        self.remove_object_at_pos(x, y); self.room_data['instances'].append({"object": self.active_object_name, "x": x, "y": y})
    def remove_object_at_pos(self, x, y):
        target_rect = pygame.Rect(x, y, self.grid_size, self.grid_size); instance_to_remove = None
        for inst in self.room_data['instances']:
            if (sprite := self.sprite_cache.get(inst['object'])) and target_rect.colliderect(sprite.get_rect(topleft=(inst['x'], inst['y']))):
                instance_to_remove = inst; break
        if instance_to_remove: self.room_data['instances'].remove(instance_to_remove)
        
    def place_tile(self, x, y, empty=False):
        tile_layer = self.get_or_create_tile_layer()
        col, row = x // self.grid_size, y // self.grid_size
        if 0 <= row < len(tile_layer['tiles']) and 0 <= col < len(tile_layer['tiles'][row]):
            tile_id_to_place = -1 if empty else self.active_tile_id
            tile_layer['tiles'][row][col] = tile_id_to_place