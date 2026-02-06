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


class MainWindow:
    def __init__(self, root, working_path, default_language="cn"):
        self.root = root
        self.working_path = working_path
        self.default_language = default_language
        self.theme_mode = "auto"  # "auto", "light", or "dark"
        self.description_labels = []  # Store description label references

        # Configure responsive grid
        self._setup_grid_config()

        # Create all widgets
        self._create_widgets()

        # Apply initial theme
        self.apply_theme()

    def _setup_grid_config(self):
        """Configure column and row weights for responsive layout"""
        # Columns: 0=label, 1=input(expand), 2=label, 3=control, 4=control, 5=theme
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.columnconfigure(2, weight=0)
        self.root.columnconfigure(3, weight=0)
        self.root.columnconfigure(4, weight=0)
        self.root.columnconfigure(5, weight=0)

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
        # dynamic width based on path length
        width = 1300 + len(self.working_path.encode("utf-8")) * 5
        self.root.geometry(f"{width}x900")

        # Set default combobox listbox font
        self.root.option_add("*TCombobox*Listbox.font", 20)

        # ===== ROW 0: Working Path + Language + Theme =====
        self.l_text_working_path = tk.Label(
            self.root, text=t("current_working_dir"), font=20, height=3
        )
        self.l_working_path = tk.Label(
            self.root, text=self.working_path, bg="lightgray", font=20, height=3
        )

        self.l_language = tk.Label(self.root, text=t("language"), font=20, height=2)
        self.e_language = ttk.Combobox(self.root, values=["中文", "English"], font=20, width=10)
        self.e_language.current(0 if self.default_language == "cn" else 1)

        self.l_theme = tk.Label(self.root, text=t("theme"), font=20, height=2)
        self.e_theme = ttk.Combobox(
            self.root, values=[t("auto"), t("light"), t("dark")], font=20, width=10
        )
        self.e_theme.current(0)
        self.e_theme.bind("<<ComboboxSelected>>", self.change_theme)

        # Grid row 0
        self.l_text_working_path.grid(row=0, column=0, sticky="e", padx=10, pady=5)
        self.l_working_path.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.l_language.grid(row=0, column=2, sticky="e", padx=10, pady=5)
        self.e_language.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        self.l_theme.grid(row=0, column=4, sticky="e", padx=10, pady=5)
        self.e_theme.grid(row=0, column=5, sticky="w", padx=5, pady=5)

        # ===== ROW 1: Mode + Show Description =====
        self.l_mode = tk.Label(self.root, text=t("select_mode"), font=20, height=3)
        self.e_mode = ttk.Combobox(self.root, font=20, height=4, width=28)
        self.e_mode["value"] = (
            t("mode_normal_audio_only"),
            t("mode_normal_keep_video"),
            t("mode_lazy_keep_valid"),
            t("mode_lazy_cut_all")
        )
        self.e_mode.current(1)
        self.b_show_desc = tk.Button(self.root, text=t("show_desc"), font=20)

        self.l_mode.grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.e_mode.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.b_show_desc.grid(row=1, column=2, columnspan=4, sticky="ew", padx=10, pady=5)

        # ===== ROWS 4-7: Margin Inputs (left column) =====
        self.l_top_margin = tk.Label(self.root, text=t("top_margin"), font=20, height=2)
        self.e_top_margin = tk.Entry(self.root, bg="white", font=20)

        self.l_bottom_margin = tk.Label(self.root, text=t("bottom_margin"), font=20, height=2)
        self.e_bottom_margin = tk.Entry(self.root, bg="white", font=20)

        self.l_left_margin = tk.Label(self.root, text=t("left_margin"), font=20, height=2)
        self.e_left_margin = tk.Entry(self.root, bg="white", font=20)

        self.l_right_margin = tk.Label(self.root, text=t("right_margin"), font=20, height=2)
        self.e_right_margin = tk.Entry(self.root, bg="white", font=20)

        # Grid margin inputs
        self.l_top_margin.grid(row=4, column=0, sticky="e", padx=10, pady=3)
        self.e_top_margin.grid(row=4, column=1, sticky="ew", padx=5, pady=3)
        self.l_bottom_margin.grid(row=5, column=0, sticky="e", padx=10, pady=3)
        self.e_bottom_margin.grid(row=5, column=1, sticky="ew", padx=5, pady=3)
        self.l_left_margin.grid(row=6, column=0, sticky="e", padx=10, pady=3)
        self.e_left_margin.grid(row=6, column=1, sticky="ew", padx=5, pady=3)
        self.l_right_margin.grid(row=7, column=0, sticky="e", padx=10, pady=3)
        self.e_right_margin.grid(row=7, column=1, sticky="ew", padx=5, pady=3)

        # ===== ROWS 4-7: Manual Detection Panel (right columns) =====
        self.l_manual_set_or_not = tk.Label(self.root, text=t("manual_set_or_not"), font=20, height=3)
        self.e_manual_set_or_not = ttk.Combobox(
            self.root, values=(t("no"), t("yes")), font=20, height=4, width=10
        )
        self.e_manual_set_or_not.current(0)

        self.l_manual_set_second = tk.Label(self.root, text=t("manual_set_second"), font=20, height=2)
        self.e_manual_set_second_1 = tk.Entry(self.root, bg="white", font=20, width=10)
        self.e_manual_set_second_2 = tk.Entry(self.root, bg="white", font=20, width=10)

        self.b_manual_set = tk.Button(self.root, text=t("manual_set"), font=20)
        self.b_manual_set_sample = tk.Button(self.root, text=t("sample_images"), font=20)
        self.b_manual_set_save = tk.Button(self.root, text=t("save_detection_points"), font=20)

        # Coordinate display labels
        self.l_acc_right = tk.Label(self.root, text="y,x", font=20, height=2)
        self.l_acc_left = tk.Label(self.root, text="y,x", font=20, height=2)

        self.l_frame_desc = tk.Label(self.root, text=t("refer_sample"), font=20, height=2)
        self.l_frame_1_desc = tk.Label(self.root, text=t("frame_1_desc"), font=20, height=2)
        self.l_frame_2_desc = tk.Label(self.root, text=t("frame_2_desc"), font=20, height=2)

        self.l_pause_middle = tk.Label(self.root, text="y,x", font=20, height=2)
        self.l_pause_left = tk.Label(self.root, text="y,x", font=20, height=2)

        self.l_middle_pause_left = tk.Label(self.root, text="y,x", font=20, height=2)
        self.l_middle_pause_middle_2 = tk.Label(self.root, text="y,x", font=20, height=2)
        self.l_middle_pause_middle = tk.Label(self.root, text="y,x", font=20, height=2)
        self.l_middle_pause_right = tk.Label(self.root, text="y,x", font=20, height=2)

        self.l_valid_pause = tk.Label(self.root, text="y,x1,x2,x3,x4", font=20, height=2)

        # Grid manual detection (rows 4-15, columns 2-4)
        self.l_manual_set_or_not.grid(row=4, column=2, sticky="e", padx=10, pady=3)
        self.e_manual_set_or_not.grid(row=4, column=3, sticky="w", padx=5, pady=3)
        self.l_manual_set_second.grid(row=5, column=2, sticky="e", padx=10, pady=3)
        self.e_manual_set_second_1.grid(row=5, column=3, sticky="w", padx=5, pady=3)
        self.e_manual_set_second_2.grid(row=5, column=4, sticky="w", padx=5, pady=3)
        self.b_manual_set.grid(row=6, column=2, sticky="ew", padx=5, pady=3)
        self.b_manual_set_sample.grid(row=6, column=3, sticky="ew", padx=5, pady=3)
        self.b_manual_set_save.grid(row=6, column=4, sticky="ew", padx=5, pady=3)
        self.l_acc_right.grid(row=7, column=2, sticky="w", padx=5, pady=3)
        self.l_acc_left.grid(row=8, column=2, sticky="w", padx=5, pady=3)
        self.l_frame_desc.grid(row=7, column=3, columnspan=2, sticky="w", padx=5, pady=3)
        self.l_frame_1_desc.grid(row=8, column=3, columnspan=2, sticky="w", padx=5, pady=3)
        self.l_frame_2_desc.grid(row=9, column=3, columnspan=2, sticky="w", padx=5, pady=3)
        self.l_pause_middle.grid(row=9, column=2, sticky="w", padx=5, pady=3)
        self.l_pause_left.grid(row=10, column=2, sticky="w", padx=5, pady=3)
        self.l_middle_pause_left.grid(row=11, column=2, sticky="w", padx=5, pady=3)
        self.l_middle_pause_middle_2.grid(row=12, column=2, sticky="w", padx=5, pady=3)
        self.l_middle_pause_middle.grid(row=13, column=2, sticky="w", padx=5, pady=3)
        self.l_middle_pause_right.grid(row=14, column=2, sticky="w", padx=5, pady=3)
        self.l_valid_pause.grid(row=15, column=2, sticky="w", padx=5, pady=3)

        # ===== ROWS 8-9: Thread/Ignore inputs =====
        self.l_thread_num = tk.Label(self.root, text=t("thread_num"), font=20, height=2)
        self.e_thread_num = tk.Entry(self.root, bg="white", font=20)

        self.l_ignore_frame_cnt = tk.Label(self.root, text=t("ignore_frame_cnt"), font=20, height=2)
        self.e_ignore_frame_cnt = tk.Entry(self.root, bg="white", font=20)

        self.l_thread_num.grid(row=8, column=0, sticky="e", padx=10, pady=3)
        self.e_thread_num.grid(row=8, column=1, sticky="ew", padx=5, pady=3)
        self.l_ignore_frame_cnt.grid(row=9, column=0, sticky="e", padx=10, pady=3)
        self.e_ignore_frame_cnt.grid(row=9, column=1, sticky="ew", padx=5, pady=3)

        # ===== ROW 10: Save Settings button =====
        self.b_save_settings = tk.Button(self.root, text=t("save_settings"), font=20)
        self.b_save_settings.grid(row=10, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        # ===== ROWS 11-12: Measure/Cut controls =====
        self.l_measure_margin_second = tk.Label(self.root, text=t("measure_margin_second"), font=20, height=2)
        self.e_measure_margin_second = tk.Entry(self.root, bg="white", font=20)

        self.b_measure_margin = tk.Button(self.root, text=t("measure_margin"), font=20)
        self.b_crop = tk.Button(self.root, text=t("crop_btn"), font=20)

        self.l_measure_margin_second.grid(row=11, column=0, sticky="e", padx=10, pady=3)
        self.e_measure_margin_second.grid(row=11, column=1, sticky="ew", padx=5, pady=3)
        self.b_measure_margin.grid(row=12, column=0, sticky="ew", padx=5, pady=3)
        self.b_crop.grid(row=12, column=1, sticky="ew", padx=5, pady=3)

        # ===== ROWS 13-14: Start/End seconds =====
        self.l_start_second = tk.Label(self.root, text=t("start_second"), font=20, height=2)
        self.e_start_second = tk.Entry(self.root, bg="white", font=20)

        self.l_end_second = tk.Label(self.root, text=t("end_second"), font=20, height=2)
        self.e_end_second = tk.Entry(self.root, bg="white", font=20)

        self.l_start_second.grid(row=13, column=0, sticky="e", padx=10, pady=3)
        self.e_start_second.grid(row=13, column=1, sticky="ew", padx=5, pady=3)
        self.l_end_second.grid(row=14, column=0, sticky="e", padx=10, pady=3)
        self.e_end_second.grid(row=14, column=1, sticky="ew", padx=5, pady=3)

        # ===== ROW 15: Action buttons =====
        self.b_cut_without_crop = tk.Button(self.root, text=t("start_without_crop"), font=20)
        self.b_cut_with_crop = tk.Button(self.root, text=t("start_with_crop"), font=20)

        self.b_cut_without_crop.grid(row=15, column=0, sticky="ew", padx=5, pady=3)
        self.b_cut_with_crop.grid(row=15, column=1, sticky="ew", padx=5, pady=3)

        # ===== ROW 16: Tutorial links =====
        self.l_tutorial = tk.Label(self.root, text=t("tutorial"), font=20, height=2)

        import tkinter.font as tkFont
        ft = tkFont.Font(family="Fixdsys", size=11, weight=tkFont.NORMAL, underline=1)
        self.l_tutorial_url = tk.Label(
            self.root, text="www.bilibili.com/video/BV1qg411r7dV", font=ft, fg="blue", height=2
        )

        self.l_tutorial.grid(row=16, column=0, sticky="e", padx=10, pady=3)
        self.l_tutorial_url.grid(row=16, column=1, sticky="w", padx=5, pady=3)

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
        """Show mode description labels (rows 2-3)"""
        # Clear existing description labels first
        for lbl in self.description_labels:
            lbl.grid_remove()
        self.description_labels.clear()

        # Create new description labels
        mode_idx = self.e_mode.current()
        if mode_idx in [2, 3]:  # Lazy mode
            self._add_desc_label(2, 0, 2, "lazy_mode_desc1")
            self._add_desc_label(3, 0, 2, "lazy_mode_desc2")
            self._add_desc_label(4, 0, 2, "lazy_mode_desc3")
        else:  # Normal mode
            self._add_desc_label(2, 0, 2, "normal_mode_desc1")
            self._add_desc_label(3, 0, 2, "normal_mode_desc2")
            self._add_desc_label(4, 0, 2, "normal_mode_desc3")

    def _add_desc_label(self, row, col, colspan, text_key):
        """Helper to add a description label"""
        lbl = tk.Label(self.root, text=t(text_key), font=20)
        lbl.grid(row=row, column=col, columnspan=colspan, sticky="w", padx=10, pady=2)
        self.description_labels.append(lbl)

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

        # Update margin labels
        self.l_top_margin.config(text=t("top_margin"))
        self.l_bottom_margin.config(text=t("bottom_margin"))
        self.l_left_margin.config(text=t("left_margin"))
        self.l_right_margin.config(text=t("right_margin"))

        # Update thread/ignore labels
        self.l_thread_num.config(text=t("thread_num"))
        self.l_ignore_frame_cnt.config(text=t("ignore_frame_cnt"))

        # Update button
        self.b_save_settings.config(text=t("save_settings"))

        # Update measure/cut labels and buttons
        self.l_measure_margin_second.config(text=t("measure_margin_second"))
        self.b_measure_margin.config(text=t("measure_margin"))
        self.b_crop.config(text=t("crop_btn"))

        # Update start/end labels
        self.l_start_second.config(text=t("start_second"))
        self.l_end_second.config(text=t("end_second"))

        # Update action buttons
        self.b_cut_without_crop.config(text=t("start_without_crop"))
        self.b_cut_with_crop.config(text=t("start_with_crop"))

        # Update tutorial
        self.l_tutorial.config(text=t("tutorial"))

        # Update manual detection labels
        self.l_manual_set_or_not.config(text=t("manual_set_or_not"))
        update_combobox_preserve_selection(self.e_manual_set_or_not, "no", "yes")
        self.l_manual_set_second.config(text=t("manual_set_second"))
        self.b_manual_set.config(text=t("manual_set"))
        self.b_manual_set_sample.config(text=t("sample_images"))
        self.b_manual_set_save.config(text=t("save_detection_points"))
        self.l_frame_desc.config(text=t("refer_sample"))
        self.l_frame_1_desc.config(text=t("frame_1_desc"))
        self.l_frame_2_desc.config(text=t("frame_2_desc"))
