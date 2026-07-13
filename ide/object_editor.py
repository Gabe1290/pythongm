import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from PIL import Image, ImageTk

# --- MASTER DATA & DIALOGS (UNCHANGED) ---
KEYBOARD_KEYS = ["LEFT", "RIGHT", "UP", "DOWN", "SPACE"]
KNOWN_ACTIONS = {"move_fixed": [{"name": "direction", "type": "number", "default": 0}, {"name": "speed", "type": "number", "default": 4}], "check_keyboard": [{"name": "key", "type": "dropdown", "options": KEYBOARD_KEYS}, {"name": "result_action_list", "type": "string", "default": "action_name"}]}
KNOWN_EVENTS = ["create", "step"]

class AddEventDialog(tk.Toplevel):
    def __init__(self, master, available_events):
        super().__init__(master);self.transient(master);self.title("Add Event");self.geometry("250x300");self.result=None;ttk.Label(self, text="Select an event to add:").pack(pady=10);self.listbox=tk.Listbox(self);self.listbox.pack(fill=tk.BOTH, expand=True, padx=10)
        for event in sorted(available_events): self.listbox.insert(tk.END, event)
        btn_frame=ttk.Frame(self,padding=5);btn_frame.pack(fill=tk.X);ttk.Button(btn_frame,text="OK",command=self.on_ok).pack(side=tk.RIGHT,padx=5);ttk.Button(btn_frame,text="Cancel",command=self.destroy).pack(side=tk.RIGHT);self.protocol("WM_DELETE_WINDOW",self.destroy);self.wait_visibility();self.grab_set();self.wait_window(self)
    def on_ok(self):
        selection=self.listbox.curselection();
        if selection:self.result=self.listbox.get(selection[0])
        self.destroy()

class AddActionDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master);self.transient(master);self.title("Add Action");self.result=None;self.param_widgets={};top_frame=ttk.Frame(self,padding=10);top_frame.pack(fill=tk.X);ttk.Label(top_frame,text="Action Type:").pack(side=tk.LEFT,padx=(0,10));self.action_type_var=tk.StringVar();self.action_type_combo=ttk.Combobox(top_frame,textvariable=self.action_type_var,values=sorted(KNOWN_ACTIONS.keys()),state="readonly");self.action_type_combo.pack(fill=tk.X,expand=True);self.action_type_combo.bind("<<ComboboxSelected>>",self.on_action_type_selected);self.params_frame=ttk.LabelFrame(self,text="Parameters",padding=10);self.params_frame.pack(fill=tk.BOTH,expand=True,padx=10,pady=5);btn_frame=ttk.Frame(self,padding=(10,0));btn_frame.pack(fill=tk.X,side=tk.BOTTOM);ttk.Button(btn_frame,text="OK",command=self.on_ok).pack(side=tk.RIGHT);ttk.Button(btn_frame,text="Cancel",command=self.destroy).pack(side=tk.RIGHT,padx=5);self.protocol("WM_DELETE_WINDOW",self.destroy);self.wait_visibility();self.grab_set();self.wait_window(self)
    def on_action_type_selected(self, event):
        for widget in self.params_frame.winfo_children():widget.destroy()
        self.param_widgets={};action_type=self.action_type_var.get();params=KNOWN_ACTIONS.get(action_type,[])
        for i,param_def in enumerate(params):
            name=param_def["name"];label=ttk.Label(self.params_frame,text=f"{name}:");label.grid(row=i,column=0,sticky=tk.W,pady=2);var=tk.StringVar(value=param_def.get("default",""));widget=None
            if param_def["type"] in("number","string"):widget=ttk.Entry(self.params_frame,textvariable=var)
            elif param_def["type"]=="dropdown":widget=ttk.Combobox(self.params_frame,textvariable=var,values=param_def.get("options",[]),state="readonly")
            if widget:widget.grid(row=i,column=1,sticky=tk.EW,pady=2);self.param_widgets[name]=var
        self.params_frame.columnconfigure(1,weight=1)
    def on_ok(self):
        self.result={"action":self.action_type_var.get()}
        for name,var in self.param_widgets.items():
            value=var.get()
            try:
                if KNOWN_ACTIONS[self.result["action"]][len(self.result)-1]["type"]=="number":value=float(value)if"."in value else int(value)
            except(ValueError,KeyError,IndexError):pass
            self.result[name]=value
        self.destroy()

