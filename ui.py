"""
ui.py - UI module for Arknights Auto Separate/Cut Pause
Contains all widget creation, layout, and theme management
"""

import tkinter as tk
from tkinter import ttk
import darkdetect
from i18n import t, register_language_change_callback, update_combobox_preserve_selection

# Theme color definitions
THEMES = {
    "light": {
        "bg": "#f5f5f5",
        "fg": "#000000",
        "input_bg": "#ffffff",
        "path_bg": "#e0e0e0",
        "link_fg": "#0066cc",
    },
    "dark": {
        "bg": "#2b2b2b",
        "fg": "#ffffff",
        "input_bg": "#3c3c3c",
        "path_bg": "#404040",
        "link_fg": "#66b3ff",
    }
}

# Font constants
FONT_NORMAL = ("TkDefaultFont", 10)
FONT_LABEL = ("TkDefaultFont", 10)
FONT_BUTTON = ("TkDefaultFont", 10)
FONT_LINK = ("TkDefaultFont", 10, "underline")


class MainWindow:
    def __init__(self, root, working_path, default_language="cn"):
        self.root = root
        self.working_path = working_path
        self.default_language = default_language
        self.theme_mode = "auto"  # "auto", "light", or "dark"
        self.description_labels = []  # Store description label references

        # Configure root window for pack layout
        self._setup_layout_config()

        # Create all widgets
        self._create_widgets()

        # Apply initial theme
        self.apply_theme()

    def _setup_layout_config(self):
        """Configure root window for vertical pack layout"""
        # Root will use pack layout - no columnconfigure needed
        pass

    def get_effective_theme(self):
        """Get the actual theme to apply (resolves 'auto')"""
        if self.theme_mode == "auto":
            return "dark" if darkdetect.isDark() else "light"
        return self.theme_mode

    def apply_theme(self):
        """Apply current theme to all widgets"""
        theme = THEMES[self.get_effective_theme()]

        # Update root window background
        try:
            self.root.configure(bg=theme["bg"])
        except Exception:
            pass  # Root window may not support bg on all platforms

        # Update all Entry widgets with input_bg
        entry_widgets = [
            'e_top_margin', 'e_bottom_margin', 'e_left_margin', 'e_right_margin',
            'e_thread_num', 'e_ignore_frame_cnt', 'e_measure_margin_second',
            'e_start_second', 'e_end_second',
            'e_manual_set_second_1', 'e_manual_set_second_2'
        ]

        for widget_name in entry_widgets:
            if hasattr(self, widget_name):
                try:
                    getattr(self, widget_name).configure(bg=theme["input_bg"], fg=theme["fg"])
                except Exception:
                    pass

        # Update path label
        if hasattr(self, 'l_working_path'):
            try:
                self.l_working_path.configure(bg=theme["path_bg"], fg=theme["fg"])
            except Exception:
                pass

        # Update tutorial link
        if hasattr(self, 'l_tutorial_url'):
            try:
                self.l_tutorial_url.configure(fg=theme["link_fg"])
            except Exception:
                pass

    def change_theme(self, event=None):
        """Handle theme dropdown change"""
        idx = self.e_theme.current()
        self.theme_mode = ["auto", "light", "dark"][idx]
        self.apply_theme()

    def _create_widgets(self):
        """Create all UI widgets"""
        # Window setup
        self.root.title(t("window_title"))
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Set default combobox listbox font
        self.root.option_add("*TCombobox*Listbox.font", FONT_NORMAL)

        # Create main container for centered content
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(expand=True, fill="both", padx=20, pady=20)

        # ===== HEADER SECTION =====
        self._create_header_section()

        # ===== MODE SECTION =====
        self._create_mode_section()

        # ===== TWO COLUMN SECTION (Margin + Processing) =====
        self._create_two_column_section()

        # ===== CROP ACTIONS SECTION =====
        self._create_crop_section()

        # ===== PROCESS ACTIONS SECTION =====
        self._create_process_section()

        # ===== TUTORIAL SECTION =====
        self._create_tutorial_section()

        # ===== MANUAL DETECTION SECTION (HIDDEN - widgets created but not displayed) =====
        # Still create the widgets for compatibility, but don't display them
        self._create_manual_detection_hidden()

    def _create_header_section(self):
        """Create header section with working path, language, and theme"""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill="x", expand=False, padx=5, pady=5)

        # Working path row
        self.l_text_working_path = tk.Label(
            header_frame, text=t("current_working_dir"), font=FONT_LABEL
        )
        self.l_working_path = tk.Label(
            header_frame, text=self.working_path, font=FONT_LABEL
        )

        self.l_text_working_path.grid(row=0, column=0, sticky="e", padx=10, pady=5)
        self.l_working_path.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Language and theme row
        self.l_language = tk.Label(header_frame, text=t("language"), font=FONT_LABEL)
        self.e_language = ttk.Combobox(header_frame, values=["中文", "English"], font=FONT_NORMAL, width=10)
        self.e_language.current(0 if self.default_language == "cn" else 1)

        self.l_theme = tk.Label(header_frame, text=t("theme"), font=FONT_LABEL)
        self.e_theme = ttk.Combobox(
            header_frame, values=[t("auto"), t("light"), t("dark")], font=FONT_NORMAL, width=10
        )
        self.e_theme.current(0)
        self.e_theme.bind("<<ComboboxSelected>>", self.change_theme)

        self.l_language.grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.e_language.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.l_theme.grid(row=1, column=2, sticky="e", padx=10, pady=5)
        self.e_theme.grid(row=1, column=3, sticky="w", padx=5, pady=5)

        header_frame.columnconfigure(1, weight=1)

    def _create_mode_section(self):
        """Create mode selection section"""
        self.mode_frame = ttk.LabelFrame(self.main_container, text=t("select_mode"))
        self.mode_frame.pack(fill="x", expand=False, padx=5, pady=5)

        # Mode dropdown and show description button
        self.l_mode = tk.Label(self.mode_frame, text=t("select_mode"), font=FONT_LABEL)
        self.e_mode = ttk.Combobox(self.mode_frame, font=FONT_NORMAL, width=35)
        self.e_mode["value"] = (
            t("mode_normal_audio_only"),
            t("mode_normal_keep_video"),
            t("mode_lazy_keep_valid"),
            t("mode_lazy_cut_all")
        )
        self.e_mode.current(1)
        self.b_show_desc = tk.Button(self.mode_frame, text=t("show_desc"), font=FONT_BUTTON)

        self.l_mode.grid(row=0, column=0, sticky="e", padx=10, pady=5)
        self.e_mode.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.b_show_desc.grid(row=0, column=2, sticky="ew", padx=10, pady=5)

        # Description labels container (rows 1-3)
        self._create_description_labels()

        self.mode_frame.columnconfigure(1, weight=1)

    def _create_description_labels(self):
        """Create mode description labels (initially empty)"""
        # Labels will be dynamically created/updated by show_description_labels()
        # Reserve space for 3 description lines
        for i in range(3):
            lbl = tk.Label(self.mode_frame, text="", font=FONT_LABEL, justify="left")
            lbl.grid(row=1 + i, column=0, columnspan=3, sticky="w", padx=10, pady=2)
            lbl.grid_remove()  # Initially hidden
            self.description_labels.append(lbl)

    def _create_two_column_section(self):
        """Create two-column section with margin and processing settings"""
        two_col_container = tk.Frame(self.main_container)
        two_col_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Left column - Margin Section
        margin_frame = self._create_margin_section(two_col_container)
        margin_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Right column - Processing Section
        processing_frame = self._create_processing_section(two_col_container)
        processing_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        # Equal column weights
        two_col_container.columnconfigure(0, weight=1)
        two_col_container.columnconfigure(1, weight=1)

    def _create_manual_detection_hidden(self):
        """Create manual detection widgets but don't display them (for compatibility)"""
        # Create a hidden frame as parent
        hidden_frame = tk.Frame(self.root)
        # Don't pack or grid the frame - widgets exist but aren't visible

        # Mode selector
        self.l_manual_set_or_not = tk.Label(hidden_frame, text=t("manual_set_or_not"), font=FONT_LABEL)
        self.e_manual_set_or_not = ttk.Combobox(
            hidden_frame, values=(t("no"), t("yes")), font=FONT_NORMAL, width=10
        )
        self.e_manual_set_or_not.current(0)

        # Second inputs
        self.l_manual_set_second = tk.Label(hidden_frame, text=t("manual_set_second"), font=FONT_LABEL)
        self.e_manual_set_second_1 = tk.Entry(hidden_frame, font=FONT_NORMAL, width=10)
        self.e_manual_set_second_2 = tk.Entry(hidden_frame, font=FONT_NORMAL, width=10)

        # Action buttons
        self.b_manual_set = tk.Button(hidden_frame, text=t("manual_set"), font=FONT_BUTTON)
        self.b_manual_set_sample = tk.Button(hidden_frame, text=t("sample_images"), font=FONT_BUTTON)
        self.b_manual_set_save = tk.Button(hidden_frame, text=t("save_detection_points"), font=FONT_BUTTON)

        # Coordinate display labels
        self._create_coordinate_labels_hidden(hidden_frame)

        # Frame references
        self.l_frame_desc = tk.Label(hidden_frame, text=t("refer_sample"), font=FONT_LABEL)
        self.l_frame_1_desc = tk.Label(hidden_frame, text=t("frame_1_desc"), font=FONT_LABEL)
        self.l_frame_2_desc = tk.Label(hidden_frame, text=t("frame_2_desc"), font=FONT_LABEL)

    def _create_coordinate_labels_hidden(self, parent):
        """Create coordinate display labels for detection points (hidden)"""
        self.l_acc_right = tk.Label(parent, text="y,x", font=FONT_LABEL)
        self.l_acc_left = tk.Label(parent, text="y,x", font=FONT_LABEL)
        self.l_pause_middle = tk.Label(parent, text="y,x", font=FONT_LABEL)
        self.l_pause_left = tk.Label(parent, text="y,x", font=FONT_LABEL)
        self.l_middle_pause_left = tk.Label(parent, text="y,x", font=FONT_LABEL)
        self.l_middle_pause_middle_2 = tk.Label(parent, text="y,x", font=FONT_LABEL)
        self.l_middle_pause_middle = tk.Label(parent, text="y,x", font=FONT_LABEL)
        self.l_middle_pause_right = tk.Label(parent, text="y,x", font=FONT_LABEL)
        self.l_valid_pause = tk.Label(parent, text="y,x1,x2,x3,x4", font=FONT_LABEL)

    def _create_margin_section(self, parent):
        """Create margin settings section"""
        margin_frame = ttk.LabelFrame(parent, text=t("margin_section"))

        self.l_top_margin = tk.Label(margin_frame, text=t("top_margin"), font=FONT_LABEL)
        self.e_top_margin = tk.Entry(margin_frame, font=FONT_NORMAL)

        self.l_bottom_margin = tk.Label(margin_frame, text=t("bottom_margin"), font=FONT_LABEL)
        self.e_bottom_margin = tk.Entry(margin_frame, font=FONT_NORMAL)

        self.l_left_margin = tk.Label(margin_frame, text=t("left_margin"), font=FONT_LABEL)
        self.e_left_margin = tk.Entry(margin_frame, font=FONT_NORMAL)

        self.l_right_margin = tk.Label(margin_frame, text=t("right_margin"), font=FONT_LABEL)
        self.e_right_margin = tk.Entry(margin_frame, font=FONT_NORMAL)

        # 2x4 grid layout
        self.l_top_margin.grid(row=0, column=0, sticky="e", padx=10, pady=3)
        self.e_top_margin.grid(row=0, column=1, sticky="ew", padx=5, pady=3)
        self.l_bottom_margin.grid(row=1, column=0, sticky="e", padx=10, pady=3)
        self.e_bottom_margin.grid(row=1, column=1, sticky="ew", padx=5, pady=3)
        self.l_left_margin.grid(row=2, column=0, sticky="e", padx=10, pady=3)
        self.e_left_margin.grid(row=2, column=1, sticky="ew", padx=5, pady=3)
        self.l_right_margin.grid(row=3, column=0, sticky="e", padx=10, pady=3)
        self.e_right_margin.grid(row=3, column=1, sticky="ew", padx=5, pady=3)

        margin_frame.columnconfigure(1, weight=1)
        return margin_frame

    def _create_processing_section(self, parent):
        """Create processing settings section"""
        processing_frame = ttk.LabelFrame(parent, text=t("processing_settings"))

        self.l_thread_num = tk.Label(processing_frame, text=t("thread_num"), font=FONT_LABEL)
        self.e_thread_num = tk.Entry(processing_frame, font=FONT_NORMAL)

        self.l_ignore_frame_cnt = tk.Label(processing_frame, text=t("ignore_frame_cnt"), font=FONT_LABEL)
        self.e_ignore_frame_cnt = tk.Entry(processing_frame, font=FONT_NORMAL)

        self.l_thread_num.grid(row=0, column=0, sticky="e", padx=10, pady=3)
        self.e_thread_num.grid(row=0, column=1, sticky="ew", padx=5, pady=3)
        self.l_ignore_frame_cnt.grid(row=1, column=0, sticky="e", padx=10, pady=3)
        self.e_ignore_frame_cnt.grid(row=1, column=1, sticky="ew", padx=5, pady=3)

        self.b_save_settings = tk.Button(processing_frame, text=t("save_settings"), font=FONT_BUTTON)
        self.b_save_settings.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        processing_frame.columnconfigure(1, weight=1)
        return processing_frame

    def _create_crop_section(self):
        """Create crop actions section"""
        crop_frame = ttk.LabelFrame(self.main_container, text=t("crop_actions"))
        crop_frame.pack(fill="x", expand=False, padx=5, pady=5)

        self.l_measure_margin_second = tk.Label(crop_frame, text=t("measure_margin_second"), font=FONT_LABEL)
        self.e_measure_margin_second = tk.Entry(crop_frame, font=FONT_NORMAL)

        self.b_measure_margin = tk.Button(crop_frame, text=t("measure_margin"), font=FONT_BUTTON)
        self.b_crop = tk.Button(crop_frame, text=t("crop_btn"), font=FONT_BUTTON)

        self.l_measure_margin_second.grid(row=0, column=0, sticky="e", padx=10, pady=3)
        self.e_measure_margin_second.grid(row=0, column=1, sticky="ew", padx=5, pady=3)
        self.b_measure_margin.grid(row=1, column=0, sticky="ew", padx=5, pady=3)
        self.b_crop.grid(row=1, column=1, sticky="ew", padx=5, pady=3)

        crop_frame.columnconfigure(1, weight=1)

    def _create_process_section(self):
        """Create process actions section"""
        process_frame = ttk.LabelFrame(self.main_container, text=t("process_actions"))
        process_frame.pack(fill="x", expand=False, padx=5, pady=5)

        self.l_start_second = tk.Label(process_frame, text=t("start_second"), font=FONT_LABEL)
        self.e_start_second = tk.Entry(process_frame, font=FONT_NORMAL)

        self.l_end_second = tk.Label(process_frame, text=t("end_second"), font=FONT_LABEL)
        self.e_end_second = tk.Entry(process_frame, font=FONT_NORMAL)

        self.b_cut_without_crop = tk.Button(process_frame, text=t("start_without_crop"), font=FONT_BUTTON)
        self.b_cut_with_crop = tk.Button(process_frame, text=t("start_with_crop"), font=FONT_BUTTON)

        self.l_start_second.grid(row=0, column=0, sticky="e", padx=10, pady=3)
        self.e_start_second.grid(row=0, column=1, sticky="ew", padx=5, pady=3)
        self.l_end_second.grid(row=1, column=0, sticky="e", padx=10, pady=3)
        self.e_end_second.grid(row=1, column=1, sticky="ew", padx=5, pady=3)
        self.b_cut_without_crop.grid(row=2, column=0, sticky="ew", padx=5, pady=3)
        self.b_cut_with_crop.grid(row=2, column=1, sticky="ew", padx=5, pady=3)

        process_frame.columnconfigure(1, weight=1)

    def _create_tutorial_section(self):
        """Create tutorial section"""
        tutorial_frame = ttk.Frame(self.main_container)
        tutorial_frame.pack(fill="x", expand=False, padx=5, pady=5)

        self.l_tutorial = tk.Label(tutorial_frame, text=t("tutorial"), font=FONT_LABEL)
        self.l_tutorial_url = tk.Label(
            tutorial_frame, text="www.bilibili.com/video/BV1qg411r7dV",
            font=FONT_LINK, fg="blue"
        )

        self.l_tutorial.grid(row=0, column=0, sticky="e", padx=10, pady=3)
        self.l_tutorial_url.grid(row=0, column=1, sticky="w", padx=5, pady=3)

        tutorial_frame.columnconfigure(1, weight=1)

    # ===== Widget update methods for callbacks =====

    def set_margin(self, top, bottom, left, right):
        """Update margin entry values"""
        self.e_top_margin.delete(0, tk.END)
        self.e_top_margin.insert(0, str(top))
        self.e_bottom_margin.delete(0, tk.END)
        self.e_bottom_margin.insert(0, str(bottom))
        self.e_left_margin.delete(0, tk.END)
        self.e_left_margin.insert(0, str(left))
        self.e_right_margin.delete(0, tk.END)
        self.e_right_margin.insert(0, str(right))

    def set_thread_num(self, num):
        """Update thread num entry"""
        self.e_thread_num.delete(0, tk.END)
        self.e_thread_num.insert(0, str(num))

    def set_ignore_frame_cnt(self, cnt):
        """Update ignore frame count entry"""
        self.e_ignore_frame_cnt.delete(0, tk.END)
        self.e_ignore_frame_cnt.insert(0, str(cnt))

    def set_coordinates(self, pause_middle, pause_left, acc_left, acc_right,
                       middle_pause_left, middle_pause_middle_2, middle_pause_middle,
                       middle_pause_right, valid_pause):
        """Update coordinate display labels"""
        self.l_pause_middle.config(text=pause_middle)
        self.l_pause_left.config(text=pause_left)
        self.l_acc_left.config(text=acc_left)
        self.l_acc_right.config(text=acc_right)
        self.l_middle_pause_left.config(text=middle_pause_left)
        self.l_middle_pause_middle_2.config(text=middle_pause_middle_2)
        self.l_middle_pause_middle.config(text=middle_pause_middle)
        self.l_middle_pause_right.config(text=middle_pause_right)
        self.l_valid_pause.config(text=valid_pause)

    def show_description_labels(self):
        """Show mode description labels in mode section"""
        mode_idx = self.e_mode.current()
        if mode_idx in [2, 3]:  # Lazy mode
            self.description_labels[0].config(text=t("lazy_mode_desc1"))
            self.description_labels[1].config(text=t("lazy_mode_desc2"))
            self.description_labels[2].config(text=t("lazy_mode_desc3"))
        else:  # Normal mode
            self.description_labels[0].config(text=t("normal_mode_desc1"))
            self.description_labels[1].config(text=t("normal_mode_desc2"))
            self.description_labels[2].config(text=t("normal_mode_desc3"))

        # Show all labels
        for lbl in self.description_labels:
            lbl.grid()

    def update_all_text(self):
        """Update all widget text when language changes"""
        self.root.title(t("window_title"))
        self.l_text_working_path.config(text=t("current_working_dir"))
        self.l_language.config(text=t("language"))
        self.l_theme.config(text=t("theme"))
        self.l_mode.config(text=t("select_mode"))
        self.b_show_desc.config(text=t("show_desc"))

        # Update theme combobox
        current_theme_idx = self.e_theme.current()
        self.e_theme["values"] = [t("auto"), t("light"), t("dark")]
        if 0 <= current_theme_idx < 3:
            self.e_theme.current(current_theme_idx)

        # Update mode combobox
        update_combobox_preserve_selection(
            self.e_mode,
            "mode_normal_audio_only",
            "mode_normal_keep_video",
            "mode_lazy_keep_valid",
            "mode_lazy_cut_all"
        )

        # Update margin labels and section title
        self.mode_frame.config(text=t("select_mode"))
        self.l_top_margin.config(text=t("top_margin"))
        self.l_bottom_margin.config(text=t("bottom_margin"))
        self.l_left_margin.config(text=t("left_margin"))
        self.l_right_margin.config(text=t("right_margin"))

        # Update thread/ignore labels and section title
        self.l_thread_num.config(text=t("thread_num"))
        self.l_ignore_frame_cnt.config(text=t("ignore_frame_cnt"))

        # Update button
        self.b_save_settings.config(text=t("save_settings"))

        # Update measure/cut labels and buttons and section title
        self.l_measure_margin_second.config(text=t("measure_margin_second"))
        self.b_measure_margin.config(text=t("measure_margin"))
        self.b_crop.config(text=t("crop_btn"))

        # Update start/end labels and section title
        self.l_start_second.config(text=t("start_second"))
        self.l_end_second.config(text=t("end_second"))

        # Update action buttons and section title
        self.b_cut_without_crop.config(text=t("start_without_crop"))
        self.b_cut_with_crop.config(text=t("start_with_crop"))

        # Update tutorial
        self.l_tutorial.config(text=t("tutorial"))

        # Update manual detection labels and section title
        self.l_manual_set_or_not.config(text=t("manual_set_or_not"))
        update_combobox_preserve_selection(self.e_manual_set_or_not, "no", "yes")
        self.l_manual_set_second.config(text=t("manual_set_second"))
        self.b_manual_set.config(text=t("manual_set"))
        self.b_manual_set_sample.config(text=t("sample_images"))
        self.b_manual_set_save.config(text=t("save_detection_points"))
        self.l_frame_desc.config(text=t("refer_sample"))
        self.l_frame_1_desc.config(text=t("frame_1_desc"))
        self.l_frame_2_desc.config(text=t("frame_2_desc"))

        # Update section titles
        # Need to get references to the section frames
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.LabelFrame):
                title = widget.cget("text")
                if title == t("margin_section") or title == "边距设置" or title == "Margin Settings":
                    widget.config(text=t("margin_section"))
                elif title == t("manual_detection") or title == "手动检测点" or title == "Manual Detection":
                    widget.config(text=t("manual_detection"))
                elif title == t("processing_settings") or title == "处理设置" or title == "Processing Settings":
                    widget.config(text=t("processing_settings"))
                elif title == t("crop_actions") or title == "裁剪操作" or title == "Crop Actions":
                    widget.config(text=t("crop_actions"))
                elif title == t("process_actions") or title == "处理操作" or title == "Process Actions":
                    widget.config(text=t("process_actions"))
