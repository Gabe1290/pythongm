# ide/object_editor.py
# FINAL WORKING VERSION

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

# These top-level definitions are unchanged and correct.
KEYBOARD_KEYS = ["LEFT", "RIGHT", "UP", "DOWN", "SPACE"]
KNOWN_ACTIONS = {
    "move_fixed": [{"name": "direction", "type": "number", "default": 0}, {"name": "speed", "type": "number", "default": 4}],
    "check_keyboard": [{"name": "key", "type": "dropdown", "options": KEYBOARD_KEYS}, {"name": "result_action_list", "type": "string", "default": "action_name"}]
}
KNOWN_EVENTS = ["create", "step"]

class AddEventDialog(tk.Toplevel):
    def __init__(self, master, available_events):
        super().__init__(master)
        self.transient(master); self.title("Add Event"); self.geometry("250x300"); self.result = None
        ttk.Label(self, text="Select an event to add:").pack(pady=10)
        self.listbox = tk.Listbox(self); self.listbox.pack(fill=tk.BOTH, expand=True, padx=10)
        for event in sorted(available_events): self.listbox.insert(tk.END, event)
        btn_frame = ttk.Frame(self, padding=5); btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)
        self.protocol("WM_DELETE_WINDOW", self.destroy); self.wait_visibility(); self.grab_set(); self.wait_window(self)
    def on_ok(self):
        s = self.listbox.curselection();
        if s: self.result = self.listbox.get(s[0])
        self.destroy()

class AddActionDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.transient(master); self.title("Add Action"); self.result = None; self.param_widgets = {}
        top_frame = ttk.Frame(self, padding=10); top_frame.pack(fill=tk.X)
        ttk.Label(top_frame, text="Action Type:").pack(side=tk.LEFT, padx=(0, 10))
        self.action_type_var = tk.StringVar()
        self.action_type_combo = ttk.Combobox(top_frame, textvariable=self.action_type_var, values=sorted(KNOWN_ACTIONS.keys()), state="readonly")
        self.action_type_combo.pack(fill=tk.X, expand=True); self.action_type_combo.bind("<<ComboboxSelected>>", self.on_action_type_selected)
        self.params_frame = ttk.LabelFrame(self, text="Parameters", padding=10); self.params_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        btn_frame = ttk.Frame(self, padding=(10, 0)); btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        self.protocol("WM_DELETE_WINDOW", self.destroy); self.wait_visibility(); self.grab_set(); self.wait_window(self)
    def on_action_type_selected(self, event):
        for widget in self.params_frame.winfo_children(): widget.destroy()
        self.param_widgets = {}; action_type = self.action_type_var.get(); params = KNOWN_ACTIONS.get(action_type, [])
        for i, p_def in enumerate(params):
            n = p_def["name"]; l = ttk.Label(self.params_frame, text=f"{n}:"); l.grid(row=i, column=0, sticky=tk.W, pady=2)
            v = tk.StringVar(value=p_def.get("default", "")); w = None
            if p_def["type"] in ["number", "string"]: w = ttk.Entry(self.params_frame, textvariable=v)
            elif p_def["type"] == "dropdown": w = ttk.Combobox(self.params_frame, textvariable=v, values=p_def.get("options", []), state="readonly")
            if w: w.grid(row=i, column=1, sticky=tk.EW, pady=2); self.param_widgets[n] = v
        self.params_frame.columnconfigure(1, weight=1)
    def on_ok(self):
        self.result = {"action": self.action_type_var.get()}
        for n, v in self.param_widgets.items():
            val = v.get()
            try:
                p_def = next(p for p in KNOWN_ACTIONS[self.result["action"]] if p["name"] == n)
                if p_def["type"] == "number": val = int(val) if "." not in val else float(val)
            except (ValueError, StopIteration, KeyError): pass
            self.result[n] = val
        self.destroy()

