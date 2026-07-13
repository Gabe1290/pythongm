import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import json
import os
import subprocess
import sys
import shutil
from PIL import Image, ImageTk
from .object_editor import ObjectEditorWindow
from .room_editor import RoomEditorWindow

class MainIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("My GameMaker Clone")
        self.geometry("800x600")
        self.project_root = os.getcwd()
        self.project_file_path = os.path.join(self.project_root, "my_game.json")
        self.project_data = None
        self.tree_item_map = {}
        
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        self.tree_frame = ttk.Frame(self.paned_window, width=250)
        self.paned_window.add(self.tree_frame, weight=1)
        
        self.resource_tree = ttk.Treeview(self.tree_frame)
        self.resource_tree.pack(fill=tk.BOTH, expand=True)
        self.resource_tree.bind("<Double-1>", self.on_item_double_click)
        self.resource_tree.bind("<<TreeviewSelect>>", self.on_resource_selected)
        
        resource_button_frame = ttk.Frame(self.tree_frame)
        resource_button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=2)
        ttk.Button(resource_button_frame, text="Add", command=self.add_resource).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(resource_button_frame, text="Remove", command=self.remove_resource).pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.workspace_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.workspace_frame, weight=4)
        
        self.create_menu()
        self.load_project()
        
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def create_menu(self):
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Project", command=self.save_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        
        run_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Game", command=self.run_game)
        
        # --- NEW: Add this for debugging ---
        run_menu.add_separator()
        run_menu.add_command(label="Test Run Command", command=self.test_run_command)

    def test_run_command(self):
        """A simple test to see if menu commands are working at all."""
        print("DEBUG: Test Run Command was called.")
        messagebox.showinfo("Test", "The menu command is working!")

    def run_game(self):
        print("--- RUN GAME INITIATED ---")
        try:
            # Step 1: Check if project root exists
            print(f"DEBUG: Project root is: {self.project_root}")
            if not os.path.isdir(self.project_root):
                messagebox.showerror("Run Error", f"Project root directory not found:\n{self.project_root}")
                return

            # Step 2: Check if runner.py exists
            runner_path = os.path.join(self.project_root, "runner.py")
            print(f"DEBUG: Runner path is: {runner_path}")
            if not os.path.isfile(runner_path):
                messagebox.showerror("Run Error", f"Cannot find runner.py at:\n{runner_path}")
                return

            # Step 3: Check Python executable
            python_executable = sys.executable
            print(f"DEBUG: Python executable is: {python_executable}")
            if not os.path.isfile(python_executable):
                 messagebox.showerror("Run Error", f"Python executable not found at:\n{python_executable}")
                 return

            # Step 4: Attempt to launch the subprocess
            print(f"DEBUG: Launching subprocess with Popen...")
            subprocess.Popen([python_executable, "runner.py"], cwd=self.project_root)
            print("--- SUBPROCESS LAUNCHED (No immediate errors) ---")

        except Exception as e:
            # Catch any other unexpected error
            print(f"!!! UNEXPECTED ERROR IN run_game: {e} !!!")
            messagebox.showerror("Run Error", f"An unexpected error occurred while trying to run the game.\n\nError: {e}")

    def load_project(self):
        try:
            with open(self.project_file_path, 'r') as f:
                self.project_data = json.load(f)
            self.populate_resource_tree()
        except FileNotFoundError:
            messagebox.showerror("Error", f"Project file not found!\n\nExpected at: {self.project_file_path}")
            self.destroy()

    def refresh_project_data(self):
        self.load_project()

    def populate_resource_tree(self):
        for i in self.resource_tree.get_children(): self.resource_tree.delete(i)
        self.tree_item_map.clear()
        if not self.project_data: return
        resource_map = {
            "Sprites": self.project_data['resources'].get('sprites', []),
            "Backgrounds": self.project_data['resources'].get('backgrounds', []),
            "Tilesets": self.project_data['resources'].get('tilesets', []),
            "Objects": self.project_data['resources'].get('objects', []),
            "Rooms": self.project_data['resources'].get('rooms', []),
        }
        for category, resources in resource_map.items():
            category_id = self.resource_tree.insert("", "end", text=category, open=True)
            if resources:
                for resource in resources:
                    item_id = self.resource_tree.insert(category_id, "end", text=resource['name'])
                    self.tree_item_map[item_id] = resource

    def save_project(self):
        with open(self.project_file_path, 'w') as f:
            json.dump(self.project_data, f, indent=4, sort_keys=True)
        print("Project saved!")

    def on_resource_selected(self, event):
        for widget in self.workspace_frame.winfo_children(): widget.destroy()
        selection = self.resource_tree.selection()
        if not selection: return
        item_id = selection[0]; parent_id = self.resource_tree.parent(item_id)
        if not parent_id: return
        category = self.resource_tree.item(parent_id, "text"); resource_info = self.tree_item_map.get(item_id)
        if not resource_info: return

        if category in ["Sprites", "Backgrounds", "Tilesets"]:
            full_path = os.path.join(self.project_root, resource_info.get('path', ''))
            if os.path.exists(full_path):
                try:
                    preview_frame = ttk.Frame(self.workspace_frame, padding=10); preview_frame.pack(fill=tk.BOTH, expand=True)
                    img = Image.open(full_path)
                    info_text = f"Name: {resource_info['name']}\nPath: {resource_info['path']}\nDimensions: {img.width} x {img.height}"
                    ttk.Label(preview_frame, text=info_text, justify=tk.LEFT).pack(anchor="nw", pady=5)
                    img_label = ttk.Label(preview_frame); img_label.pack(pady=10)
                    img.thumbnail((400, 400), Image.Resampling.LANCZOS); photo_img = ImageTk.PhotoImage(img)
                    img_label.config(image=photo_img); img_label.image = photo_img
                except Exception as e: ttk.Label(self.workspace_frame, text=f"Error loading preview: {e}").pack()
        elif category == "Objects":
            try:
                with open(os.path.join(self.project_root, resource_info['definition_file']), 'r') as f: obj_data = json.load(f)
                preview_text = f"Name: {obj_data.get('name', 'N/A')}\nSprite: {obj_data.get('sprite', 'None')}\nSolid: {obj_data.get('solid', False)}\n\nEvents:\n"
                for event_name in obj_data.get('events', {}): preview_text += f"  - {event_name}\n"
                ttk.Label(self.workspace_frame, text=preview_text, justify=tk.LEFT, font=("Courier", 10), padding=10).pack(anchor="nw")
            except Exception as e: ttk.Label(self.workspace_frame, text=f"Error loading object data: {e}").pack()
        else: ttk.Label(self.workspace_frame, text=f"Selected: {resource_info['name']}\n(No preview available)", padding=10).pack()

    def on_item_double_click(self, event):
        item_id = self.resource_tree.identify_row(event.y)
        if not item_id: return
        self.resource_tree.selection_set(item_id); parent_id = self.resource_tree.parent(item_id)
        if not parent_id: return
        category = self.resource_tree.item(parent_id, "text"); resource_info = self.tree_item_map.get(item_id)
        if not resource_info: return
        if category == "Objects":
            ObjectEditorWindow(self, os.path.join(self.project_root, resource_info['definition_file']), self.project_data)
        elif category == "Rooms":
            RoomEditorWindow(self, os.path.join(self.project_root, resource_info['definition_file']), self.project_data)

    def _add_image_resource(self, category_name, resource_key, name_prefix, title):
        filepath = filedialog.askopenfilename(title=title, filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")], parent=self)
        if not filepath: return None
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        new_name = simpledialog.askstring(f"New {category_name}", f"Enter name:", initialvalue=f"{name_prefix}_{base_name}", parent=self)
        if not new_name or not new_name.strip(): return None
        dest_path = os.path.join("sprites", f"{new_name}.png")
        if os.path.exists(os.path.join(self.project_root, dest_path)): messagebox.showerror("Error", f"File '{new_name}.png' already exists."); return None
        shutil.copy(filepath, os.path.join(self.project_root, dest_path))
        new_resource_data = {"name": new_name, "path": dest_path}
        if resource_key == 'tilesets': new_resource_data.update({"tile_width": 32, "tile_height": 32})
        if resource_key not in self.project_data['resources']: self.project_data['resources'][resource_key] = []
        self.project_data['resources'][resource_key].append(new_resource_data); return True

    def add_resource(self):
        selection = self.resource_tree.selection()
        if not selection: messagebox.showwarning("No Selection", "Please select a category."); return
        item_id = selection[0]
        category = self.resource_tree.item(item_id, "text") if self.resource_tree.parent(item_id) == "" else self.resource_tree.item(self.resource_tree.parent(item_id), "text")
        success = False
        if category == "Sprites": success = self._add_image_resource("Sprite", "sprites", "spr", "Select Sprite")
        elif category == "Backgrounds": success = self._add_image_resource("Background", "backgrounds", "bg", "Select Background")
        elif category == "Tilesets": success = self._add_image_resource("Tileset", "tilesets", "ts", "Select Tileset")
        elif category == "Objects":
            new_name = simpledialog.askstring("New Object", "Enter object name:", parent=self)
            if new_name and new_name.strip():
                obj_def_path = os.path.join("objects", f"{new_name}.json")
                if os.path.exists(os.path.join(self.project_root, obj_def_path)): messagebox.showerror("Error", f"Object '{new_name}' already exists."); return
                new_object_data = {"name": new_name, "sprite": "", "solid": False, "events": {}, "action_lists": {}};
                with open(os.path.join(self.project_root, obj_def_path), 'w') as f: json.dump(new_object_data, f, indent=4)
                if 'objects' not in self.project_data['resources']: self.project_data['resources']['objects'] = []
                self.project_data['resources']['objects'].append({"name": new_name, "definition_file": obj_def_path}); success = True
        elif category == "Rooms":
            new_name = simpledialog.askstring("New Room", "Enter room name:", parent=self)
            if new_name and new_name.strip():
                room_def_path = os.path.join("rooms", f"{new_name}.json")
                if os.path.exists(os.path.join(self.project_root, room_def_path)): messagebox.showerror("Error", f"Room '{new_name}' already exists."); return
                new_room_data = {"name": new_name, "settings": {"background_color": [100, 100, 100], "width": 800, "height": 600}, "instances": []};
                with open(os.path.join(self.project_root, room_def_path), 'w') as f: json.dump(new_room_data, f, indent=4)
                if 'rooms' not in self.project_data['resources']: self.project_data['resources']['rooms'] = []
                self.project_data['resources']['rooms'].append({"name": new_name, "definition_file": room_def_path}); success = True
        if success: self.save_project(); self.refresh_project_data()

    def remove_resource(self):
        selection = self.resource_tree.selection()
        if not selection: messagebox.showwarning("No Selection", "Please select a resource."); return
        item_id = selection[0]
        if self.resource_tree.parent(item_id) == "": messagebox.showwarning("Invalid Selection", "Cannot remove a category folder."); return
        parent_id, category = self.resource_tree.parent(item_id), self.resource_tree.item(parent_id, "text")
        resource_name, resource_info = self.resource_tree.item(item_id, "text"), self.tree_item_map.get(item_id)
        if not resource_info or not messagebox.askyesno("Confirm Removal", f"Permanently delete '{resource_name}'?"): return
        
        resource_keys = {"Objects": "objects", "Rooms": "rooms", "Sprites": "sprites", "Backgrounds": "backgrounds", "Tilesets": "tilesets"}
        path_keys = {"Objects": "definition_file", "Rooms": "definition_file", "Sprites": "path", "Backgrounds": "path", "Tilesets": "path"}
        
        resource_key = resource_keys.get(category)
        path_key = path_keys.get(category)

        if resource_key and path_key:
            file_to_delete = os.path.join(self.project_root, resource_info[path_key])
            if os.path.exists(file_to_delete):
                os.remove(file_to_delete)
            
            if resource_key in self.project_data['resources']:
                self.project_data['resources'][resource_key] = [
                    res for res in self.project_data['resources'][resource_key] 
                    if res.get('name') != resource_name
                ]
            
            self.save_project()
            self.refresh_project_data()

if __name__ == "__main__":
    app = MainIDE()
    app.mainloop()