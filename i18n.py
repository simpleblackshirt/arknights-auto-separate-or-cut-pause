"""
i18n.py - Internationalization module for Arknights Auto Separate/Cut Pause

This module provides:
- Translation storage and lookup
- Language state management
- Callback system for language change notifications
- Helper functions for GUI widgets
"""

from typing import Callable

# Translation dictionary for bilingual support
TRANSLATIONS = {
    "cn": {
        "window_title": "明日方舟自动分离/剪掉暂停",
        "language": "语言",
        "current_working_dir": "当前工作目录",
        "select_mode": "选择模式",
        "show_desc": "显示说明",
        "top_margin": "上边距（像素数）",
        "bottom_margin": "下边距",
        "left_margin": "左边距",
        "right_margin": "右边距",
        "thread_num": "线程数",
        "ignore_frame_cnt": "忽视小于等于该帧数的片段",
        "save_settings": "保存设置",
        "measure_margin_second": "检测边距秒数（支持小数）",
        "measure_margin": "检测边距",
        "crop_btn": "按边距裁剪（边距将被重置为0）",
        "start_without_crop": "点击开始自动分离/剪掉暂停（不包含边距裁剪）",
        "start_with_crop": "点击开始自动分离/剪掉暂停（包含边距裁剪）",
        "tutorial": "详细操作教程：",
        "start_second": "开始秒数",
        "end_second": "结束秒数",
        "manual_set_second": "手动设置检测点画面秒数（支持小数）",
        "manual_set": "手动设置",
        "sample_images": "设置示例图",
        "save_detection_points": "保存检测点",
        "refer_sample": "请参考示例图",
        "frame_1_desc": "前者秒数为1倍速无暂停画面",
        "frame_2_desc": "后者秒数为有效暂停画面",
        "manual_set_or_not": "是否手动设置检测点",
        "no": "否",
        "yes": "是",
        # Section titles
        "margin_section": "边距设置",
        "manual_detection": "手动检测点",
        "processing_settings": "处理设置",
        "crop_actions": "裁剪操作",
        "process_actions": "处理操作",
        # Theme options
        "theme": "主题",
        "light": "浅色",
        "dark": "深色",
        "auto": "自动",
        # Mode options
        "mode_normal_audio_only": "正常模式（仅保留无效暂停音效）",
        "mode_normal_keep_video": "正常模式（保留无效暂停视频）",
        "mode_lazy_keep_valid": "懒人模式（保留有效暂停）",
        "mode_lazy_cut_all": "懒人模式（暂停全剪）",
        # Description labels
        "lazy_mode_desc1": "懒人模式将会自动剪掉暂停\n并且加速1倍速的部分为2倍速",
        "lazy_mode_desc2": "适用于无需保留音效",
        "lazy_mode_desc3": "此模式只会生成1个文件",
        "normal_mode_desc1": "正常模式将会自动分离暂停部分\n并且保留音效",
        "normal_mode_desc2": "适用于需要保留音效\n（注：正常模式不支持mkv格式）",
        "normal_mode_desc3": "此模式会生成较多文件",
        # Error messages
        "error_title": "出错了！",
        "margin_param_error": "边距参数有误（需整数）",
        "margin_too_large": "边距像素数过大，请重新设置",
        "negative_margin_error": "不能裁剪负数边距（剪暂停不影响）",
        "aftercrop_name_error": "裁剪文件名不能为aftercrop.mp4",
        "duplicate_file_error": "上级目录已存在同文件名，请重命名",
        "start_end_param_error": "开始结束秒数有误（需正整数）",
        "end_must_be_greater": "结束秒数必须大于开始秒数",
        "no_out_prefix": "文件名不得以out开头，请重命名",
        "single_file_required": "工作目录下文件数必须为1",
        "measure_margin_error": "检测边距秒数有误（需大于0的数字，接受小数）",
        "manual_set_second_error": "手动设置检测点画面秒数有误（需大于0的数字，接受小数）",
        "margin_exceeds_length": "检测边距秒数必须小于视频长度",
        "thread_num_error": "线程数必须为1~16的整数",
        "ignore_frame_error": "忽视帧数必须为>=0的整数",
        "no_detection_points": "未设置检测点",
        "calculation_error": "计算有误，请重新输入正确的检测边距秒数（显示编队的帧）",
        "end_exceeds_video": "结束秒数必须小于视频长度",
        "sample_image_missing": "示例图不存在请重新下载",
        "frame_read_failed": "画面读取失败",
        "not_4_points": "未设置4个点请重新设置",
        "not_8_points": "未设置8个点请重新设置",
        # Info messages
        "info_title": "消息",
        "margin_filled": "边距已填充",
        "settings_saved": "设置已保存",
        "detection_points_saved": "检测点坐标已保存",
        "warning_title": "注意",
        "fps_warning": "视频帧数为非整数，可能会有剪辑问题，推荐使用其他软件重新导出为整数帧文件，点击确定或关闭窗口以继续",
        "click_4_points": "请参考示例图1按顺序点击以下4个点（红叉中心位置）：\n第一个点请点击右上角1倍速X正下方的三角形白色区域\n第二个点请点击右上角1倍速1正下方的灰色区域\n第三个点请点击右上角暂停正中的灰色区域\n第四个点请点击右上角暂停靠左的白色区域",
        "click_8_points": "请参考示例图2按顺序点击以下8个点（红叉中心位置）：\n第一个点请点击中间P字母的T型连接处\n第二个点请点击中间U字母中间的灰色区域\n第三个点请点击中间U字母靠下的白色区域\n第四个点请点击中间E字母的T型连接处靠上的白色区域\n第五至第八个点请点击左侧技能二字上方的灰色条状（纵坐标必须与灰色条状持平 横坐标比较平均的点上就可以）",
        # File suffixes (internal use)
        "valid_pause": "_有效暂停",
        "invalid_pause": "_无效暂停",
        # Console logging messages
        "log_crop_complete": "已完成，请在working_folder下查看裁剪后的aftercrop.mp4文件，原文件已移动至上级目录",
        "log_started": "开始",
        "log_lazy_complete": "已完成，请在working_folder下查看output.mp4文件",
        "log_normal_complete": "已完成，请在working_folder下查看分离的mp4文件",
        "log_segment_deleted": "片段 {} 小于等于忽视帧数，已删除",
        "log_timing_for": "    为 {} 计时",
        "log_timing_started": "    计时开始于 {}",
        "log_timing_ended": "    计时结束于 {}",
        "log_time_elapsed": "        用时 {}",
        "log_thread_analyze_pause_start": "线程{}:开始分析暂停位置",
        "log_thread_100_percent": "线程{}：100%",
        "log_thread_cut_pause_accel_start": "线程{}：开始剪掉暂停及加速",
        "log_thread_no_intersection": "开始结束秒数与被分配区间没有交集，线程{}未启动\n请尽量只将需要剪辑的部分放入使用",
        "log_thread_generate_video_start": "线程{}：开始生成视频片段",
        "log_thread_merge_audio_video_start": "线程{}：开始合并音频视频片段",
        "log_thread_no_audio_rename": "线程{}：视频未检测出音频，仅重命名",
        "log_timing_cropping": "裁剪",
        "log_timing_full_process": "全流程",
        "log_timing_cleaning_segments": "清理片段",
        "log_timing_analyzing_pauses": "分析暂停",
        "log_timing_generating_video": "生成视频",
        "log_timing_generating_video_segments": "生成视频片段",
        "log_timing_generating_audio_segments": "生成音频片段",
        "log_timing_merging_video_audio": "合并视频音频",
    },
    "en": {
        "window_title": "Arknights Auto Separate/Cut Pause",
        "language": "Language",
        "current_working_dir": "Current Working Directory",
        "select_mode": "Select Mode",
        "show_desc": "Show Description",
        "top_margin": "Top Margin (pixels)",
        "bottom_margin": "Bottom Margin",
        "left_margin": "Left Margin",
        "right_margin": "Right Margin",
        "thread_num": "Thread Count",
        "ignore_frame_cnt": "Ignore segments <= this frame count",
        "save_settings": "Save Settings",
        "measure_margin_second": "Measure Margin Second (decimals OK)",
        "measure_margin": "Measure Margin",
        "crop_btn": "Crop by Margin (margin will be reset to 0)",
        "start_without_crop": "Click to Start Auto Separate/Cut Pause (no crop)",
        "start_with_crop": "Click to Start Auto Separate/Cut Pause (with crop)",
        "tutorial": "Detailed Tutorial:",
        "start_second": "Start Second",
        "end_second": "End Second",
        "manual_set_second": "Manual Set Detection Point Second (decimals OK)",
        "manual_set": "Manual Set",
        "sample_images": "Sample Images",
        "save_detection_points": "Save Detection Points",
        "refer_sample": "Please refer to sample images",
        "frame_1_desc": "First value: 1x speed no pause frame",
        "frame_2_desc": "Second value: valid pause frame",
        "manual_set_or_not": "Manually set detection points?",
        "no": "No",
        "yes": "Yes",
        # Section titles
        "margin_section": "Margin Settings",
        "manual_detection": "Manual Detection",
        "processing_settings": "Processing Settings",
        "crop_actions": "Crop Actions",
        "process_actions": "Process Actions",
        # Theme options
        "theme": "Theme",
        "light": "Light",
        "dark": "Dark",
        "auto": "Auto",
        # Mode options
        "mode_normal_audio_only": "Normal Mode (keep invalid pause audio only)",
        "mode_normal_keep_video": "Normal Mode (keep invalid pause video)",
        "mode_lazy_keep_valid": "Lazy Mode (keep valid pauses)",
        "mode_lazy_cut_all": "Lazy Mode (cut all pauses)",
        # Description labels
        "lazy_mode_desc1": "Lazy Mode will automatically cut pauses\nand speed up 1x parts to 2x",
        "lazy_mode_desc2": "For when you don't need to keep sound effects",
        "lazy_mode_desc3": "This mode only generates 1 file",
        "normal_mode_desc1": "Normal Mode will automatically separate pauses\nand keep sound effects",
        "normal_mode_desc2": "For when you need to keep sound effects\n(Note: normal mode doesn't support mkv format)",
        "normal_mode_desc3": "This mode generates multiple files",
        # Error messages
        "error_title": "Error!",
        "margin_param_error": "Margin parameter error (must be integer)",
        "margin_too_large": "Margin pixel value too large, please reset",
        "negative_margin_error": "Cannot crop negative margins (pause cutting unaffected)",
        "aftercrop_name_error": "Crop filename cannot be aftercrop.mp4",
        "duplicate_file_error": "A file with the same name already exists in parent directory, please rename",
        "start_end_param_error": "Start/end second parameter error (must be positive integer)",
        "end_must_be_greater": "End second must be greater than start second",
        "no_out_prefix": "Filename cannot start with 'out', please rename",
        "single_file_required": "Working directory must contain exactly 1 file",
        "measure_margin_error": "Measure margin second error (must be >0, decimals accepted)",
        "manual_set_second_error": "Manual set detection point second error (must be >0, decimals accepted)",
        "margin_exceeds_length": "Measure margin second must be less than video length",
        "thread_num_error": "Thread count must be integer from 1 to 16",
        "ignore_frame_error": "Ignore frame count must be integer >= 0",
        "no_detection_points": "Detection points not set",
        "calculation_error": "Calculation error, please enter correct measure margin second (frame showing squad)",
        "end_exceeds_video": "End second must be less than video length",
        "sample_image_missing": "Sample image not found, please re-download",
        "frame_read_failed": "Failed to read frame",
        "not_4_points": "Not all 4 points set, please reset",
        "not_8_points": "Not all 8 points set, please reset",
        # Info messages
        "info_title": "Message",
        "margin_filled": "Margins filled",
        "settings_saved": "Settings saved",
        "detection_points_saved": "Detection point coordinates saved",
        "warning_title": "Notice",
        "fps_warning": "Video has non-integer FPS, there may be editing issues. It's recommended to re-export as integer FPS file using other software. Click OK or close window to continue",
        "click_4_points": "Please refer to sample image 1 and click these 4 points in order (center of red X markers):\nPoint 1: Click the triangular white area directly below the 1x speed X in the top right corner\nPoint 2: Click the gray area directly below the 1x speed 1 in the top right corner\nPoint 3: Click the gray area in the center of the pause icon in the top right corner\nPoint 4: Click the white area on the left side of the pause icon in the top right corner",
        "click_8_points": "Please refer to sample image 2 and click these 8 points in order (center of red X markers):\nPoint 1: Click the T-shaped connection of the P letter in the center\nPoint 2: Click the gray area in the middle of the U letter in the center\nPoint 3: Click the white area below the U letter in the center\nPoint 4: Click the white area above the T-shaped connection of the E letter in the center\nPoints 5-8: Click the gray bar above 'Skill' (技能) on the left side (vertical coordinate must align with gray bar, horizontal coordinate should be evenly distributed points)",
        # File suffixes (internal use)
        "valid_pause": "_valid_pause",
        "invalid_pause": "_invalid_pause",
        # Console logging messages
        "log_crop_complete": "Completed. Please check the cropped aftercrop.mp4 file in working_folder. Original file has been moved to parent directory",
        "log_started": "started",
        "log_lazy_complete": "Completed. Please check output.mp4 file in working_folder",
        "log_normal_complete": "Completed. Please check the separated mp4 files in working_folder",
        "log_segment_deleted": "Segment {} is less than or equal to ignore frame count, deleted",
        "log_timing_for": "    Timing for {}",
        "log_timing_started": "    Timing started at {}",
        "log_timing_ended": "    Timing ended at {}",
        "log_time_elapsed": "        Time elapsed: {}",
        "log_thread_analyze_pause_start": "Thread {}: Starting to analyze pause positions",
        "log_thread_100_percent": "Thread {}: 100%",
        "log_thread_cut_pause_accel_start": "Thread {}: Starting to cut out pauses and accelerations",
        "log_thread_no_intersection": "Start/end seconds have no intersection with assigned range, thread {} not started\nPlease try to only include the parts that need to be edited",
        "log_thread_generate_video_start": "Thread {}: Starting to generate video segments",
        "log_thread_merge_audio_video_start": "Thread {}: Starting to merge audio and video segments",
        "log_thread_no_audio_rename": "Thread {}: No audio detected in video, renaming only",
        "log_timing_cropping": "Cropping",
        "log_timing_full_process": "Full process",
        "log_timing_cleaning_segments": "Cleaning segments",
        "log_timing_analyzing_pauses": "Analyzing pauses",
        "log_timing_generating_video": "Generating video",
        "log_timing_generating_video_segments": "Generating video segments",
        "log_timing_generating_audio_segments": "Generating audio segments",
        "log_timing_merging_video_audio": "Merging video and audio",
    }
}