class ObjectEditorWindow(tk.Toplevel):
    def __init__(self, master, object_file_path, project_data):
        super().__init__(master)
        self.transient(master)
        self.object_file_path = object_file_path
        self.project_data = project_data
        self.object_data = None
        self.param_vars = {}

        # --- THE CORE FIX: VARIABLES TO STORE THE SELECTION STATE ---
        self.selected_event_index = None
        self.selected_action_index = None

        self.title(f"Object Editor - {os.path.basename(object_file_path)}")
        self.geometry("750x550")
        self.load_object_data()
        self.create_widgets()
        self.populate_forms()
        self.after(10, self.grab_set)

    def load_object_data(self):
        try:
            with open(self.object_file_path, 'r') as f:
                self.object_data = json.load(f)
            if "events" not in self.object_data: self.object_data["events"] = {}
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", f"Failed to load object data: {e}", parent=self); self.destroy()

    def create_widgets(self):
        top_frame = ttk.Frame(self, padding="10"); top_frame.pack(fill=tk.X)
        ttk.Label(top_frame, text="Object Name:").grid(row=0, column=0, sticky=tk.W)
        self.name_var = tk.StringVar(); ttk.Entry(top_frame, textvariable=self.name_var).grid(row=0, column=1, sticky=tk.EW)
        ttk.Label(top_frame, text="Sprite:").grid(row=1, column=0, sticky=tk.W, pady=(5,0))
        sprite_names = [s['name'] for s in self.project_data['resources']['sprites']]
        self.sprite_var = tk.StringVar()
        self.sprite_combobox = ttk.Combobox(top_frame, textvariable=self.sprite_var, values=sprite_names, state="readonly")
        self.sprite_combobox.grid(row=1, column=1, sticky=tk.EW); top_frame.columnconfigure(1, weight=1)
        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL); main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        events_frame = ttk.LabelFrame(main_pane, text="Events", padding="5"); main_pane.add(events_frame, weight=1)
        self.events_listbox = tk.Listbox(events_frame); self.events_listbox.pack(fill=tk.BOTH, expand=True)
        self.events_listbox.bind("<ButtonRelease-1>", self.on_event_selected)
        event_buttons_frame = ttk.Frame(events_frame); event_buttons_frame.pack(fill=tk.X, pady=(5,0))
        ttk.Button(event_buttons_frame, text="Add Event...", command=self.add_event).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(event_buttons_frame, text="Remove Event", command=self.remove_event).pack(side=tk.LEFT, expand=True, fill=tk.X)
        actions_pane_frame = ttk.Frame(main_pane); main_pane.add(actions_pane_frame, weight=2)
        actions_frame = ttk.LabelFrame(actions_pane_frame, text="Actions for Selected Event", padding="5"); actions_frame.pack(fill=tk.BOTH, expand=True)
        self.actions_listbox = tk.Listbox(actions_frame); self.actions_listbox.pack(fill=tk.BOTH, expand=True)
        self.actions_listbox.bind("<ButtonRelease-1>", self.on_action_selected)
        action_buttons_frame = ttk.Frame(actions_frame); action_buttons_frame.pack(fill=tk.X, pady=(5,0))
        self.add_action_button = ttk.Button(action_buttons_frame, text="Add Action...", command=self.add_action, state="disabled")
        self.add_action_button.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.remove_action_button = ttk.Button(action_buttons_frame, text="Remove Action", command=self.remove_action, state="disabled")
        self.remove_action_button.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.params_frame = ttk.LabelFrame(actions_pane_frame, text="Action Parameters", padding="10"); self.params_frame.pack(fill=tk.X, pady=(5,0))
        bottom_button_frame = ttk.Frame(self, padding="10"); bottom_button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(bottom_button_frame, text="Save & Close", command=self.save_and_close).pack(side=tk.RIGHT)
        ttk.Button(bottom_button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def populate_forms(self):
        self.name_var.set(self.object_data.get("name", "")); self.sprite_var.set(self.object_data.get("sprite", ""))
        self.events_listbox.delete(0, tk.END)
        for event_name in sorted(self.object_data.get("events", {})):
            self.events_listbox.insert(tk.END, event_name)
        self.update_button_states()

    def on_event_selected(self, event):
        selection = self.events_listbox.curselection()
        if not selection: return
        self.selected_event_index = selection[0]
        self.selected_action_index = None # Reset action selection

        self.actions_listbox.delete(0, tk.END)
        self._clear_param_widgets()

        selected_event_name = self.events_listbox.get(self.selected_event_index)
        for action_data in self.object_data["events"].get(selected_event_name, []):
            action_type = action_data.get("action", "unknown")
            params = ", ".join(f"{k}: {v}" for k, v in action_data.items() if k != "action")
            self.actions_listbox.insert(tk.END, f"{action_type} ({params})")
        self.update_button_states()

    def on_action_selected(self, event):
        selection = self.actions_listbox.curselection()
        if not selection: return
        self.selected_action_index = selection[0]

        self._clear_param_widgets()
        event_name = self.events_listbox.get(self.selected_event_index)
        action_data = self.object_data["events"][event_name][self.selected_action_index]
        action_def = KNOWN_ACTIONS.get(action_data.get("action"))
        if action_def:
            self._build_param_ui(action_def, action_data)
        self.update_button_states()

    def remove_action(self):
        # Use the stored indices, which are immune to focus changes.
        if self.selected_event_index is None or self.selected_action_index is None:
            return

        if messagebox.askyesno("Confirm Removal", "Are you sure you want to remove this action?"):
            event_name = self.events_listbox.get(self.selected_event_index)

            # Delete from data
            del self.object_data["events"][event_name][self.selected_action_index]

            # Delete from UI
            self.actions_listbox.delete(self.selected_action_index)

            # Reset state
            self.selected_action_index = None
            self._clear_param_widgets()
            self.update_button_states()

    def update_button_states(self):
        self.add_action_button.config(state="normal" if self.selected_event_index is not None else "disabled")
        self.remove_action_button.config(state="normal" if self.selected_action_index is not None else "disabled")

    def _clear_param_widgets(self):
        for widget in self.params_frame.winfo_children(): widget.destroy()
        self.param_vars.clear()

    # --- Other methods are largely unchanged but included for completeness ---

    def _build_param_ui(self, action_def, action_data):
        for i, p_def in enumerate(action_def):
            # --- THE FIX IS HERE ---
            # OLD, BUGGY LINE:
            # n, l = p_def["name"], ttk.Label(self.params_frame, text=f"{n}:"); l.grid(row=i, column=0, sticky=tk.W, pady=2)

            # NEW, CORRECTED LINES:
            name = p_def["name"]
            label = ttk.Label(self.params_frame, text=f"{name}:")
            label.grid(row=i, column=0, sticky=tk.W, pady=2)

            current_value = action_data.get(name, p_def.get("default", ""))
            var = tk.StringVar(value=str(current_value))
            widget = None

            if p_def["type"] in ["number", "string"]:
                widget = ttk.Entry(self.params_frame, textvariable=var)
            elif p_def["type"] == "dropdown":
                widget = ttk.Combobox(self.params_frame, textvariable=var, values=p_def.get("options", []), state="readonly")

            if widget:
                widget.grid(row=i, column=1, sticky=tk.EW, pady=2)
                self.param_vars[name] = var

        self.params_frame.columnconfigure(1, weight=1)

    def _update_action_from_params(self):
        if self.selected_event_index is None or self.selected_action_index is None: return
        event_name = self.events_listbox.get(self.selected_event_index)
        action_data = self.object_data["events"][event_name][self.selected_action_index]
        for n, v in self.param_vars.items():
            val = v.get()
            try:
                p_def = next(p for p in KNOWN_ACTIONS[action_data["action"]] if p["name"] == n)
                if p_def["type"] == "number": val = int(val) if "." not in val else float(val)
            except (ValueError, StopIteration, KeyError): pass
            action_data[n] = val

    def add_event(self):
        current = set(self.object_data.get("events", {}).keys()); available = set(KNOWN_EVENTS) - current
        if not available: messagebox.showinfo("No More Events", "All available events have been added.", parent=self); return
        dialog = AddEventDialog(self, available); new_event = dialog.result
        if new_event:
            self.object_data["events"][new_event] = []; self.populate_forms()
            for i, item in enumerate(self.events_listbox.get(0, tk.END)):
                if item == new_event: self.events_listbox.selection_set(i); self.on_event_selected(None); break

    def remove_event(self):
        if self.selected_event_index is None: return
        event_name = self.events_listbox.get(self.selected_event_index)
        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove the '{event_name}' event?"):
            del self.object_data["events"][event_name]; self.populate_forms()
            self.actions_listbox.delete(0, tk.END); self._clear_param_widgets()
            self.selected_event_index = None; self.selected_action_index = None

    def add_action(self):
        self._update_action_from_params()
        if self.selected_event_index is None: return
        dialog = AddActionDialog(self); new_action = dialog.result
        if new_action:
            event_name = self.events_listbox.get(self.selected_event_index)
            self.object_data["events"][event_name].append(new_action)
            self.on_event_selected(None) # Refresh list
            new_idx = self.actions_listbox.size() - 1
            if new_idx >= 0: self.actions_listbox.selection_set(new_idx); self.on_action_selected(None)

    def save_and_close(self):
        self._update_action_from_params()
        self.object_data['name'] = self.name_var.get(); self.object_data['sprite'] = self.sprite_var.get()
        try:
            with open(self.object_file_path, 'w') as f: json.dump(self.object_data, f, indent=2, sort_keys=True)
            self.master.refresh_project_data(); self.destroy()
        except Exception as e: messagebox.showerror("Save Error", f"Could not save the file: {e}", parent=self)
