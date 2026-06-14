import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import argparse
import zlib
import urllib.request
from io import BytesIO
from pathlib import Path
try:
    from PIL import Image, ImageTk
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    from visualizer_utils import (
        UNKNOWN_MATCH,
        detect_model_result_match,
        extract_case_id_from_agentc_filename,
        extract_case_id_from_json,
        find_matching_model_for_result,
    )
except ImportError:
    from .visualizer_utils import (
        UNKNOWN_MATCH,
        detect_model_result_match,
        extract_case_id_from_agentc_filename,
        extract_case_id_from_json,
        find_matching_model_for_result,
    )


class ComplianceVisualizer:
    def __init__(self, root, models_dir=None, guidelines_dir=None, model_path=None, guidelines_path=None, **kwargs):
        self.root = root
        self.root.title("VEGO-AI")
        self.root.geometry("1400x850")
        # Force light-mode appearance regardless of macOS dark mode
        style = ttk.Style()
        style.theme_use("clam")


        self.models_dir = models_dir
        self.guidelines_dir = guidelines_dir  # kept for legacy Browse mode
        self.aggregate_dir = kwargs.get('aggregate_dir', None)

        self.compliance_data = []    # list of display items for the tree
        self.uncovered_data = []     # uncovered fragments (alien elements)
        self.current_case_id = ""
        self.current_aggregate_path = None
        self.current_model_path = None
        self.current_model_content = ""
        self.current_match_info = {}
        self.diagram_image = None
        self.original_pill_image = None
        self.zoom_level = 1.0
        self.raw_json_data = {}      # full JSON for metadata panel
        self.reference_guidelines_map = {} # map of guideline ID -> reference details

        self._load_all_reference_guidelines()

        self.setup_ui()
        self.refresh_file_lists()

        # initial selection (legacy CLI args)
        if model_path:
            self.model_combo.set(os.path.basename(model_path))
        if guidelines_path:
            # try to find it in the aggregate list instead
            base = os.path.basename(guidelines_path)
            if base in self.aggregate_combo['values']:
                self.aggregate_combo.set(base)
                self.on_aggregate_selected()

    def _load_all_reference_guidelines(self):
        """Pre-load all reference guidelines from guidelines_dir (or a specific file)."""
        self.reference_guidelines_map.clear()
        if not self.guidelines_dir or not os.path.exists(self.guidelines_dir):
            return

        def _load_file(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    if "reference_guidelines" in data:
                        for rg in data["reference_guidelines"]:
                            gid = rg.get("id")
                            if gid:
                                self.reference_guidelines_map[gid] = rg
            except Exception:
                pass

        if os.path.isfile(self.guidelines_dir):
            if self.guidelines_dir.endswith('.json'):
                _load_file(self.guidelines_dir)
            return

        for root, _, files in os.walk(self.guidelines_dir):
            for f in files:
                if f.endswith('.json'):
                    _load_file(os.path.join(root, f))

    # ──────────────────────────────────────────────
    # UI CONSTRUCTION
    # ──────────────────────────────────────────────
    def setup_ui(self):
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=(8, 0))
        ttk.Label(header_frame, text="VEGO-AI", font=("Arial", 20, "bold")).pack(side=tk.LEFT)

        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(top_frame, text="Model:", font=("Arial", 13)).pack(side=tk.LEFT, padx=(0, 5))
        self.model_combo = ttk.Combobox(top_frame, width=38, state="readonly", font=("Arial", 12))
        self.model_combo.pack(side=tk.LEFT, padx=5)
        self.model_combo.bind("<<ComboboxSelected>>", self.on_model_selected)

        ttk.Label(top_frame, text="Aggregate:", font=("Arial", 13)).pack(side=tk.LEFT, padx=(10, 5))
        self.aggregate_combo = ttk.Combobox(top_frame, width=38, state="readonly", font=("Arial", 12))
        self.aggregate_combo.pack(side=tk.LEFT, padx=5)
        self.aggregate_combo.bind("<<ComboboxSelected>>", self.on_aggregate_selected)

        ttk.Button(top_frame, text="Refresh",          command=self.refresh_file_lists).pack(side=tk.LEFT, padx=(10,2))
        ttk.Button(top_frame, text="Browse Models…",   command=self.browse_models).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_frame, text="Browse Vectors…",  command=self.browse_vectors).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_frame, text="Browse Guide(s)…", command=self.browse_guidelines_dir).pack(side=tk.LEFT, padx=2)

        self.status_label = ttk.Label(top_frame, text="Ready.", font=("Arial", 12))
        self.status_label.pack(side=tk.LEFT, padx=10)

        self.match_banner = tk.Frame(self.root, background="#F4F6F8", bd=0, highlightthickness=1,
                                     highlightbackground="#C9D1D9")
        self.match_banner.pack(fill=tk.X, padx=10, pady=(0, 6))
        self.match_title_label = tk.Label(self.match_banner, text="Unknown", font=("Arial", 12, "bold"),
                                          background="#F4F6F8", foreground="#24292F")
        self.match_title_label.pack(side=tk.LEFT, padx=(10, 8), pady=6)
        self.match_message_label = tk.Label(self.match_banner, text="Select an aggregate result to validate the model pairing.",
                                            font=("Arial", 11), background="#F4F6F8", foreground="#24292F",
                                            anchor="w", justify=tk.LEFT, wraplength=930)
        self.match_message_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), pady=6)
        self.auto_match_button = ttk.Button(self.match_banner, text="Auto-load matching model",
                                            command=self.auto_load_matching_model)
        self.auto_match_button.pack(side=tk.RIGHT, padx=(0, 10), pady=4)
        self.auto_match_button.pack_forget()

        # ── Main paned layout ──────────────────────
        self.main_pw = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_pw.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Left: Code + Diagram notebook
        left_pane = ttk.Frame(self.main_pw)
        self.main_pw.add(left_pane, weight=1)
        self.left_notebook = ttk.Notebook(left_pane)
        self.left_notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Code
        self.code_tab = ttk.Frame(self.left_notebook)
        self.left_notebook.add(self.code_tab, text="Code")
        self.model_text = tk.Text(self.code_tab, wrap=tk.NONE, font=("Menlo", 13),
                                   background="white", foreground="black",
                                   insertbackground="black", padx=6, pady=4)
        vs = ttk.Scrollbar(self.code_tab, orient=tk.VERTICAL, command=self.model_text.yview)
        vs.pack(side=tk.RIGHT, fill=tk.Y)
        hs = ttk.Scrollbar(self.code_tab, orient=tk.HORIZONTAL, command=self.model_text.xview)
        hs.pack(side=tk.BOTTOM, fill=tk.X)
        self.model_text.config(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.model_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 2: Diagram
        self.diag_tab = ttk.Frame(self.left_notebook)
        self.left_notebook.add(self.diag_tab, text="Diagram")

        zoom_frame = ttk.Frame(self.diag_tab)
        zoom_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        ttk.Button(zoom_frame, text="In",  command=self.zoom_in,    width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="Out", command=self.zoom_out,   width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(zoom_frame, text="1x",  command=self.zoom_reset, width=3).pack(side=tk.LEFT, padx=2)
        self.zoom_label = ttk.Label(zoom_frame, text="100%")
        self.zoom_label.pack(side=tk.LEFT, padx=10)

        self.diag_canvas = tk.Canvas(self.diag_tab, background="white")
        dvs = ttk.Scrollbar(self.diag_tab, orient=tk.VERTICAL,   command=self.diag_canvas.yview)
        dvs.pack(side=tk.RIGHT, fill=tk.Y)
        dhs = ttk.Scrollbar(self.diag_tab, orient=tk.HORIZONTAL, command=self.diag_canvas.xview)
        dhs.pack(side=tk.BOTTOM, fill=tk.X)
        self.diag_canvas.config(yscrollcommand=dvs.set, xscrollcommand=dhs.set)
        self.diag_canvas.pack(fill=tk.BOTH, expand=True)
        self.diag_label = ttk.Label(self.diag_canvas, background="white")
        self.diag_canvas.create_window((0, 0), window=self.diag_label, anchor="nw")

        self.diag_canvas.bind("<Control-MouseWheel>", self.on_mousewheel)
        self.root.bind("<Command-equal>", lambda e: self.zoom_in())
        self.root.bind("<Command-minus>", lambda e: self.zoom_out())
        self.root.bind("<Command-0>",     lambda e: self.zoom_reset())

        # Right: Compliance tree + Details
        right_pw = ttk.PanedWindow(self.main_pw, orient=tk.VERTICAL)
        self.main_pw.add(right_pw, weight=1)

        list_frame = ttk.LabelFrame(right_pw, text="Compliance Vector")
        right_pw.add(list_frame, weight=1)
        self.summary_var = tk.StringVar(value="No aggregate loaded.")
        summary_frame = ttk.Frame(list_frame)
        summary_frame.pack(fill=tk.X, padx=5, pady=(5, 2))
        ttk.Label(summary_frame, textvariable=self.summary_var, font=("Arial", 11, "bold")).pack(side=tk.LEFT)

        filter_frame = ttk.Frame(list_frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=(0, 4))
        self.filter_text_var = tk.StringVar()
        self.status_filter_var = tk.StringVar(value="All statuses")
        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 4))
        search_entry = ttk.Entry(filter_frame, textvariable=self.filter_text_var, width=26)
        search_entry.pack(side=tk.LEFT, padx=(0, 8))
        search_entry.bind("<KeyRelease>", lambda _event: self._populate_tree())
        ttk.Label(filter_frame, text="Status:").pack(side=tk.LEFT, padx=(0, 4))
        self.status_filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.status_filter_var,
            values=("All statuses", "Satisfied", "Partially-Satisfied", "Not-Satisfied", "Alternative",
                    "Domain Mistake", "Language Mistake"),
            state="readonly",
            width=22,
        )
        self.status_filter_combo.pack(side=tk.LEFT)
        self.status_filter_combo.bind("<<ComboboxSelected>>", lambda _event: self._populate_tree())

        cols = ("id", "status", "guideline", "evidence")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings", style="Custom.Treeview")
        style = ttk.Style()
        style.configure("Custom.Treeview", font=("Arial", 12), rowheight=26)
        style.configure("Custom.Treeview.Heading", font=("Arial", 13, "bold"))
        self.tree.heading("id",          text="ID")
        self.tree.heading("status",      text="Status")
        self.tree.heading("guideline",   text="Guideline Desc")
        self.tree.heading("evidence",    text="Evidence / Fragment")
        self.tree.column("id",        width=65,  stretch=False)
        self.tree.column("status",    width=150, stretch=False)
        self.tree.column("guideline", width=250, stretch=True)
        self.tree.column("evidence",  width=250, stretch=True)
        ts = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        ts.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=ts.set)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_item)

        details_frame = ttk.LabelFrame(right_pw, text="Details")
        right_pw.add(details_frame, weight=1)
        self.details_notebook = ttk.Notebook(details_frame)
        self.details_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        details_tab = ttk.Frame(self.details_notebook)
        research_tab = ttk.Frame(self.details_notebook)
        self.details_notebook.add(details_tab, text="Details")
        self.details_notebook.add(research_tab, text="Research")

        self.details_text = tk.Text(details_tab, wrap=tk.WORD, font=("Arial", 13), state=tk.DISABLED,
                                    background="white", foreground="black",
                                    insertbackground="black", padx=8, pady=6,
                                    spacing1=2, spacing3=4)
        ds = ttk.Scrollbar(details_tab, orient=tk.VERTICAL, command=self.details_text.yview)
        ds.pack(side=tk.RIGHT, fill=tk.Y)
        self.details_text.config(yscrollcommand=ds.set)
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        self.research_text = tk.Text(research_tab, wrap=tk.WORD, font=("Arial", 12), state=tk.DISABLED,
                                     background="white", foreground="black",
                                     insertbackground="black", padx=8, pady=6,
                                     spacing1=2, spacing3=4)
        self.research_text.tag_configure("danger", foreground="#B00020", font=("Arial", 12, "bold"))
        rs = ttk.Scrollbar(research_tab, orient=tk.VERTICAL, command=self.research_text.yview)
        rs.pack(side=tk.RIGHT, fill=tk.Y)
        self.research_text.config(yscrollcommand=rs.set)
        self.research_text.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Tree colour tags
        self.tree.tag_configure("Satisfied",         foreground="green")
        self.tree.tag_configure("Partially-Satisfied", foreground="orange")
        self.tree.tag_configure("Not-Satisfied",     foreground="red")
        self.tree.tag_configure("Alternative",       foreground="#2E7D32")
        self.tree.tag_configure("Domain Mistake",    foreground="#D32F2F")
        self.tree.tag_configure("Language Mistake",  foreground="#7B1FA2")
        self.tree.tag_configure("Header", font=("Arial", 10, "bold"), background="#EEEEEE")

    # ──────────────────────────────────────────────
    # FILE LIST MANAGEMENT
    # ──────────────────────────────────────────────
    def refresh_file_lists(self):
        models = (
            [f for f in os.listdir(self.models_dir) if f.endswith(('.txt', '.puml'))]
            if self.models_dir and os.path.exists(self.models_dir) else []
        )
        aggregates = (
            [f for f in os.listdir(self.aggregate_dir) if f.endswith('.json')]
            if self.aggregate_dir and os.path.exists(self.aggregate_dir) else []
        )
        self.model_combo['values']     = sorted(models)
        self.aggregate_combo['values'] = sorted(aggregates)
        msg = f"{len(models)} models, {len(aggregates)} aggregate files available."
        self.status_label.config(text=msg)

    def _aggregate_path_from_combo(self):
        agg = self.aggregate_combo.get()
        if not agg or not self.aggregate_dir:
            return None
        return os.path.join(self.aggregate_dir, agg)

    def _model_path_from_combo(self):
        model_name = self.model_combo.get()
        if not model_name or not self.models_dir:
            return None
        return os.path.join(self.models_dir, model_name)

    def _read_json_file(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _set_match_banner(self, match_info):
        self.current_match_info = match_info or {}
        matched = self.current_match_info.get("matched", UNKNOWN_MATCH)
        mismatch_type = self.current_match_info.get("mismatch_type", "none")
        warning = self.current_match_info.get("warning_message") or "Pairing status is unknown."
        action = self.current_match_info.get("recommended_action") or ""

        if matched is True:
            title = "Matched"
            bg, fg, border = "#E6F4EA", "#137333", "#B7E1CD"
        elif mismatch_type == "no_matching_model_found":
            title = "No matching model found"
            bg, fg, border = "#FCE8E6", "#B00020", "#F5B5AC"
        elif matched is False:
            title = "Mismatch"
            bg, fg, border = "#FCE8E6", "#B00020", "#F5B5AC"
        else:
            title = "Unknown"
            bg, fg, border = "#FFF8E1", "#8A5A00", "#F9D57A"

        text = warning if not action else f"{warning} Recommended action: {action}"
        self.match_banner.config(background=bg, highlightbackground=border)
        self.match_title_label.config(text=title, background=bg, foreground=fg)
        self.match_message_label.config(text=text, background=bg, foreground="#24292F")

        self.auto_match_button.pack_forget()
        if matched is not True and self.current_match_info.get("result_case_id") and self.models_dir:
            self.auto_match_button.pack(side=tk.RIGHT, padx=(0, 10), pady=4)

    def _set_text(self, widget, text, danger_phrases=None):
        widget.config(state=tk.NORMAL)
        widget.delete(1.0, tk.END)
        widget.insert(tk.END, text)
        for phrase in danger_phrases or []:
            start = "1.0"
            while True:
                idx = widget.search(phrase, start, tk.END)
                if not idx:
                    break
                end = f"{idx}+{len(phrase)}c"
                widget.tag_add("danger", idx, end)
                start = end
        widget.config(state=tk.DISABLED)

    def _clear_model_selection(self):
        self.model_combo.set("")
        self.current_model_path = None
        self.current_model_content = ""
        if hasattr(self, "model_text"):
            self.model_text.delete(1.0, tk.END)
        if hasattr(self, "diag_label"):
            self.diag_label.config(image="", text="No model loaded.")

    def auto_load_matching_model(self):
        agg_path = self.current_aggregate_path or self._aggregate_path_from_combo()
        if not agg_path or not os.path.exists(agg_path):
            messagebox.showwarning("No aggregate selected", "Select an aggregate result before auto-loading a model.")
            return
        try:
            data = self._read_json_file(agg_path)
        except Exception as e:
            messagebox.showerror("Error loading aggregate file", str(e))
            return

        result_case_id = extract_case_id_from_json(data) or extract_case_id_from_agentc_filename(agg_path)
        model_path = find_matching_model_for_result(self.models_dir, result_case_id)
        if model_path:
            self.model_combo.set(os.path.basename(model_path))
            self._load_aggregate_file(agg_path, model_override=model_path)
            return

        self._clear_model_selection()
        no_match = detect_model_result_match(None, agg_path, data)
        if result_case_id and self.models_dir:
            no_match["warning_message"] = (
                f"No matching model found for result case {result_case_id} in {self.models_dir}."
            )
        self._set_match_banner(no_match)
        self._load_aggregate_file(agg_path, model_override=None, match_override=no_match)

    # ──────────────────────────────────────────────
    # EVENT HANDLERS
    # ──────────────────────────────────────────────
    def on_model_selected(self, event=None):
        """User manually picks a model, then validate it against the loaded result."""
        agg_path = self._aggregate_path_from_combo()
        model_path = self._model_path_from_combo()
        if agg_path:
            self._load_aggregate_file(agg_path, model_override=model_path)
            return
        if model_path:
            match_info = detect_model_result_match(model_path, None, None)
            self._set_match_banner(match_info)

    def on_aggregate_selected(self, event=None):
        agg_file = self.aggregate_combo.get()
        if not agg_file or not self.aggregate_dir:
            return
        agg_path = os.path.join(self.aggregate_dir, agg_file)

        try:
            peek = self._read_json_file(agg_path)
        except Exception:
            peek = {}

        cid = extract_case_id_from_json(peek) or extract_case_id_from_agentc_filename(agg_path)

        model_path = find_matching_model_for_result(self.models_dir, cid)
        match_override = None
        if model_path:
            self.model_combo.set(os.path.basename(model_path))
        else:
            self._clear_model_selection()
            match_override = detect_model_result_match(None, agg_path, peek)
            if cid and self.models_dir:
                match_override["warning_message"] = (
                    f"No matching model found for result case {cid} in {self.models_dir}."
                )

        self._load_aggregate_file(agg_path, model_override=model_path, match_override=match_override)

    def on_selection_change(self):
        """Legacy path when no aggregate is in play."""
        m = self.model_combo.get()
        agg = self.aggregate_combo.get()
        if agg and self.aggregate_dir:
            self.on_aggregate_selected()
        elif m and self.guidelines_dir:
            g_path = os.path.join(self.guidelines_dir, m)
            if os.path.exists(g_path):
                self._load_legacy_guidelines(
                    os.path.join(self.models_dir, m) if self.models_dir else None,
                    g_path
                )

    def browse_models(self):
        """Pick the folder that contains model .txt / .puml files."""
        folder = filedialog.askdirectory(title="Select Models Folder")
        if not folder:
            return
        self.models_dir = folder
        self.refresh_file_lists()
        if self.aggregate_combo.get():
            self.on_aggregate_selected()

    def browse_vectors(self):
        """Pick the folder that contains compliance-vector JSON files."""
        folder = filedialog.askdirectory(title="Select Compliance Vectors Folder")
        if not folder:
            return
        self.aggregate_dir = folder
        self.refresh_file_lists()
        self._clear_model_selection()

    def browse_guidelines_dir(self):
        """Pick a JSON file or folder containing reference guidelines."""
        path = filedialog.askopenfilename(title="Select Reference Guidelines File (JSON)", filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")])
        if not path:
            return
        self.guidelines_dir = path
        self._load_all_reference_guidelines()
        
        msg = f"Loaded {len(self.reference_guidelines_map)} guidelines from {os.path.basename(self.guidelines_dir)}."
        self.status_label.config(text=msg)
        
        # Refresh tree to display newly loaded guideline descriptions
        self._populate_tree()
        self.on_select_item()

    def open_files(self):
        """Legacy: pick individual files via file dialog."""
        m = filedialog.askopenfilename(title="Select Model (.txt / .puml)")
        if not m:
            return
        g = filedialog.askopenfilename(title="Select Aggregate / Guidelines (.json)")
        if not g:
            return
        self.models_dir = os.path.dirname(m)
        # decide whether this is an aggregate file
        try:
            with open(g, 'r', encoding='utf-8') as f:
                sample = json.load(f)
            is_aggregate = "existing_mapping" in sample or "compliance_contributions" in sample
        except Exception:
            is_aggregate = False

        if is_aggregate:
            self.aggregate_dir = os.path.dirname(g)
        else:
            self.guidelines_dir = os.path.dirname(g)
        self.refresh_file_lists()
        self.model_combo.set(os.path.basename(m))
        agg_name = os.path.basename(g)
        if agg_name in self.aggregate_combo['values']:
            self.aggregate_combo.set(agg_name)
            self._load_aggregate_file(g, model_override=m)
        else:
            self._load_legacy_guidelines(m, g)

    # ──────────────────────────────────────────────
    # AGGREGATE JSON LOADING  (new format)
    # ──────────────────────────────────────────────
    def _load_aggregate_file(self, agg_path, model_override=None, match_override=None):
        try:
            with open(agg_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.raw_json_data = data
            cid = str(
                extract_case_id_from_json(data)
                or extract_case_id_from_agentc_filename(agg_path)
                or data.get("case_id", os.path.splitext(os.path.basename(agg_path))[0])
            )
            self.current_case_id = cid
            self.current_aggregate_path = agg_path

            # ── load model text ──────────────────────
            m_content = ""
            if model_override and os.path.exists(model_override):
                with open(model_override, 'r', encoding='utf-8') as f:
                    m_content = f.read()
                self.current_model_path = model_override
            else:
                self.current_model_path = None

            self.current_model_content = m_content
            self.model_text.delete(1.0, tk.END)
            self.model_text.insert(tk.END, m_content)
            match_info = match_override or detect_model_result_match(self.current_model_path, agg_path, data)
            self._set_match_banner(match_info)

            # ── build compliance_data from existing_mapping ──
            existing   = data.get("existing_mapping", [])
            potential  = data.get("potential_found", [])
            contrib    = {e["guideline_id"]: e for e in data.get("compliance_contributions", []) if "guideline_id" in e}

            # merge potential into existing by guideline_id (fill gaps)
            existing_ids = {e.get("guideline_id") for e in existing}
            for p in potential:
                if p.get("guideline_id") not in existing_ids:
                    existing.append(p)

            self.compliance_data = []
            for entry in existing:
                gid    = entry.get("guideline_id", "")
                status = entry.get("compliance_status", "")
                ev     = entry.get("evidence", entry.get("notes", ""))
                score  = contrib.get(gid, {}).get("score", "")
                self.compliance_data.append({
                    "guideline_id": gid,
                    "label":        status,          # drives tree colour tag
                    "evidence":     ev,
                    "notes":        entry.get("notes", ""),
                    "score":        score,
                    "description":  ev[:80] if ev else "",
                })

            # ── uncovered fragments (alien-like) ────
            self.uncovered_data = data.get("uncovered_fragments", [])

            self._populate_tree()
            n_g = len(self.compliance_data)
            n_u = len(self.uncovered_data)
            score_pct = data.get("score_pct", "")
            score_str = f" | Score: {score_pct}%" if score_pct != "" else ""
            self.status_label.config(text=f"Loaded case {cid} | {n_g} guidelines, {n_u} fragments{score_str}")
            self._populate_research_panel(agg_path, data, match_info)
            self.update_diagram()

        except Exception as e:
            messagebox.showerror("Error loading aggregate file", str(e))

    # ──────────────────────────────────────────────
    # LEGACY GUIDELINES LOADING  (old compliance_vector format)
    # ──────────────────────────────────────────────
    def _load_legacy_guidelines(self, m_path, g_path):
        try:
            m_content = ""
            if m_path and os.path.exists(m_path):
                with open(m_path, 'r', encoding='utf-8') as f:
                    m_content = f.read()
            with open(g_path, 'r', encoding='utf-8') as f:
                g_json = json.load(f)
            self.raw_json_data = g_json
            self.current_aggregate_path = g_path
            self.current_model_path = m_path if m_path and os.path.exists(m_path) else None

            cid = ""
            if m_path:
                cid = os.path.splitext(os.path.basename(m_path))[0].split('_')[0]
            elif isinstance(g_json, dict) and "case_id" in g_json:
                cid = str(g_json["case_id"])
            self.current_case_id = cid

            vector, aliens = None, []
            if isinstance(g_json, dict):
                vector = g_json.get("compliance_vector") or g_json.get(cid, {}).get("compliance_vector")
                aliens = g_json.get("alien_elements_evaluation") or g_json.get(cid, {}).get("alien_elements_evaluation", [])
            elif isinstance(g_json, list):
                for case in g_json:
                    if str(case.get("case_id")) == cid:
                        vector = case.get("compliance_vector")
                        aliens = case.get("alien_elements_evaluation", [])
                        self.raw_json_data = case
                        break

            self.current_model_content = m_content
            self.model_text.delete(1.0, tk.END)
            self.model_text.insert(tk.END, m_content)
            self.compliance_data = vector or []
            self.uncovered_data  = aliens or []
            match_info = detect_model_result_match(self.current_model_path, g_path, g_json)
            self._set_match_banner(match_info)
            self._populate_research_panel(g_path, g_json, match_info)
            self._populate_tree()
            self.status_label.config(text=f"Loaded {cid} | {len(self.compliance_data)} Gs, {len(self.uncovered_data)} Aliens")
            self.update_diagram()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ──────────────────────────────────────────────
    # READ-ONLY RESEARCH PANELS
    # ──────────────────────────────────────────────
    def _populate_research_panel(self, agg_path, result_json, match_info):
        lines = [
            "READ-ONLY RESEARCH CONTEXT",
            "==========================",
            "",
            "This panel summarizes optional M1/M2/M3/M4 research artifacts if they are present near the selected result.",
            "It never writes feedback, memory, advice, comparisons, eval output, or model files.",
            "",
            "PAIRING STATE",
            "-------------",
            f"Model case id: {match_info.get('model_case_id') or 'Unknown'}",
            f"Result case id: {match_info.get('result_case_id') or 'Unknown'}",
            f"Match status: {match_info.get('matched')}",
            f"Mismatch type: {match_info.get('mismatch_type')}",
            f"Message: {match_info.get('warning_message') or 'None'}",
            "",
        ]
        danger_phrases = []
        artifacts = self._discover_research_artifacts(agg_path)

        try:
            if artifacts.get("review_queue"):
                lines.extend(self._format_review_queue_panel("M1/M2 HUMAN REVIEW QUEUE", artifacts["review_queue"]))
            if artifacts.get("resolved_queue"):
                lines.extend(self._format_review_queue_panel("M1/M2 RESOLVED HUMAN FEEDBACK", artifacts["resolved_queue"]))
            if artifacts.get("memory"):
                lines.extend(self._format_memory_panel(artifacts["memory"]))
            if artifacts.get("memory_advice"):
                advice_lines, advice_dangers = self._format_memory_advice_panel(artifacts["memory_advice"])
                lines.extend(advice_lines)
                danger_phrases.extend(advice_dangers)
            if artifacts.get("memory_informed_comparison"):
                comparison_lines, comparison_dangers = self._format_memory_comparison_panel(
                    artifacts["memory_informed_comparison"]
                )
                lines.extend(comparison_lines)
                danger_phrases.extend(comparison_dangers)
        except Exception as e:
            warning = f"RED WARNING: optional research artifact could not be read: {e}"
            lines.extend(["RESEARCH ARTIFACT WARNING", "-------------------------", warning, ""])
            danger_phrases.append(warning)

        if not any(artifacts.values()):
            lines.extend(
                [
                    "OPTIONAL RESEARCH ARTIFACTS",
                    "---------------------------",
                    "No supported research-layer files were found near this aggregate.",
                    "",
                    "Supported read-only schemas:",
                    "- M1/M2 review JSONL: review_id, review_signature, status, trigger_reasons, ai_decision, human_feedback.",
                    "- M3 memory JSONL: memory_id, decision_type, human_classification, conflict_status, reuse_scope, rationale, provenance.",
                    "- M4A memory_advice JSON: top-level advice[] with ai_classification_changed=false.",
                    "- M4B-1 comparison JSON: mode=experimental and ai_behavior_changed_in_baseline=false.",
                ]
            )

        self._set_text(self.research_text, "\n".join(lines), danger_phrases)

    def _discover_research_artifacts(self, agg_path):
        found = {
            "review_queue": None,
            "resolved_queue": None,
            "memory": None,
            "memory_advice": None,
            "memory_informed_comparison": None,
        }
        if not agg_path:
            return found
        base = Path(agg_path).resolve().parent
        search_dirs = [base]
        if base.parent not in search_dirs:
            search_dirs.append(base.parent)

        candidates = {
            "review_queue": ("human_review_queue.jsonl", "review_queue.jsonl"),
            "resolved_queue": ("human_review_queue_resolved.jsonl", "resolved_human_feedback.jsonl"),
            "memory": ("human_judgment_memory.jsonl", "judgment_memory.jsonl"),
            "memory_advice": ("memory_advice.json",),
            "memory_informed_comparison": ("memory_informed_comparison.json",),
        }
        for key, names in candidates.items():
            for folder in search_dirs:
                for name in names:
                    path = folder / name
                    if path.exists() and path.is_file():
                        found[key] = path
                        break
                if found[key]:
                    break
        return found

    def _format_review_queue_panel(self, title, path):
        items = self._read_jsonl_items(path, limit=8)
        lines = [title, "-" * len(title), f"Source: {path}", f"Items shown: {len(items)}", ""]
        for item in items:
            feedback = item.get("human_feedback") if isinstance(item.get("human_feedback"), dict) else {}
            ai_decision = item.get("ai_decision") if isinstance(item.get("ai_decision"), dict) else {}
            trigger_reasons = item.get("trigger_reasons", [])
            review_signature = item.get("review_signature")
            feedback_signature = feedback.get("review_signature")
            lines.extend(
                [
                    f"review_id: {item.get('review_id', 'Unknown')}",
                    f"status: {item.get('status', 'Unknown')}",
                    f"trigger_reasons: {self._compact(trigger_reasons)}",
                    f"ai_decision: {self._compact(ai_decision)}",
                    f"feedback.decision_type: {feedback.get('decision_type', 'Unknown')}",
                    f"feedback.rationale: {feedback.get('rationale', '')}",
                    f"feedback.reusable: {feedback.get('reusable', 'Unknown')}",
                ]
            )
            if review_signature and feedback_signature and review_signature != feedback_signature:
                lines.append("WARNING: human feedback signature does not match the queued review signature.")
            lines.append("")
        return lines

    def _format_memory_panel(self, path):
        items = self._read_jsonl_items(path, limit=8)
        lines = ["M3 HUMAN JUDGMENT MEMORY", "------------------------", f"Source: {path}", f"Items shown: {len(items)}", ""]
        for item in items:
            lines.extend(
                [
                    f"memory_id: {item.get('memory_id', 'Unknown')}",
                    f"decision_type: {item.get('decision_type', 'Unknown')}",
                    f"human_classification: {item.get('human_classification', 'Unknown')}",
                    f"conflict_status: {item.get('conflict_status', 'Unknown')}",
                    f"reuse_scope: {self._compact(item.get('reuse_scope', 'Unknown'))}",
                    f"rationale: {item.get('rationale', '')}",
                    f"provenance: {self._compact(item.get('provenance', {}))}",
                    "",
                ]
            )
        return lines

    def _format_memory_advice_panel(self, path):
        data = self._read_json_file(path)
        advice = data.get("advice", []) if isinstance(data, dict) else []
        if not isinstance(advice, list):
            advice = []
        danger = []
        danger_line = "RED WARNING: memory_advice contains ai_classification_changed values that are not false."
        if any(item.get("ai_classification_changed") is not False for item in advice if isinstance(item, dict)):
            danger.append(danger_line)

        lines = [
            "M4A MEMORY ADVICE",
            "----------------",
            f"Source: {path}",
            "Memory advice is advisory only. AI classification was not changed.",
            f"Advice items shown: {min(len(advice), 8)} of {len(advice)}",
        ]
        if danger:
            lines.append(danger_line)
        lines.append("")
        for item in advice[:8]:
            if not isinstance(item, dict):
                continue
            lines.extend(
                [
                    f"pattern_id: {item.get('pattern_id', 'Unknown')}",
                    f"advice_mode: {item.get('advice_mode', 'Unknown')}",
                    f"ai_classification_changed: {item.get('ai_classification_changed', 'Unknown')}",
                    f"advice_strength: {item.get('advice_strength', 'Unknown')}",
                    f"advice_summary: {item.get('advice_summary', '')}",
                    f"memory_matches: {self._compact(item.get('memory_matches', []))}",
                    f"conflicts: {self._compact(item.get('conflicts', []))}",
                    f"original_ai_classification: {self._compact(item.get('original_ai_classification', 'Unknown'))}",
                    "",
                ]
            )
        return lines, danger

    def _format_memory_comparison_panel(self, path):
        data = self._read_json_file(path)
        comparisons = data.get("comparisons", []) if isinstance(data, dict) else []
        if not isinstance(comparisons, list):
            comparisons = []
        danger = []
        danger_line = "RED WARNING: memory-informed comparison indicates baseline AI behavior may have changed."
        if not isinstance(data, dict) or data.get("ai_behavior_changed_in_baseline") is not False:
            danger.append(danger_line)

        lines = [
            "M4B-1 MEMORY-INFORMED COMPARISON",
            "--------------------------------",
            f"Source: {path}",
            "Memory-informed comparison is experimental and non-destructive. Baseline Agent 4 output was not overwritten.",
            f"mode: {data.get('mode', 'Unknown') if isinstance(data, dict) else 'Unknown'}",
            f"ai_behavior_changed_in_baseline: {data.get('ai_behavior_changed_in_baseline', 'Unknown') if isinstance(data, dict) else 'Unknown'}",
            f"Comparisons shown: {min(len(comparisons), 8)} of {len(comparisons)}",
        ]
        if danger:
            lines.append(danger_line)
        lines.append("")
        for item in comparisons[:8]:
            if not isinstance(item, dict):
                continue
            lines.extend(
                [
                    f"pattern_id: {item.get('pattern_id', 'Unknown')}",
                    f"baseline_classification: {self._compact(item.get('baseline_classification', 'Unknown'))}",
                    f"memory_informed_classification: {self._compact(item.get('memory_informed_classification', 'Unknown'))}",
                    f"classification_changed: {item.get('classification_changed', 'Unknown')}",
                    f"human_review_after_memory: {item.get('human_review_after_memory', 'Unknown')}",
                    "",
                ]
            )
        return lines, danger

    def _read_jsonl_items(self, path, limit=8):
        items = []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    stripped = line.strip()
                    if not stripped:
                        continue
                    items.append(json.loads(stripped))
                    if len(items) >= limit:
                        break
        except Exception as e:
            return [{"review_id": "Error", "status": str(e)}]
        return items

    def _compact(self, value, max_len=240):
        if isinstance(value, (dict, list)):
            text = json.dumps(value, ensure_ascii=False, sort_keys=True)
        else:
            text = str(value)
        return text if len(text) <= max_len else text[: max_len - 3] + "..."

    # ──────────────────────────────────────────────
    # DIAGRAM
    # ──────────────────────────────────────────────
    def update_diagram(self):
        # clear previous image
        self.diag_label.config(image="", text="")
        if not self.current_model_content.strip():
            self.diag_label.config(text="No model loaded.")
            return
        try:
            url = self._plantuml_url(self.current_model_content)
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read()
            if PILLOW_AVAILABLE:
                self.original_pill_image = Image.open(BytesIO(raw))
                self.apply_zoom()
            else:
                self.diagram_image = tk.PhotoImage(data=raw)
                self.diag_label.config(image=self.diagram_image)
                self.diag_canvas.config(
                    scrollregion=(0, 0, self.diagram_image.width(), self.diagram_image.height())
                )
        except Exception as e:
            self.diag_label.config(text=f"Diagram error: {e}", image="")

    def apply_zoom(self):
        if not PILLOW_AVAILABLE or not self.original_pill_image:
            return
        w, h = self.original_pill_image.size
        nw, nh = max(1, int(w * self.zoom_level)), max(1, int(h * self.zoom_level))
        res = Image.LANCZOS if hasattr(Image, "LANCZOS") else Image.BICUBIC
        self.diagram_image = ImageTk.PhotoImage(self.original_pill_image.resize((nw, nh), res))
        self.diag_label.config(image=self.diagram_image)
        self.diag_canvas.config(scrollregion=(0, 0, nw, nh))
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")

    def zoom_in(self):    self.zoom_level = min(5.0, self.zoom_level * 1.2);  self.apply_zoom()
    def zoom_out(self):   self.zoom_level = max(0.1, self.zoom_level / 1.2);  self.apply_zoom()
    def zoom_reset(self): self.zoom_level = 1.0;                               self.apply_zoom()
    def on_mousewheel(self, e): (self.zoom_in() if e.delta > 0 else self.zoom_out()); return "break"

    def _plantuml_url(self, text):
        c = zlib.compress(text.encode('utf-8'), 9)[2:-4]
        res = ""
        for i in range(0, len(c), 3):
            chunk = c[i:i+3]
            b1 = chunk[0]
            b2 = chunk[1] if len(chunk) > 1 else 0
            b3 = chunk[2] if len(chunk) > 2 else 0
            c1, c2, c3, c4 = b1 >> 2, ((b1 & 3) << 4) | (b2 >> 4), ((b2 & 15) << 2) | (b3 >> 6), b3 & 63
            for x in [c1, c2, c3, c4]:
                res += self._e(x & 63)
        return f"http://www.plantuml.com/plantuml/png/{res}"

    def _e(self, b):
        if b < 10: return chr(48 + b)
        b -= 10
        if b < 26: return chr(65 + b)
        b -= 26
        if b < 26: return chr(97 + b)
        b -= 26
        return '-' if b == 0 else ('_' if b == 1 else '?')

    # ──────────────────────────────────────────────
    # TREE POPULATION
    # ──────────────────────────────────────────────
    def _row_matches_filters(self, values):
        search_text = self.filter_text_var.get().strip().lower() if hasattr(self, "filter_text_var") else ""
        status_filter = self.status_filter_var.get() if hasattr(self, "status_filter_var") else "All statuses"
        if status_filter and status_filter != "All statuses" and values[1] != status_filter:
            return False
        if search_text and search_text not in " ".join(str(v).lower() for v in values):
            return False
        return True

    def _populate_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Section: guidelines / compliance
        self.tree.insert("", tk.END, iid="h_g",
                         values=("---", "COMPLIANCE", "GUIDELINES ---", ""), tags=("Header",))
        shown_guidelines = 0
        for idx, g in enumerate(self.compliance_data):
            gid    = g.get("guideline_id", "")
            status = g.get("label", g.get("compliance_status", ""))
            
            ref = self.reference_guidelines_map.get(gid, {})
            guide_desc = (ref.get("description") or ref.get("guideline_name") or "")[:120]
            ev = (g.get("evidence") or g.get("notes") or g.get("description", ""))[:90]
            values = (gid, status, guide_desc, ev)
            if not self._row_matches_filters(values):
                continue
            self.tree.insert("", tk.END, iid=f"g_{idx}",
                             values=values, tags=(status,))
            shown_guidelines += 1

        # Section: uncovered fragments (shown below guidelines)
        shown_fragments = 0
        if self.uncovered_data:
            for idx, uf in enumerate(self.uncovered_data):
                lbl   = uf.get("label", "")
                snip  = uf.get("fragment", "")[:80]
                values = ("Frag", lbl, "", snip)
                if not self._row_matches_filters(values):
                    continue
                self.tree.insert("", tk.END, iid=f"u_{idx}",
                                 values=values, tags=(lbl,))
                shown_fragments += 1

        # Summary row always at the very bottom
        self.tree.insert("", tk.END, iid="h_summary",
                         values=("📊", "SUMMARY", "Click to view case score & assessment", ""), tags=("Header",))
        if hasattr(self, "summary_var"):
            score_pct = self.raw_json_data.get("score_pct", "") if isinstance(self.raw_json_data, dict) else ""
            score_text = f" | Score {score_pct}%" if score_pct != "" else ""
            self.summary_var.set(
                f"Case {self.current_case_id or 'Unknown'}{score_text} | "
                f"Guidelines {shown_guidelines}/{len(self.compliance_data)} shown | "
                f"Fragments {shown_fragments}/{len(self.uncovered_data)} shown"
            )

    # ──────────────────────────────────────────────
    # DETAILS PANEL
    # ──────────────────────────────────────────────
    def on_select_item(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]

        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)

        if iid == "h_summary" or iid.startswith("h_"):
            # show case summary: score + overall assessment first, then other meta
            d = "CASE SUMMARY\n============\n\n"
            priority = ["case_id", "skill_version", "total_score", "max_score", "score_pct", "overall_assessment"]
            shown = set()
            for k in priority:
                if k in self.raw_json_data:
                    v = self.raw_json_data[k]
                    d += f"{k.upper().replace('_',' ')}:\n{v}\n\n"
                    shown.add(k)
            skip = {"existing_mapping", "potential_found", "uncovered_fragments",
                    "compliance_contributions", "fragment_contributions",
                    "compliance_vector", "alien_elements_evaluation"}
            for k, v in self.raw_json_data.items():
                if k not in skip and k not in shown:
                    d += f"{k.upper().replace('_',' ')}:\n"
                    d += f"{json.dumps(v, indent=2) if isinstance(v, (dict, list)) else v}\n\n"
            self.details_text.insert(tk.END, d)

        elif iid.startswith("g_"):
            item = self.compliance_data[int(iid.split("_")[1])]
            gid  = item.get("guideline_id", "???")
            d = f"GUIDELINE {gid}\n{'=' * (12 + len(gid))}\n\n"
            
            if gid in self.reference_guidelines_map:
                ref = self.reference_guidelines_map[gid]
                if ref.get("guideline_name"):
                    d += f"NAME:\n{ref.get('guideline_name')}\n\n"
                if ref.get("description"):
                    d += f"DESCRIPTION:\n{ref.get('description')}\n\n"

            d += f"STATUS:\n{item.get('label', item.get('compliance_status', ''))}\n\n"
            ev = item.get("evidence", "")
            if ev:
                d += f"EVIDENCE:\n{ev}\n\n"
            notes = item.get("notes", "")
            if notes:
                d += f"NOTES:\n{notes}\n\n"
            score = item.get("score", "")
            if score != "":
                d += f"SCORE: {score}\n\n"
            # any remaining keys
            shown = {"guideline_id", "label", "compliance_status", "evidence", "notes", "score", "description"}
            for k, v in item.items():
                if k not in shown and v not in (None, "", []):
                    d += f"{k.upper().replace('_',' ')}:\n{json.dumps(v, indent=2) if isinstance(v, (dict, list)) else v}\n\n"
            self.details_text.insert(tk.END, d)

        elif iid.startswith("u_"):
            item = self.uncovered_data[int(iid.split("_")[1])]
            d = "UNCOVERED FRAGMENT\n==================\n\n"
            d += f"LABEL: {item.get('label', '')}\n"
            sev = item.get("severity", "")
            if sev:
                d += f"SEVERITY: {sev}\n"
            d += f"\nFRAGMENT:\n{item.get('fragment', '')}\n\n"
            reason = item.get("reason", "")
            if reason:
                d += f"REASON:\n{reason}\n"
            self.details_text.insert(tk.END, d)

        self.details_text.config(state=tk.DISABLED)


# ──────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="visualize_config.yaml")
    p.add_argument("--models_dir")
    p.add_argument("--guidelines_dir")
    p.add_argument("--aggregate_dir")
    args = p.parse_args()

    md, gd, ad = args.models_dir, args.guidelines_dir, args.aggregate_dir
    cp = args.config
    if not os.path.isabs(cp) and not os.path.exists(cp):
        sd = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(os.path.join(sd, cp)):
            cp = os.path.join(sd, cp)

    if os.path.exists(cp):
        with open(cp, 'r', encoding='utf-8') as f:
            for line in f:
                if ':' in line:
                    k, v = [x.strip().strip('"').strip("'") for x in line.split(':', 1)]
                    if k == 'models_dir'    and not md: md = v
                    elif k == 'guidelines_dir' and not gd: gd = v
                    elif k == 'aggregate_dir'  and not ad: ad = v

    tk_root = tk.Tk()
    ComplianceVisualizer(tk_root, models_dir=md, guidelines_dir=gd, aggregate_dir=ad)
    tk_root.mainloop()