class I18nManager:
    """Manages internationalization with callback support"""

    def __init__(self):
        self._current_language = "cn"
        self._callbacks = []

    def get_current_language(self) -> str:
        """Get current language code"""
        return self._current_language

    def set_language(self, language: str, notify: bool = True) -> None:
        """
        Set current language and optionally notify callbacks

        Args:
            language: Language code ("cn" or "en")
            notify: Whether to trigger update callbacks (default: True)
        """
        if language in TRANSLATIONS:
            self._current_language = language
            if notify:
                self._notify_callbacks()
        else:
            raise ValueError(f"Unsupported language: {language}")

    def t(self, key: str) -> str:
        """
        Get translated text for current language

        Args:
            key: Translation key

        Returns:
            Translated text or key if not found
        """
        return TRANSLATIONS[self._current_language].get(key, key)

    def register_callback(self, callback: Callable[[], None]) -> None:
        """
        Register a callback to be called when language changes

        Args:
            callback: Function to call when language changes
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[], None]) -> None:
        """
        Unregister a language change callback

        Args:
            callback: Function to remove from callbacks
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _notify_callbacks(self) -> None:
        """Notify all registered callbacks that language has changed"""
        for callback in self._callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error in language change callback: {e}")

    def update_combobox_with_translation(self, combobox, *translation_keys: str) -> None:
        """
        Update combobox values with translated text while preserving selection

        Args:
            combobox: ttk.Combobox widget
            *translation_keys: Translation keys for combobox values
        """
        # Store current selection
        current_idx = combobox.current()

        # Update values with translations
        translated_values = tuple(self.t(key) for key in translation_keys)
        combobox["value"] = translated_values

        # Restore selection (clamp to valid range)
        if 0 <= current_idx < len(translated_values):
            combobox.current(current_idx)
        elif len(translated_values) > 0:
            combobox.current(0)


# Global i18n manager instance
_i18n_manager = I18nManager()

# Public API functions (backward compatible)
def t(key: str) -> str:
    """Get translated text for current language"""
    return _i18n_manager.t(key)

def get_current_language() -> str:
    """Get current language code"""
    return _i18n_manager.get_current_language()

def set_language(language: str, notify: bool = True) -> None:
    """Set current language and optionally trigger update callbacks"""
    _i18n_manager.set_language(language, notify)

def register_language_change_callback(callback: Callable[[], None]) -> None:
    """Register a callback to be called when language changes"""
    _i18n_manager.register_callback(callback)

def update_combobox_preserve_selection(combobox, *translation_keys: str) -> None:
    """Update combobox with translations while preserving selection"""
    _i18n_manager.update_combobox_with_translation(combobox, *translation_keys)

# Export the manager for advanced usage
__all__ = [
    "t", "get_current_language", "set_language",
    "register_language_change_callback", "update_combobox_preserve_selection",
    "TRANSLATIONS", "_i18n_manager"
]
