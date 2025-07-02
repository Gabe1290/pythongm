# ide/main_ide.py
import tkinter as tk
from tkinter import ttk
import json
import os
import subprocess
import sys # sys.executable will resolve to an absolute path like
           # /usr/bin/python3.11 or C:\Python311\python.exe.
           # There is no guesswork
from .object_editor import ObjectEditorWindow

class MainIDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("My GameMaker Clone")
        self.geometry("800x600")

        # --- PATH FIXES ---
        # The project root is the current working directory, since we run from there.
        self.project_root = os.getcwd()
        self.project_file_path = os.path.join(self.project_root, "my_game.json")

        self.project_data = None
        self.tree_item_map = {}

        # ... (rest of the __init__ method is the same) ...
        self.paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        self.tree_frame = ttk.Frame(self.paned_window, width=200)
        self.paned_window.add(self.tree_frame, weight=1)
        self.resource_tree = ttk.Treeview(self.tree_frame)
        self.resource_tree.pack(fill=tk.BOTH, expand=True)
        self.resource_tree.bind("<Double-1>", self.on_item_double_click)
        self.workspace_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.workspace_frame, weight=4)
        self.create_menu()
        self.load_project()
    
    # ... (create_menu is unchanged) ...
    def create_menu(self):
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Project...", command=self.load_project)
        file_menu.add_command(label="Save Project", command=self.save_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        run_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Run Game", command=self.run_game)

    def load_project(self):
        try:
            with open(self.project_file_path, 'r') as f:
                self.project_data = json.load(f)
            self.populate_resource_tree()
        except FileNotFoundError:
            # More helpful error message
            messagebox.showerror("Error", f"Project file not found!\n\nExpected at: {self.project_file_path}\n\nMake sure you are running the IDE from the project's root directory.")
            self.quit()

    def refresh_project_data(self):
        self.load_project()

    def populate_resource_tree(self):
        # ... (this method is unchanged) ...
        for i in self.resource_tree.get_children(): self.resource_tree.delete(i)
        self.tree_item_map.clear()
        if not self.project_data: return
        resource_map = {
            "Sprites": self.project_data['resources']['sprites'],
            "Objects": self.project_data['resources']['objects'],
            "Rooms": self.project_data['resources']['rooms'],
        }
        for category, resources in resource_map.items():
            category_id = self.resource_tree.insert("", "end", text=category, open=True)
            for resource in resources:
                item_id = self.resource_tree.insert(category_id, "end", text=resource['name'])
                self.tree_item_map[item_id] = resource
    
    def save_project(self):
        # ... (this method is unchanged) ...
        with open(self.project_file_path, 'w') as f:
            json.dump(self.project_data, f, indent=2)
        print("Project saved!")

    def run_game(self):
        # --- PATH FIX ---
        # The runner is just "runner.py" relative to the project root.
        runner_path = os.path.join(self.project_root, "runner.py")
        print(f"Attempting to run game with: python {runner_path}")
        # We need to tell the subprocess what its working directory should be.
        subprocess.Popen([sys.executable, "runner.py"], cwd=self.project_root)

    def on_item_double_click(self, event):
        """
        Handles the double-click event on the resource tree.
        This is the robust version that identifies the item under the cursor.
        """
        # Identify the item ID directly from the click's y-coordinate
        item_id = self.resource_tree.identify_row(event.y)

        # If the click was not on an item, do nothing.
        if not item_id:
            return

        # Optional but good for UX: ensure the clicked item is selected
        self.resource_tree.selection_set(item_id)

        # Check if the item has a parent (i.e., it's not a top-level category)
        parent_id = self.resource_tree.parent(item_id)
        if not parent_id:
            return # User double-clicked on "Sprites", "Objects", etc.

        category = self.resource_tree.item(parent_id, "text")

        if category == "Objects":
            resource_info = self.tree_item_map.get(item_id)
            if resource_info and 'definition_file' in resource_info:
                # This part was correct, the issue was getting the item_id
                obj_file_path = os.path.join(self.project_root, resource_info['definition_file'])
                # Open the editor window!
                ObjectEditorWindow(self, obj_file_path, self.project_data)

        # You could add elif blocks here for other editors, like a Room Editor
        # elif category == "Rooms":
        #     print("Room editor would open here.")

if __name__ == "__main__":
    app = MainIDE()
    app.mainloop()
