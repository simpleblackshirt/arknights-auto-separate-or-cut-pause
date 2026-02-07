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
        "input_fg": "#000000",
        "path_bg": "#e0e0e0",
        "link_fg": "#0066cc",
        "border_color": "#cccccc",
        "button_bg": "#e8e8e8",
        "button_active_bg": "#d0d0d0",
        "input_disabled_bg": "#e0e0e0",
    },
    "dark": {
        "bg": "#1a1a1e",
        "fg": "#cccccc",
        "input_bg": "#2F3136",
        "input_fg": "#cccccc",
        "path_bg": "#222327",
        "link_fg": "#66b3ff",
        "border_color": "#2b2b2f",
        "button_bg": "#121214",
        "button_active_bg": "#232325",
        "input_disabled_bg": "#222327",
    }
}

# Font constants
FONT_NORMAL = ("TkDefaultFont", 10)
FONT_LABEL = ("TkDefaultFont", 10)
FONT_FRAME = ("TkDefaultFont", 8)
FONT_BUTTON = ("TkDefaultFont", 10)
FONT_LINK = ("TkDefaultFont", 10, "underline")


class MainWindow:
    def __init__(self, root, working_path, default_language="cn"):
        self.root = root
        self.working_path = working_path
        self.default_language = default_language
        self.theme_mode = "auto"  # "auto", "light", or "dark"

        # Track themeable widgets
        self.themeable_labels = []  # All tk.Label widgets
        self.themeable_buttons = []  # All tk.Button widgets
        self.themeable_frames = []  # All Frame widgets
        self.button_border_frames = []  # Border frames for buttons

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

        # Update all themeable labels
        for lbl in self.themeable_labels:
            try:
                lbl.configure(bg=theme["bg"], fg=theme["fg"])
            except Exception:
                pass

        # Update all themeable buttons
        for btn in self.themeable_buttons:
            try:
                btn.configure(
                    bg=theme["button_bg"],
                    fg=theme["fg"],
                    activebackground=theme["button_active_bg"],
                    activeforeground=theme["fg"],
                    relief="flat",
                    borderwidth=0,
                    highlightthickness=0
                )
            except Exception:
                pass

        # Update all button border frames
        for frame in self.button_border_frames:
            try:
                frame.configure(
                    bg=theme["button_bg"],
                    highlightbackground=theme["border_color"],
                    highlightcolor=theme["border_color"],
                    highlightthickness=1
                )
            except Exception:
                pass

        # Update all themeable frames
        for frame in self.themeable_frames:
            try:
                frame.configure(bg=theme["bg"])
            except Exception:
                pass

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
                    getattr(self, widget_name).configure(
                        bg=theme["input_bg"],
                        disabledbackground=theme["input_disabled_bg"],
                        fg=theme["input_fg"],
                        insertbackground=theme["input_fg"],
                        relief="flat",
                        borderwidth=0,
                        highlightthickness=0,
                    )
                except Exception:
                    pass

        # Update path label with special background
        if hasattr(self, 'l_working_path'):
            try:
                self.l_working_path.configure(bg=theme["path_bg"], fg=theme["fg"])
            except Exception:
                pass

        # Update tutorial link color
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

    def _create_bordered_button(self, parent, text, command=None, font=FONT_BUTTON, width=None):
        """Create a button with a themed border frame.
        Returns a tuple of (border_frame, button).
        The border_frame should be used for layout (grid/pack).
        """
        theme = THEMES[self.get_effective_theme()]
        border_frame = tk.Frame(parent, bg=theme["button_bg"])
        self.themeable_frames.append(border_frame)
        self.button_border_frames.append(border_frame)

        button = tk.Button(border_frame, text=text, font=font, command=command,
                          bg=theme["button_bg"], fg=theme["fg"],
                          activebackground=theme["button_active_bg"],
                          activeforeground=theme["fg"], relief="flat",
                          borderwidth=0, highlightthickness=0, width=width)
        self.themeable_buttons.append(button)

        # Pack button inside border frame with no gaps
        button.pack(fill="both", expand=True, padx=1, pady=1)

        return border_frame, button

    def _create_info_button(self, parent, command):
        """Create a circular info button with 'i' text.
        Returns a tuple of (frame, label). The frame should be used for layout.
        """
        theme = THEMES[self.get_effective_theme()]
        size = 20

        # Frame with circular border effect
        frame = tk.Frame(parent, width=size, height=size, bg=theme["bg"])
        frame.pack_propagate(False)

        # Circular effect using border (not perfect but works)
        border = tk.Frame(frame, width=size-2, height=size-2,
                         bg=theme["border_color"],
                         highlightbackground=theme["border_color"],
                         highlightthickness=1)
        border.pack_propagate(False)
        border.pack()  # THIS WAS MISSING - pack the border into the frame

        # Info label
        info_label = tk.Label(border, text="i", font=("TkDefaultFont", 10, "bold"),
                             bg=theme["button_bg"], fg=theme["fg"],
                             cursor="hand2")
        info_label.pack(fill="both", expand=True)
        info_label.bind("<Button-1>", lambda _: command())

        self.themeable_frames.append(frame)
        self.themeable_frames.append(border)
        self.themeable_labels.append(info_label)
        self.button_border_frames.append(border)

        return frame, info_label

    def _create_widgets(self):
        """Create all UI widgets"""
        # Window setup
        self.root.title(t("window_title"))
        self.root.geometry("845x810+150+150")
        self.root.minsize(845, 810)

        # Set default combobox listbox font
        self.root.option_add("*TCombobox*Listbox.font", FONT_NORMAL)

        #Set default labelframe font
        self.root.option_add("*LabelFrame.font", FONT_FRAME)

        # Create main container for centered content
        self.main_container = tk.Frame(self.root)
        self.themeable_frames.append(self.main_container)
        self.main_container.pack(expand=True, fill="both", padx=20, pady=20)

        # ===== HEADER SECTION =====
        self._create_header_section()

        # ===== MODE SECTION =====
        self._create_mode_section()

        # ===== MANUAL DETECTION SECTION =====
        self._create_manual_detection_section()

        # ===== TWO COLUMN SECTION (Margin + Processing) =====
        self._create_two_column_section()

        # ===== CROP ACTIONS SECTION =====
        self._create_crop_section()

        # ===== PROCESS ACTIONS SECTION =====
        self._create_process_section()

        # ===== TUTORIAL SECTION =====
        self._create_tutorial_section()

    def _create_header_section(self):
        """Create header section with working path, language, and theme"""
        header_frame = tk.Frame(self.main_container)
        self.themeable_frames.append(header_frame)
        header_frame.pack(fill="x", expand=False, padx=5, pady=(5, 0))

        # Working path row
        self.l_text_working_path = tk.Label(
            header_frame, text=t("current_working_dir"), font=FONT_LABEL
        )
        self.themeable_labels.append(self.l_text_working_path)
        self.l_working_path = tk.Label(
            header_frame, text=self.working_path, font=FONT_LABEL
        )
        self.themeable_labels.append(self.l_working_path)

        self.l_text_working_path.grid(row=0, column=0, sticky="e", padx=10, pady=5)
        self.l_working_path.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Language and theme row - place in their own frame for proper alignment
        lang_theme_frame = tk.Frame(header_frame)
        self.themeable_frames.append(lang_theme_frame)
        lang_theme_frame.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        self.l_language = tk.Label(lang_theme_frame, text=t("language"), font=FONT_LABEL)
        self.themeable_labels.append(self.l_language)
        self.e_language = ttk.Combobox(lang_theme_frame, values=["中文", "English", "日本語"], font=FONT_NORMAL, width=10)
        self.e_language.current(0 if self.default_language == "cn" else 1 if self.default_language == "en" else 2)

        self.l_theme = tk.Label(lang_theme_frame, text=t("theme"), font=FONT_LABEL)
        self.themeable_labels.append(self.l_theme)
        self.e_theme = ttk.Combobox(
            lang_theme_frame, values=[t("auto"), t("light"), t("dark")], font=FONT_NORMAL, width=10
        )
        self.e_theme.current(0)
        self.e_theme.bind("<<ComboboxSelected>>", self.change_theme)

        self.l_language.grid(row=0, column=0, sticky="e", padx=(0, 10), pady=5)
        self.e_language.grid(row=0, column=1, sticky="w", padx=(0, 20), pady=5)
        self.l_theme.grid(row=0, column=2, sticky="e", padx=(0, 10), pady=5)
        self.e_theme.grid(row=0, column=3, sticky="w", padx=0, pady=5)

    def _create_mode_section(self):
        """Create mode selection section"""
        self.mode_frame = tk.LabelFrame(self.main_container, text=t("select_mode"), padx=5, pady=5)
        self.themeable_labels.append(self.mode_frame)
        self.mode_frame.pack(fill="x", expand=False, padx=5, pady=5)

        # Mode dropdown and show description button
        self.l_mode = tk.Label(self.mode_frame, text=t("select_mode"), font=FONT_LABEL)
        self.themeable_labels.append(self.l_mode)
        self.e_mode = ttk.Combobox(self.mode_frame, font=FONT_NORMAL, width=35)
        self.e_mode["value"] = (
            t("mode_normal_audio_only"),
            t("mode_normal_keep_video"),
            t("mode_lazy_keep_valid"),
            t("mode_lazy_cut_all")
        )
        self.e_mode.current(1)
        self.b_show_desc_frame, self.b_show_desc = self._create_bordered_button(
            self.mode_frame, text=t("show_desc")
        )

        self.l_mode.grid(row=0, column=0, sticky="e", padx=10, pady=5)
        self.e_mode.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.b_show_desc_frame.grid(row=0, column=2, sticky="ew", padx=10, pady=(5, 10))

        self.mode_frame.columnconfigure(1, weight=1)

    def _create_two_column_section(self):
        """Create two-column section with margin and processing settings"""
        two_col_container = tk.Frame(self.main_container)
        self.themeable_frames.append(two_col_container)
        two_col_container.pack(fill="both", expand=False, padx=5, pady=0)

        # Left column - Margin Section
        self.margin_frame = self._create_margin_section(two_col_container)
        self.margin_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)

        # Right column - Processing Section
        self.processing_frame = self._create_processing_section(two_col_container)
        self.processing_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)

        # Equal column weights
        two_col_container.columnconfigure(0, weight=1)
        two_col_container.columnconfigure(1, weight=1)

    def _create_manual_detection_section(self):
        """Create manual detection section"""
        manual_frame = tk.LabelFrame(self.main_container, text=t("manual_detection"), padx=5, pady=5)
        self.themeable_labels.append(manual_frame)
        manual_frame.pack(fill="x", expand=False, padx=5, pady=5)

        # Grid layout configuration
        manual_frame.columnconfigure(1, weight=1)
        manual_frame.columnconfigure(2, weight=1)

        # Row 0: Mode selector
        self.l_manual_set_or_not = tk.Label(manual_frame, text=t("manual_set_or_not"), font=FONT_LABEL)
        self.themeable_labels.append(self.l_manual_set_or_not)
        self.e_manual_set_or_not = ttk.Combobox(
            manual_frame, values=(t("no"), t("yes")), font=FONT_NORMAL, width=10
        )
        self.e_manual_set_or_not.current(0)

        self.l_manual_set_or_not.grid(row=0, column=0, sticky="e", padx=10, pady=5)
        self.e_manual_set_or_not.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        self.l_frame_desc = tk.Label(manual_frame, text=f"({t('refer_sample')})", font=FONT_LABEL)
        self.themeable_labels.append(self.l_frame_desc)
        self.l_frame_desc.grid(row=0, column=2, sticky="w", padx=(10, 0), pady=5)

        # Row 1: Second inputs
        self.l_manual_set_second = tk.Label(manual_frame, text=t("manual_set_second"), font=FONT_LABEL)
        self.themeable_labels.append(self.l_manual_set_second)
        self.e_manual_set_second_1 = tk.Entry(manual_frame, font=FONT_NORMAL, width=10)
        self.e_manual_set_second_2 = tk.Entry(manual_frame, font=FONT_NORMAL, width=10)

        self.l_manual_set_second.grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.e_manual_set_second_1.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.e_manual_set_second_2.grid(row=1, column=2, sticky="ew", padx=5, pady=5)

        # Row 2: Action buttons
        self.b_manual_set_frame, self.b_manual_set = self._create_bordered_button(
            manual_frame, text=t("manual_set")
        )
        self.b_manual_set_sample_frame, self.b_manual_set_sample = self._create_bordered_button(
            manual_frame, text=t("sample_images")
        )
        self.b_manual_set_save_frame, self.b_manual_set_save = self._create_bordered_button(
            manual_frame, text=t("save_detection_points")
        )

        self.b_manual_set_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.b_manual_set_sample_frame.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        self.b_manual_set_save_frame.grid(row=2, column=2, sticky="ew", padx=5, pady=5)

        # Row 3: Frame 1 description + array 1 coordinates (4 points)
        self.l_frame_1_desc = tk.Label(manual_frame, text=t("frame_1_desc"), font=FONT_LABEL)
        self.themeable_labels.append(self.l_frame_1_desc)
        self.l_frame_1_desc.grid(row=3, column=0, sticky="w", padx=10, pady=2)

        # Container for coordinate label + info button
        coord_1_container = tk.Frame(manual_frame)
        self.themeable_frames.append(coord_1_container)

        self.l_array_1_coords = tk.Label(coord_1_container, text="(x1, y1), (x2, y2), (x3, y3), (x4, y4)", font=FONT_LABEL)
        self.themeable_labels.append(self.l_array_1_coords)
        self.l_array_1_coords.pack(side="left")

        # Info button for 4 points
        info_1_btn_frame, _ = self._create_info_button(
            coord_1_container,
            command=lambda: self.show_instruction_popup(t("click_4_points"))
        )
        info_1_btn_frame.pack(side="left", padx=(5, 0))

        coord_1_container.grid(row=3, column=1, columnspan=2, sticky="w", padx=10, pady=2)

        # Row 4: Frame 2 description + array 2 coordinates (8 points)
        self.l_frame_2_desc = tk.Label(manual_frame, text=t("frame_2_desc"), font=FONT_LABEL)
        self.themeable_labels.append(self.l_frame_2_desc)
        self.l_frame_2_desc.grid(row=4, column=0, sticky="w", padx=10, pady=2)

        # Container for coordinate label + info button
        coord_2_container = tk.Frame(manual_frame)
        self.themeable_frames.append(coord_2_container)

        self.l_array_2_coords = tk.Label(coord_2_container, text="(x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5), (x6, y6), (x7, y7), (x8, y8)", font=FONT_LABEL)
        self.themeable_labels.append(self.l_array_2_coords)
        self.l_array_2_coords.pack(side="left")

        # Info button for 8 points
        info_2_btn_frame, _ = self._create_info_button(
            coord_2_container,
            command=lambda: self.show_instruction_popup(t("click_8_points"))
        )
        info_2_btn_frame.pack(side="left", padx=(5, 0))

        coord_2_container.grid(row=4, column=1, columnspan=2, sticky="w", padx=10, pady=(2, 10))

    def _create_margin_section(self, parent):
        """Create margin settings section"""
        margin_frame = tk.LabelFrame(parent, text=t("margin_section"), padx=5, pady=5)
        self.themeable_labels.append(margin_frame)

        self.l_top_margin = tk.Label(margin_frame, text=t("top_margin"), font=FONT_LABEL)
        self.themeable_labels.append(self.l_top_margin)
        self.e_top_margin = tk.Entry(margin_frame, font=FONT_NORMAL)

        self.l_bottom_margin = tk.Label(margin_frame, text=t("bottom_margin"), font=FONT_LABEL)
        self.themeable_labels.append(self.l_bottom_margin)
        self.e_bottom_margin = tk.Entry(margin_frame, font=FONT_NORMAL)

        self.l_left_margin = tk.Label(margin_frame, text=t("left_margin"), font=FONT_LABEL)
        self.themeable_labels.append(self.l_left_margin)
        self.e_left_margin = tk.Entry(margin_frame, font=FONT_NORMAL)

        self.l_right_margin = tk.Label(margin_frame, text=t("right_margin"), font=FONT_LABEL)
        self.themeable_labels.append(self.l_right_margin)
        self.e_right_margin = tk.Entry(margin_frame, font=FONT_NORMAL)

        # 2x4 grid layout
        self.l_top_margin.grid(row=0, column=0, sticky="e", padx=10, pady=3)
        self.e_top_margin.grid(row=0, column=1, sticky="ew", padx=5, pady=3)
        self.l_bottom_margin.grid(row=1, column=0, sticky="e", padx=10, pady=3)
        self.e_bottom_margin.grid(row=1, column=1, sticky="ew", padx=5, pady=3)
        self.l_left_margin.grid(row=2, column=0, sticky="e", padx=10, pady=3)
        self.e_left_margin.grid(row=2, column=1, sticky="ew", padx=5, pady=3)
        self.l_right_margin.grid(row=3, column=0, sticky="e", padx=10, pady=(3, 10))
        self.e_right_margin.grid(row=3, column=1, sticky="ew", padx=5, pady=(3, 10))

        margin_frame.columnconfigure(1, weight=1)
        return margin_frame

    def _create_processing_section(self, parent):
        """Create processing settings section"""
        processing_frame = tk.LabelFrame(parent, text=t("processing_settings"), padx=5, pady=5)
        self.themeable_labels.append(processing_frame)

        self.l_thread_num = tk.Label(processing_frame, text=t("thread_num"), font=FONT_LABEL)
        self.themeable_labels.append(self.l_thread_num)
        self.e_thread_num = tk.Entry(processing_frame, font=FONT_NORMAL)

        self.l_ignore_frame_cnt = tk.Label(processing_frame, text=t("ignore_frame_cnt"), font=FONT_LABEL)
        self.themeable_labels.append(self.l_ignore_frame_cnt)
        self.e_ignore_frame_cnt = tk.Entry(processing_frame, font=FONT_NORMAL)

        self.l_thread_num.grid(row=0, column=0, sticky="e", padx=10, pady=3)
        self.e_thread_num.grid(row=0, column=1, sticky="ew", padx=5, pady=3)
        self.l_ignore_frame_cnt.grid(row=1, column=0, sticky="e", padx=10, pady=3)
        self.e_ignore_frame_cnt.grid(row=1, column=1, sticky="ew", padx=5, pady=3)

        # Add spacer row to push button to bottom
        processing_frame.rowconfigure(3, weight=1)

        self.b_save_settings_frame, self.b_save_settings = self._create_bordered_button(
            processing_frame, text=t("save_settings")
        )
        self.b_save_settings_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))

        processing_frame.columnconfigure(1, weight=1)
        return processing_frame

    def _create_crop_section(self):
        """Create crop actions section"""
        self.crop_frame = tk.LabelFrame(self.main_container, text=t("crop_actions"), padx=5, pady=5)
        self.themeable_labels.append(self.crop_frame)
        self.crop_frame.pack(fill="x", expand=False, padx=5, pady=5)

        self.l_measure_margin_second = tk.Label(self.crop_frame, text=t("measure_margin_second"), font=FONT_LABEL)
        self.themeable_labels.append(self.l_measure_margin_second)
        self.e_measure_margin_second = tk.Entry(self.crop_frame, font=FONT_NORMAL)

        self.b_measure_margin_frame, self.b_measure_margin = self._create_bordered_button(
            self.crop_frame, text=t("measure_margin")
        )
        self.b_crop_frame, self.b_crop = self._create_bordered_button(
            self.crop_frame, text=t("crop_btn")
        )

        self.l_measure_margin_second.grid(row=0, column=0, sticky="e", padx=10, pady=3)
        self.e_measure_margin_second.grid(row=0, column=1, sticky="ew", padx=5, pady=3)
        self.b_measure_margin_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=(3, 10))
        self.b_crop_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=(3, 10))

        self.crop_frame.columnconfigure(1, weight=1)

    def _create_process_section(self):
        """Create process actions section"""
        self.process_frame = tk.LabelFrame(self.main_container, text=t("process_actions"), padx=5, pady=5)
        self.themeable_labels.append(self.process_frame)
        self.process_frame.pack(fill="x", expand=False, padx=5, pady=5)

        self.l_start_second = tk.Label(self.process_frame, text=t("start_second"), font=FONT_LABEL)
        self.themeable_labels.append(self.l_start_second)
        self.e_start_second = tk.Entry(self.process_frame, font=FONT_NORMAL, width=20)

        self.l_end_second = tk.Label(self.process_frame, text=t("end_second"), font=FONT_LABEL)
        self.themeable_labels.append(self.l_end_second)
        self.e_end_second = tk.Entry(self.process_frame, font=FONT_NORMAL, width=20)

        self.b_cut_without_crop_frame, self.b_cut_without_crop = self._create_bordered_button(
            self.process_frame, text=t("start_without_crop")
        )
        self.b_cut_with_crop_frame, self.b_cut_with_crop = self._create_bordered_button(
            self.process_frame, text=t("start_with_crop")
        )

        self.l_start_second.grid(row=0, column=0, sticky="e", padx=10, pady=3)
        self.e_start_second.grid(row=0, column=1, sticky="w", padx=5, pady=3)
        self.l_end_second.grid(row=1, column=0, sticky="e", padx=10, pady=(3, 10))
        self.e_end_second.grid(row=1, column=1, sticky="w", padx=5, pady=(3, 10))
        self.b_cut_without_crop_frame.grid(row=0, column=2, sticky="ew", padx=5, pady=3)
        self.b_cut_with_crop_frame.grid(row=1, column=2, sticky="ew", padx=5, pady=(3, 10))

        self.process_frame.columnconfigure(2, weight=1)

    def _create_tutorial_section(self):
        """Create tutorial section"""
        tutorial_frame = tk.Frame(self.main_container)
        self.themeable_frames.append(tutorial_frame)
        tutorial_frame.pack(fill="x", expand=False, padx=5, pady=(0, 5))

        self.l_tutorial = tk.Label(tutorial_frame, text=t("tutorial"), font=FONT_LABEL)
        self.themeable_labels.append(self.l_tutorial)
        self.l_tutorial_url = tk.Label(
            tutorial_frame, text="www.bilibili.com/video/BV1qg411r7dV",
            font=FONT_LINK, fg="blue"
        )
        self.themeable_labels.append(self.l_tutorial_url)

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

    def set_coordinates(self, array_1_coords, array_2_coords):
        """Update coordinate display labels with formatted coordinate strings"""
        self.l_array_1_coords.config(text=array_1_coords)
        self.l_array_2_coords.config(text=array_2_coords)

    def show_description_labels(self):
        """Show mode description in a popup window"""
        mode_idx = self.e_mode.current()

        # Get description lines based on mode
        if mode_idx in [2, 3]:  # Lazy mode
            desc_lines = [
                t("lazy_mode_desc1"),
                t("lazy_mode_desc2"),
                t("lazy_mode_desc3")
            ]
        else:  # Normal mode
            desc_lines = [
                t("normal_mode_desc1"),
                t("normal_mode_desc2"),
                t("normal_mode_desc3")
            ]

        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title(t("show_desc"))
        popup.geometry("500x200")
        popup.resizable(False, False)

        # Get current theme colors
        theme = THEMES[self.get_effective_theme()]

        # Configure popup background
        popup.configure(bg=theme["bg"])

        # Container frame
        container = tk.Frame(popup, bg=theme["bg"], padx=20, pady=20)
        container.pack(fill="both", expand=True)

        # Description label
        desc_text = "\n\n".join(desc_lines)
        desc_label = tk.Label(
            container,
            text=desc_text,
            font=FONT_LABEL,
            justify="left",
            bg=theme["bg"],
            fg=theme["fg"],
            wraplength=450
        )
        desc_label.pack(fill="both", expand=True)

        # Close button
        close_btn_frame, close_btn = self._create_bordered_button(
            container, text=t("close")
        )
        close_btn.config(command=popup.destroy)
        close_btn_frame.pack(pady=(10, 0))

    def show_instruction_popup(self, instruction_text, button_text="close"):
        """Show instruction text in a themed popup window (modal)

        Args:
            instruction_text: The text to display
            button_text: The translation key for the button text ("close" or "proceed")
        """
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title(t("info_title"))
        popup.geometry("540x280")
        popup.resizable(False, False)

        # Make popup modal (blocking)
        popup.transient(self.root)
        popup.grab_set()

        # Get current theme colors
        theme = THEMES[self.get_effective_theme()]

        # Configure popup background
        popup.configure(bg=theme["bg"])

        # Container frame with less padding
        container = tk.Frame(popup, bg=theme["bg"], padx=15, pady=15)
        container.pack(fill="both", expand=True)

        # Instruction label
        instruction_label = tk.Label(
            container,
            text=instruction_text,
            font=FONT_LABEL,
            justify="left",
            bg=theme["bg"],
            fg=theme["fg"],
            wraplength=460
        )
        instruction_label.pack(fill="both", expand=True)

        # Action button
        action_btn_frame, action_btn = self._create_bordered_button(
            container, text=t(button_text)
        )
        action_btn.config(command=popup.destroy)
        action_btn_frame.pack(pady=(10, 0))

        # Center popup on parent and wait for close
        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - popup.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")

        # Wait for popup to be closed (makes it truly modal)
        popup.wait_window()

    def show_settings_saved_popup(self):
        """Show settings saved confirmation in a themed popup window (modal)"""
        popup = tk.Toplevel(self.root)
        popup.title(t("info_title"))
        popup.geometry("300x120")

        # Make popup modal
        popup.transient(self.root)
        popup.grab_set()

        # Get current theme colors
        theme = THEMES[self.get_effective_theme()]

        # Configure popup background
        popup.configure(bg=theme["bg"])

        # Container frame with theme
        container = tk.Frame(popup, bg=theme["bg"], padx=20, pady=20)
        container.pack(fill="both", expand=True)

        # Message label with theme
        msg_label = tk.Label(
            container,
            text=t("settings_saved"),
            font=FONT_LABEL,
            bg=theme["bg"],
            fg=theme["fg"]
        )
        msg_label.pack(fill="both", expand=True)

        # Close button with theme
        close_btn_frame, close_btn = self._create_bordered_button(
            container, text=t("close")
        )
        close_btn_frame.pack(pady=(10, 0))
        close_btn.config(command=popup.destroy)

        # Center popup on parent
        popup.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - popup.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")

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
        self.mode_frame.config(text=t("select_mode"))
        self.margin_frame.config(text=t("margin_section"))
        self.processing_frame.config(text=t("processing_settings"))
        self.crop_frame.config(text=t("crop_actions"))
        self.process_frame.config(text=t("process_actions"))