class ObjectEditorWindow(tk.Toplevel):
    def __init__(self,master,object_file_path,project_data):
        super().__init__(master);self.transient(master);self.object_file_path=object_file_path;self.project_data=project_data;self.object_data=None;self.param_vars={};self.title(f"Object Editor - {os.path.basename(object_file_path)}");self.geometry("750x550");self.load_object_data();self.create_widgets();self.populate_forms();self.after(10,self.grab_set)
    def load_object_data(self):
        try:
            with open(self.object_file_path,'r')as f:self.object_data=json.load(f)
            if"events"not in self.object_data:self.object_data["events"]={}
            if"action_lists"not in self.object_data:self.object_data["action_lists"]={}
        except(FileNotFoundError,json.JSONDecodeError)as e:messagebox.showerror("Error",f"Failed to load object data: {e}",parent=self);self.destroy()
    def create_widgets(self):
        top_frame=ttk.Frame(self,padding="10");top_frame.pack(fill=tk.X);preview_frame=ttk.LabelFrame(top_frame,text="Preview",width=100,height=100);preview_frame.grid(row=0,column=0,padx=(0,10),sticky="ns");preview_frame.grid_propagate(False);self.preview_label=ttk.Label(preview_frame);self.preview_label.pack(fill=tk.BOTH,expand=True);entries_frame=ttk.Frame(top_frame);entries_frame.grid(row=0,column=1,sticky="nsew");ttk.Label(entries_frame,text="Object Name:").grid(row=0,column=0,sticky=tk.W);self.name_var=tk.StringVar();ttk.Entry(entries_frame,textvariable=self.name_var).grid(row=0,column=1,sticky=tk.EW);ttk.Label(entries_frame,text="Sprite:").grid(row=1,column=0,sticky=tk.W,pady=(5,0));sprite_names=[s['name']for s in self.project_data['resources']['sprites']];self.sprite_var=tk.StringVar();self.sprite_combobox=ttk.Combobox(entries_frame,textvariable=self.sprite_var,values=sprite_names,state="readonly");self.sprite_combobox.grid(row=1,column=1,sticky=tk.EW);self.sprite_combobox.bind("<<ComboboxSelected>>",self.on_sprite_selected);entries_frame.columnconfigure(1,weight=1);top_frame.columnconfigure(1,weight=1);top_frame.rowconfigure(0,weight=1);main_pane=ttk.PanedWindow(self,orient=tk.HORIZONTAL);main_pane.pack(fill=tk.BOTH,expand=True,padx=10,pady=5);events_frame=ttk.LabelFrame(main_pane,text="Events",padding="5");main_pane.add(events_frame,weight=1);self.events_listbox=tk.Listbox(events_frame);self.events_listbox.pack(fill=tk.BOTH,expand=True);self.events_listbox.bind("<<ListboxSelect>>",self.on_event_selected);event_buttons_frame=ttk.Frame(events_frame);event_buttons_frame.pack(fill=tk.X,pady=(5,0));ttk.Button(event_buttons_frame,text="Add Event...",command=self.add_event).pack(side=tk.LEFT,expand=True,fill=tk.X);ttk.Button(event_buttons_frame,text="Remove Event",command=self.remove_event).pack(side=tk.LEFT,expand=True,fill=tk.X);actions_pane_frame=ttk.Frame(main_pane);main_pane.add(actions_pane_frame,weight=2);actions_frame=ttk.LabelFrame(actions_pane_frame,text="Actions for Selected Event",padding="5");actions_frame.pack(fill=tk.BOTH,expand=True);self.actions_listbox=tk.Listbox(actions_frame);self.actions_listbox.pack(fill=tk.BOTH,expand=True);self.actions_listbox.bind("<<ListboxSelect>>",self.on_action_selected);action_buttons_frame=ttk.Frame(actions_frame);action_buttons_frame.pack(fill=tk.X,pady=(5,0));self.add_action_button=ttk.Button(action_buttons_frame,text="Add Action...",command=self.add_action,state="disabled");self.add_action_button.pack(side=tk.LEFT,expand=True,fill=tk.X);self.remove_action_button=ttk.Button(action_buttons_frame,text="Remove Action",command=self.remove_action,state="disabled");self.remove_action_button.pack(side=tk.LEFT,expand=True,fill=tk.X);self.params_frame=ttk.LabelFrame(actions_pane_frame,text="Action Parameters",padding="10");self.params_frame.pack(fill=tk.X,pady=(5,0));bottom_button_frame=ttk.Frame(self,padding="10");bottom_button_frame.pack(fill=tk.X,side=tk.BOTTOM);ttk.Button(bottom_button_frame,text="Save & Close",command=self.save_and_close).pack(side=tk.RIGHT);ttk.Button(bottom_button_frame,text="Cancel",command=self.destroy).pack(side=tk.RIGHT,padx=5)
    def on_sprite_selected(self,event=None):
        sprite_name=self.sprite_var.get();sprite_path=None
        for sprite_res in self.project_data['resources']['sprites']:
            if sprite_res['name']==sprite_name:sprite_path=os.path.join(self.master.project_root,sprite_res['path']);break
        self.preview_label.config(image='');self.preview_label.image=None
        if sprite_path and os.path.exists(sprite_path):
            try:
                img=Image.open(sprite_path);img.thumbnail((100,100),Image.Resampling.LANCZOS);photo_img=ImageTk.PhotoImage(img);self.preview_label.config(image=photo_img);self.preview_label.image=photo_img
            except Exception as e:print(f"Error loading sprite preview: {e}")
        else:self.preview_label.config(image='')
    def populate_forms(self):
        self.name_var.set(self.object_data.get("name",""));self.sprite_var.set(self.object_data.get("sprite",""));self.events_listbox.delete(0,tk.END)
        for event_name in sorted(self.object_data.get("events",{})):self.events_listbox.insert(tk.END,event_name)
        self.on_sprite_selected();self.update_button_states()
    def on_event_selected(self,event_widget):
        self.actions_listbox.delete(0,tk.END);self._clear_param_widgets();selection_indices=self.events_listbox.curselection()
        if not selection_indices:self.update_button_states();return
        selected_event=self.events_listbox.get(selection_indices[0]);actions_in_event=self.object_data.get("events",{}).get(selected_event,[])
        for action_data in actions_in_event:
            action_type=action_data.get("action");params=", ".join(f"{k}: {v}"for k,v in action_data.items()if k!="action");display_text=f"{action_type} ({params})";self.actions_listbox.insert(tk.END,display_text)
        self.update_button_states()
    def on_action_selected(self,event_widget):
        self._clear_param_widgets();event_selection=self.events_listbox.curselection();action_selection=self.actions_listbox.curselection()
        if not event_selection or not action_selection:self.update_button_states();return
        event_name=self.events_listbox.get(event_selection[0]);action_index=action_selection[0];action_data=self.object_data["events"][event_name][action_index];action_def=KNOWN_ACTIONS.get(action_data["action"])
        if not action_def:return
        self._build_param_ui(action_def,action_data);self.update_button_states()
    def _clear_param_widgets(self):
        for widget in self.params_frame.winfo_children():widget.destroy()
        self.param_vars.clear()
    def _build_param_ui(self,action_def,action_data):
        for i,param_def in enumerate(action_def):
            name=param_def["name"];label=ttk.Label(self.params_frame,text=f"{name}:");label.grid(row=i,column=0,sticky=tk.W,pady=2);current_value=action_data.get(name,param_def.get("default",""));var=tk.StringVar(value=current_value);widget=None
            if param_def["type"]in("number","string"):widget=ttk.Entry(self.params_frame,textvariable=var)
            elif param_def["type"]=="dropdown":widget=ttk.Combobox(self.params_frame,textvariable=var,values=param_def.get("options",[]),state="readonly")
            if widget:widget.grid(row=i,column=1,sticky=tk.EW,pady=2);self.param_vars[name]=var
        self.params_frame.columnconfigure(1,weight=1)
    def _update_action_from_params(self):
        event_selection=self.events_listbox.curselection();action_selection=self.actions_listbox.curselection()
        if not event_selection or not action_selection:return
        event_name=self.events_listbox.get(event_selection[0]);action_index=action_selection[0];action_data=self.object_data["events"][event_name][action_index]
        for name,var in self.param_vars.items():
            value=var.get()
            try:
                param_def=next(p for p in KNOWN_ACTIONS[action_data["action"]]if p["name"]==name)
                if param_def["type"]=="number":value=int(value)if"."not in value else float(value)
            except(ValueError,StopIteration):pass
            action_data[name]=value
    def _refresh_action_list(self):
        event_selection=self.events_listbox.curselection();action_selection_index=self.actions_listbox.curselection()
        if not event_selection:return
        selected_event=self.events_listbox.get(event_selection[0]);self.actions_listbox.delete(0,tk.END);actions_in_event=self.object_data.get("events",{}).get(selected_event,[])
        for action_data in actions_in_event:
            action_type=action_data.get("action");params=", ".join(f"{k}: {v}"for k,v in action_data.items()if k!="action");display_text=f"{action_type} ({params})";self.actions_listbox.insert(tk.END,display_text)
        if action_selection_index:
            new_index=action_selection_index[0]
            if new_index>=self.actions_listbox.size():new_index=self.actions_listbox.size()-1
            if new_index>=0:self.actions_listbox.selection_set(new_index);self.actions_listbox.see(new_index)
        self.on_action_selected(None)
    def update_button_states(self):
        event_selected=self.events_listbox.curselection();action_selected=self.actions_listbox.curselection();self.add_action_button.config(state="normal"if event_selected else"disabled");self.remove_action_button.config(state="normal"if action_selected else"disabled")
    def add_action(self):
        self._update_action_from_params();event_selection=self.events_listbox.curselection()
        if not event_selection:return
        dialog=AddActionDialog(self);new_action=dialog.result
        if new_action:selected_event_name=self.events_listbox.get(event_selection[0]);self.object_data["events"][selected_event_name].append(new_action);self._refresh_action_list()
    def remove_action(self):
        event_selection=self.events_listbox.curselection();action_selection=self.actions_listbox.curselection()
        if not event_selection or not action_selection:messagebox.showwarning("No Selection","Please select an action to remove.",parent=self);return
        event_name=self.events_listbox.get(event_selection[0]);action_index=action_selection[0];action_text=self.actions_listbox.get(action_index)
        if messagebox.askyesno("Confirm Removal",f"Are you sure you want to remove this action?\n\n{action_text}",parent=self):del self.object_data["events"][event_name][action_index];self._refresh_action_list()
    def save_and_close(self):
        self._update_action_from_params();self.object_data['name']=self.name_var.get();self.object_data['sprite']=self.sprite_var.get()
        try:
            with open(self.object_file_path,'w')as f:json.dump(self.object_data,f,indent=4,sort_keys=True)
            self.master.refresh_project_data();self.destroy()
        except Exception as e:messagebox.showerror("Save Error",f"Could not save the file: {e}",parent=self)
    def add_event(self):
        current_events=set(self.object_data.get("events",{}).keys());available_events=set(KNOWN_EVENTS)-current_events
        if not available_events:messagebox.showinfo("No More Events","All available events have been added.",parent=self);return
        dialog=AddEventDialog(self,available_events);new_event=dialog.result
        if new_event:
            self.object_data["events"][new_event]=[];self.populate_forms()
            for i,item in enumerate(self.events_listbox.get(0,tk.END)):
                if item==new_event:self.events_listbox.selection_set(i);self.on_event_selected(None);break
    def remove_event(self):
        selection=self.events_listbox.curselection()
        if not selection:messagebox.showwarning("No Selection","Please select an event to remove.",parent=self);return
        event_name=self.events_listbox.get(selection[0])
        if messagebox.askyesno("Confirm Removal",f"Are you sure you want to remove the '{event_name}' event?",parent=self):
            if event_name in self.object_data["events"]:del self.object_data["events"][event_name]
            self.populate_forms();self.actions_listbox.delete(0,tk.END)