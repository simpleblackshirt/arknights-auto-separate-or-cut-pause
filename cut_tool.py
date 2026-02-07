from tkinter import *
from tkinter import ttk
from tkinter import font as tkFont
import os
import cv2
import numpy as np
import sys
from pydub import AudioSegment
import subprocess
import webbrowser
import math
import datetime
import threading
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Global variable
path = os.getcwd()
working_path = path + "\\working_folder\\"
bin_path = path + "\\bin\\"
os.environ['PATH'] = bin_path + os.pathsep + os.environ.get('PATH','')
                    
array_1 = []
array_2 = []

# Video metadata cache for performance optimization
_video_metadata_cache = {}

# Constants

TEMP_FILENAME = "temp_list.txt"
TEMP_PREFIX = "out_"
FOURCC = cv2.VideoWriter_fourcc("m", "p", "4", "v")
DEFAULT_THREAD_NUM = 4
DEFAULT_IGNORE_FRAME_CNT = 0
SHOW_PROGRESS_SEG = 5
DEFAULT_LANGUAGE = "en"  # Default language: "cn" for Chinese, "en" for English, "ja" for Japanese

P_M_Y_CO = 0.074             #(right top) pause middle coefficient
P_M_X_CO = 0.112
P_L_X_CO = 0.125
M_P_M_Y_2_CO = 0.5           #this is the black point, other 3 are white point 
M_P_M_X_2_CO = 0.5           
M_P_L_Y_CO = 0.007           #middle pause
M_P_L_X_CO = 0.19
M_P_M_Y_CO = 0.043
M_P_R_Y_CO = 0.023
M_P_R_X_CO = 0.149

ACC_L_Y_CO = 0.095           #accelerate for lazy only
ACC_L_X_CO = 0.262
ACC_R_X_CO = 0.247

VP_Y_CO = 0.5       #valid pause
VP_X_1_CO = 0.046
VP_X_2_CO = 0.093
VP_X_3_CO = 0.139
VP_X_4_CO = 0.185

# Disabled following as new UI always works with first way of checking
#VP_2_Y_CO = 0.389   #second option to check valid pause
#VP_2_X_1_CO = 0.188 #wendi
#VP_2_X_2_CO = 0.197 #niaolong(mozu)
#VP_2_X_3_CO = 0.206 #m3
#VP_2_X_4_CO = 0.217 #panxie

WHITE_10 = np.array([240, 240, 240])
WHITE_9 = np.array([200, 200, 200])  # the number indicates the white level
GRAY = np.array([128, 128, 128])
BLACK_9 = np.array([30, 30, 30])
P_DIFF_TH = 10 # threshold
M_P_DIFF_TH = np.array([30, 30, 30]) # threshold
GRAY_LOWER = np.array([55, 55, 55])
GRAY_UPPER = np.array([130, 130, 130])

BLUE = 0
GREEN = 1
RED = 2
DARK_RED_TH = [20, 20, 90] # BGR <= <= >=
RED_RATIO_FOR_TOP_MARGIN = 0.3913
BLUE_TH = [130, 110, 50] # >= >= <=
BLUE_LOWER_PERC = 0.1
BLUE_UPPER_PERC = 0.25
LIGHT_GRAY_TH = [130, 130, 130]
LIGHT_GRAY_LOWER_PERC = 0.1
LIGHT_GRAY_UPPER_PERC = 0.25


MARGIN_TH = 500

# Import i18n module
from i18n import (
    t, get_current_language, set_language,
    register_language_change_callback
)

# Import UI module
from ui import MainWindow

# Initialize default language before creating any GUI elements
set_language(DEFAULT_LANGUAGE, notify=False)

# Global language variable
current_language = get_current_language()

def change_language(event=None):
    """Handle language change"""
    global current_language
    idx = ui.e_language.current()
    if idx == 0:
        new_language = "cn"
    elif idx == 1:
        new_language = "en"
    else:
        new_language = "ja"
    set_language(new_language)
    current_language = get_current_language()
    ui.update_all_text()

def update_all_text():
    """Update all GUI text elements based on current language"""
    ui.update_all_text()

def check_margin(ui, top_margin, bottom_margin, left_margin, right_margin):
    if not (
        top_margin.replace("-", "").isdigit()
        and bottom_margin.replace("-", "").isdigit()
        and left_margin.replace("-", "").isdigit()
        and right_margin.replace("-", "").isdigit()
    ):
        ui.show_error_popup(t("margin_param_error"))
        return False
    if (
        int(top_margin) > MARGIN_TH
        or int(bottom_margin) > MARGIN_TH
        or int(left_margin) > MARGIN_TH
        or int(right_margin) > MARGIN_TH
    ):
        ui.show_error_popup(t("margin_too_large"))
        return False
    return True

def check_crop(ui, top_margin, bottom_margin, left_margin, right_margin, video_name):
    if (
        int(top_margin) < 0
        or int(bottom_margin) < 0
        or int(left_margin) < 0
        or int(right_margin) < 0
    ):
        ui.show_error_popup(t("negative_margin_error"))
        return False
    if video_name == "aftercrop.mp4":
        ui.show_error_popup(t("aftercrop_name_error"))
        return False
    if os.path.exists(path + "/" + video_name):
        ui.show_error_popup(t("duplicate_file_error"))
        return False
    return True

def check_start_end_seconds(ui, start_second, end_second):
    if not (start_second.isdigit() and end_second.isdigit()):
        ui.show_error_popup(t("start_end_param_error"))
        return False
    if int(start_second) >= int(end_second):
        ui.show_error_popup(t("end_must_be_greater"))
        return False
    return True

def check_file_and_return_path(ui):
    file_cnt = 0
    working_folder_list = os.listdir(working_path)
    for lists in working_folder_list:
        file_cnt += 1
    if file_cnt == 1:
        if working_folder_list[0].startswith("out"):
            ui.show_error_popup(t("no_out_prefix"))
            return False
        return working_path + working_folder_list[0]
    ui.show_error_popup(t("single_file_required"))
    return False

def check_measure_margin_second(ui, measure_margin_second):
    if not measure_margin_second.replace(".", "", 1).isdigit():
        ui.show_error_popup(t("measure_margin_error"))
        return False
    return True

def check_set_second(ui, set_second):
    if not set_second.replace(".", "", 1).isdigit():
        ui.show_error_popup(t("manual_set_second_error"))
        return False
    return True

def check_measure_margin_second_2(ui, measure_margin_second, fps, frame_cnt):
    if measure_margin_second >= frame_cnt / fps:
        ui.show_error_popup(t("margin_exceeds_length"))
        return False
    return True

def check_thread_num(ui, thread_num):
    if not(thread_num.isdigit() and 1 <= int(thread_num) <= 16):
        ui.show_error_popup(t("thread_num_error"))
        return False
    return True

def check_ignore_frame_cnt(ui, ignore_frame_cnt):
    if not(ignore_frame_cnt.isdigit()):
        ui.show_error_popup(t("ignore_frame_error"))
        return False
    return True

def check_coordinates_setting(ui):
    if not(len(array_1) == 4 and len(array_2) == 8):
        ui.show_error_popup(t("no_detection_points"))
        return False
    return True

def set_margin(top_margin, bottom_margin, left_margin, right_margin):
    ui.set_margin(top_margin, bottom_margin, left_margin, right_margin)

def set_thread_num(thread_num):
    ui.set_thread_num(thread_num)

def set_ignore_frame_cnt(ignore_frame_cnt):
    ui.set_ignore_frame_cnt(ignore_frame_cnt)    

def set_coordinates():
    if os.path.exists(path + "/detection_points.txt"):
        with open(path + "/detection_points.txt") as f:  # Detection points
            for i in range(4):
                coord = [int(f.readline()) , int(f.readline())]
                array_1.append(coord)

            for i in range(4):
                coord = [int(f.readline()) , int(f.readline())]
                array_2.append(coord)

            valid_pause_y = int(f.readline())

            for i in range(4):
                coord = [valid_pause_y , int(f.readline())]
                array_2.append(coord)

            set_coordinates_labels()

            #print(array_1)
            #print(array_2)
   
def set_coordinates_labels():
    # Default placeholder format
    array_1_format = "(x1, y1), (x2, y2), (x3, y3), (x4, y4)"
    array_2_format = "(x1, y1), (x2, y2), (x3, y3), (x4, y4), (x5, y5), (x6, y6), (x7, y7), (x8, y8)"

    if len(array_1) == 4 and len(array_2) == 8:
        # Format array_1 coordinates (4 points: acc_right, acc_left, pause_middle, pause_left)
        array_1_coords = ", ".join([f"({pt[0]}, {pt[1]})" for pt in array_1])

        # Format array_2 coordinates (8 points: 4 single points + 4 valid_pause points with same y)
        # First 4 are (y,x) pairs
        array_2_first_4 = ", ".join([f"({pt[0]}, {pt[1]})" for pt in array_2[:4]])
        # valid_pause points: array_2[4][0] is y, array_2[4][1], array_2[5][1], array_2[6][1], array_2[7][1] are x values
        y = array_2[4][0]
        valid_pause_points = ", ".join([f"({y}, {array_2[i][1]})" for i in range(4, 8)])
        array_2_coords = array_2_first_4 + ", " + valid_pause_points

        ui.set_coordinates(array_1_coords, array_2_coords)
    else:
        ui.set_coordinates(array_1_format, array_2_format)
 
def get_video_info(video_path, use_cache=True):
    if use_cache and video_path in _video_metadata_cache:
        return _video_metadata_cache[video_path]
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    lgt = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    hgt = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_cnt = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    result = (fps, lgt, hgt, frame_cnt)
    if use_cache:
        _video_metadata_cache[video_path] = result
    return result

def get_frame_cnt(video_path, use_cache=True):
    if use_cache and video_path in _video_metadata_cache:
        return _video_metadata_cache[video_path][3]  # Return frame_cnt
    cap = cv2.VideoCapture(video_path)
    frame_cnt = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    if use_cache:
        # Cache just the frame count if full metadata not cached
        if video_path in _video_metadata_cache:
            _video_metadata_cache[video_path] = (
                _video_metadata_cache[video_path][0],
                _video_metadata_cache[video_path][1],
                _video_metadata_cache[video_path][2],
                frame_cnt
            )
        else:
            _video_metadata_cache[video_path] = (0, 0, 0, frame_cnt)
    return frame_cnt

def clear_video_cache():
    """Clear the video metadata cache. Call when video files are modified/deleted."""
    global _video_metadata_cache
    _video_metadata_cache.clear()

def measure_margin(ui, measure_margin_second):
    if check_measure_margin_second(ui, measure_margin_second):
        video_path = check_file_and_return_path(ui)
        if video_path:
            fps, lgt, hgt, frame_cnt = get_video_info(video_path)
            if check_measure_margin_second_2(
                ui, float(measure_margin_second), fps, frame_cnt
            ):
                cap = cv2.VideoCapture(video_path)
                top_margin = MARGIN_TH
                bottom_margin = MARGIN_TH
                left_margin = MARGIN_TH
                right_margin = MARGIN_TH

                cap.set(
                    cv2.CAP_PROP_POS_FRAMES, int(fps * float(measure_margin_second))
                )
                ret, frame = cap.read()
                cap.release()

                flag = False
                red_cnt = 1
                # Vectorized right margin and top margin detection (red vertical line)
                # Only check the right half of the frame, up to half height
                right_half = frame[:int(hgt/2), int(lgt/2):]
                red_mask = (
                    (right_half[:, :, RED] >= DARK_RED_TH[RED]) &
                    (right_half[:, :, BLUE] <= DARK_RED_TH[BLUE]) &
                    (right_half[:, :, GREEN] <= DARK_RED_TH[GREEN])
                )
                # Find rightmost column with red pixels
                red_columns = np.any(red_mask, axis=0)
                if np.any(red_columns):
                    # Get index of rightmost red column (from right side)
                    rightmost_red_idx = len(red_columns) - 1 - np.argmax(red_columns[::-1])
                    right_margin = int(lgt/2) - rightmost_red_idx - 1
                    # Find top red pixel position for top margin calculation
                    red_col_mask = red_mask[:, rightmost_red_idx]
                    red_indices = np.where(red_col_mask)[0]
                    if len(red_indices) > 0:
                        first_y = red_indices[0]
                        # Count consecutive red pixels from first_y
                        red_cnt = 1
                        for idx in range(1, len(red_indices)):
                            if red_indices[idx] == red_indices[idx-1] + 1:
                                red_cnt += 1
                            else:
                                break
                        top_margin = int(first_y - red_cnt * RED_RATIO_FOR_TOP_MARGIN)
                    else:
                        top_margin = MARGIN_TH
                else:
                    top_margin = MARGIN_TH
                    right_margin = MARGIN_TH
                    flag = True  # No red found, skip to next check

                if not flag:
                    # Vectorized bottom margin detection (blue horizontal line)
                    # Check bottom half of frame
                    bottom_half = frame[int(hgt/2):, :]
                    blue_mask = (
                        (bottom_half[:, :, BLUE] >= BLUE_TH[BLUE]) &
                        (bottom_half[:, :, GREEN] >= BLUE_TH[GREEN]) &
                        (bottom_half[:, :, RED] <= BLUE_TH[RED])
                    )
                    blue_row_counts = np.sum(blue_mask, axis=1)
                    bottom_margin = MARGIN_TH
                    for bot_check in range(1, min(int(hgt / 2), len(blue_row_counts))):
                        row_idx = len(blue_row_counts) - bot_check
                        blue_cnt = blue_row_counts[row_idx]
                        if BLUE_LOWER_PERC < blue_cnt / lgt < BLUE_UPPER_PERC:
                            bottom_margin = bot_check - 1
                            break

                    # Vectorized left margin detection (light gray vertical area)
                    left_half = frame[:, :int(lgt/2)]
                    gray_mask = (
                        (left_half[:, :, BLUE] >= LIGHT_GRAY_TH[BLUE]) &
                        (left_half[:, :, GREEN] >= LIGHT_GRAY_TH[GREEN]) &
                        (left_half[:, :, RED] >= LIGHT_GRAY_TH[RED])
                    )
                    gray_column_ratios = np.sum(gray_mask, axis=0) / hgt
                    left_margin = MARGIN_TH
                    for x in range(len(gray_column_ratios)):
                        if LIGHT_GRAY_LOWER_PERC < gray_column_ratios[x] < LIGHT_GRAY_UPPER_PERC:
                            left_margin = x
                            break          
                        

                if (
                    top_margin >= MARGIN_TH
                    or bottom_margin >= MARGIN_TH
                    or left_margin >= MARGIN_TH
                    or right_margin >= MARGIN_TH
                ):
                    ui.show_error_popup(t("calculation_error"))
                    return False
                set_margin(top_margin, bottom_margin, left_margin, right_margin)
                ui.show_info_popup(t("margin_filled"))
                return True
            else:
                return False

             
def cut_with_crop(ui, mode, start_second, end_second, thread_num, measure_margin_second, ignore_frame_cnt):
    if check_ignore_frame_cnt(ui, ignore_frame_cnt):
        if check_thread_num(ui, thread_num):
            if check_start_end_seconds(ui, start_second, end_second):
                if measure_margin(ui, measure_margin_second):
                    # Cache margin values before crop (performance optimization)
                    cached_top = ui.e_top_margin.get()
                    cached_bottom = ui.e_bottom_margin.get()
                    cached_left = ui.e_left_margin.get()
                    cached_right = ui.e_right_margin.get()

                    if crop(
                        ui,
                        cached_top,
                        cached_bottom,
                        cached_left,
                        cached_right,
                    ):
                        # Restore cached margin values instead of calling measure_margin again
                        set_margin(cached_top, cached_bottom, cached_left, cached_right)
                        cut_without_crop(
                            ui,
                            mode,
                            cached_top,
                            cached_bottom,
                            cached_left,
                            cached_right,
                            start_second,
                            end_second,
                            thread_num,
                            ignore_frame_cnt
                        )

def crop(ui, top_margin, bottom_margin, left_margin, right_margin):
    video_path = check_file_and_return_path(ui)
    if video_path:
        if check_margin(ui, top_margin, bottom_margin, left_margin, right_margin):
            orig_name = os.listdir(working_path)[0]
            if check_crop(
                ui, top_margin, bottom_margin, left_margin, right_margin, orig_name
            ):
                cap = cv2.VideoCapture(video_path)
                lgt = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) 
                hgt = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) 
                cap.release()
                out = working_path + "aftercrop.mp4"
                if (lgt - int(left_margin) - int(right_margin)) % 2 == 1:
                    W = str(lgt - int(left_margin) - int(right_margin) + 1)
                else:
                    W = str(lgt - int(left_margin) - int(right_margin))
                if (hgt - int(top_margin) - int(bottom_margin)) % 2 == 1:
                    H = str(hgt - int(top_margin) - int(bottom_margin) + 1)
                else:                    
                    H = str(hgt - int(top_margin) - int(bottom_margin))
                X = left_margin
                Y = top_margin
                #print(X, Y, W, H)              
                
                tc = TimeCost()
                tc.time_start(t("log_timing_cropping"))

                subprocess.call('ffmpeg -loglevel quiet -i "'
                    + video_path + '" -b:v 0 -vf crop='
                    + W + ':' + H + ':' + X + ':' + Y + ' '+out,shell = True)
                # Original file stays in working_folder (not moved or deleted)
                logger.info(t("log_crop_complete"))

                tc.time_end()
                # set_margin(0, 0, 0, 0)
                # print("Margins reset to 0")
                return True

def show_desc():
    """Show mode description labels"""
    ui.show_description_labels()

def save_settings(ui, mode_i, top_margin, bottom_margin, left_margin, right_margin, thread_num, ignore_frame_cnt):
    if check_thread_num(ui, thread_num):
        if check_margin(ui, top_margin, bottom_margin, left_margin, right_margin):
            with open(path + "/settings.txt", "w+") as f:  # Settings
                f.write(str(mode_i) + "\n")
                f.write(top_margin + "\n")
                f.write(bottom_margin + "\n")
                f.write(left_margin + "\n")
                f.write(right_margin + "\n")
                f.write(thread_num + "\n")
                f.write(ignore_frame_cnt + "\n")
                f.write(str(current_language) + "\n")  # Save language preference
            ui.show_settings_saved_popup()

def manual_set_save(ui):
    if check_coordinates_setting(ui):
        with open(path + "/detection_points.txt", "w+") as f:  # Save detection points
            f.write(str(array_1[0][0]) + "\n")
            f.write(str(array_1[0][1]) + "\n")
            f.write(str(array_1[1][0]) + "\n")
            f.write(str(array_1[1][1]) + "\n")
            f.write(str(array_1[2][0]) + "\n")
            f.write(str(array_1[2][1]) + "\n")
            f.write(str(array_1[3][0]) + "\n")
            f.write(str(array_1[3][1]) + "\n")
            f.write(str(array_2[0][0]) + "\n")
            f.write(str(array_2[0][1]) + "\n")
            f.write(str(array_2[1][0]) + "\n")
            f.write(str(array_2[1][1]) + "\n")
            f.write(str(array_2[2][0]) + "\n")
            f.write(str(array_2[2][1]) + "\n")
            f.write(str(array_2[3][0]) + "\n")
            f.write(str(array_2[3][1]) + "\n")
            f.write(str(array_2[4][0]) + "\n")
            f.write(str(array_2[4][1]) + "\n")
            f.write(str(array_2[5][1]) + "\n")
            f.write(str(array_2[6][1]) + "\n")
            f.write(str(array_2[7][1]) + "\n")
        ui.show_info_popup(t("detection_points_saved"))

def cut_without_crop(
    ui, mode, top_margin, bottom_margin, left_margin, right_margin, start_second, end_second, thread_num, ignore_frame_cnt
):
    if ui.e_manual_set_or_not.current() == 0 or check_coordinates_setting(ui):
        if check_ignore_frame_cnt(ui, ignore_frame_cnt):
            if check_thread_num(ui, thread_num):
                if check_start_end_seconds(ui, start_second, end_second):
                    video_path = check_file_and_return_path(ui)
                    if video_path:
                        cap = cv2.VideoCapture(video_path)
                        frame_cnt = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        cap.release()
                        if check_margin(ui, top_margin, bottom_margin, left_margin, right_margin):
                            if frame_cnt / int(fps) <= int(end_second):
                                ui.show_error_popup(t("end_exceeds_video"))
                            else:
                                if int(fps) != fps:  # warning only not error
                                    ui.show_info_popup(
                                        t("fps_warning"),
                                        title=t("warning_title"),
                                    )
                                tc = TimeCost()
                                tc.time_start(t("log_timing_full_process"))
                                # Get translated mode name for display
                                mode_names = [t("mode_normal_audio_only"), t("mode_normal_keep_video"), t("mode_lazy_keep_valid"), t("mode_lazy_cut_all")]
                                logger.info(mode_names[mode] + " " + t("log_started"))
                                if mode in [2, 3]:  # Lazy mode indices
                                    lazy_version(
                                        video_path,
                                        mode,
                                        int(top_margin),
                                        int(bottom_margin),
                                        int(left_margin),
                                        int(right_margin),
                                        int(start_second),
                                        int(end_second),
                                        int(thread_num)
                                    )
                                    # already know these variables are int, thus cast here instead of inside
                                    logger.info(t("log_lazy_complete"))
                                else:  # normal mode otherwise
                                    normal_version(
                                        video_path,
                                        mode,
                                        int(top_margin),
                                        int(bottom_margin),
                                        int(left_margin),
                                        int(right_margin),
                                        int(start_second),
                                        int(end_second),
                                        int(thread_num)
                                    )
                                    logger.info(t("log_normal_complete"))
                                tc.time_end()

def jump_to_tutorial(event):
    webbrowser.open("https://www.bilibili.com/video/BV1qg411r7dV", new=0)


def set_coordinates_sample(ui):
    img2 = cv2.imread('sample2.jpg')
    img = cv2.imread('sample1.jpg')
    if img2 is None or img is None:
        ui.show_error_popup(t("sample_image_missing"))
    else:
        cv2.namedWindow("Sample_2", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Sample_2", (960,540))
        cv2.imshow('Sample_2', img2)

        cv2.namedWindow("Sample_1", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Sample_1", (960,540))
        cv2.imshow('Sample_1', img)

def set_coordinates_manually(ui, set_second_1, set_second_2):
    array_1.clear()
    array_2.clear()
    if check_set_second(ui, set_second_1):
        if check_set_second(ui, set_second_2):
            video_path = check_file_and_return_path(ui)
            if video_path:
                fps, lgt, hgt, frame_cnt = get_video_info(video_path)
                cap = cv2.VideoCapture(video_path)

                cap.set(
                    cv2.CAP_PROP_POS_FRAMES, int(fps * float(set_second_1))
                )
                ret, frame = cap.read()

                if ret:
                    cv2.namedWindow("Frame_1", cv2.WINDOW_NORMAL)
                    ui.show_instruction_popup(t("click_4_points"), button_text="proceed")
                    cv2.setWindowProperty("Frame_1", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                    cv2.imshow('Frame_1', frame)

                    cv2.setMouseCallback('Frame_1', mouse_callback_1, array_1)

                else:
                    ui.show_error_popup(t("frame_read_failed"))
                cv2.waitKey()
                if len(array_1) < 4:
                    ui.show_error_popup(t("not_4_points"))
                    if cv2.getWindowProperty('Frame_1', cv2.WND_PROP_VISIBLE):
                        cv2.destroyWindow('Frame_1')
                else:
                    cap.set(
                        cv2.CAP_PROP_POS_FRAMES, int(fps * float(set_second_2))
                    )
                    ret, frame = cap.read()
                    cap.release()

                    if ret:
                        cv2.namedWindow("Frame_2", cv2.WINDOW_NORMAL)
                        ui.show_instruction_popup(t("click_8_points"), button_text="proceed")
                        cv2.setWindowProperty("Frame_2", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                        cv2.imshow('Frame_2', frame)

                        cv2.setMouseCallback('Frame_2', mouse_callback_2, array_2)

                    else:
                        ui.show_error_popup(t("frame_read_failed"))
                    cv2.waitKey()
                    if len(array_2) < 8:
                        ui.show_error_popup(t("not_8_points"))
                        if cv2.getWindowProperty('Frame_2', cv2.WND_PROP_VISIBLE):
                            cv2.destroyWindow('Frame_2')
                set_coordinates_labels()
                        
def mouse_callback_1(event, x, y, flags, param):
    if len(param) >= 4:
        cv2.destroyWindow('Frame_1')
    elif event == cv2.EVENT_LBUTTONDOWN:
        coord = [y, x]
        param.append(coord)
        #print(f"ROI selected: ({y},{x}) ")
        #print(param)
        
def mouse_callback_2(event, x, y, flags, param):
    if len(param) >= 8:
        cv2.destroyWindow('Frame_2')
    elif event == cv2.EVENT_LBUTTONDOWN:
        coord = [y, x]
        param.append(coord)
        #print(f"ROI selected: ({y},{x}) ")
        #print(param)
            
class PointCoordinates:
    def __init__(self):
        self.p_m_y, self.p_m_x = 0, 0
        self.p_l_y, self.p_l_x = 0, 0
        self.m_p_m_y_2, self.m_p_m_x_2 = 0, 0

        self.m_p_l_y, self.m_p_l_x = 0, 0
        self.m_p_m_y, self.m_p_m_x = 0, 0
        self.m_p_r_y, self.m_p_r_x = 0, 0

        self.acc_l_y, self.acc_l_x = 0, 0
        self.acc_r_y, self.acc_r_x = 0, 0

        self.vp_y, self.vp_x_1, self.vp_x_2, self.vp_x_3, self.vp_x_4 = 0, 0, 0, 0, 0
        # self.vp_2_y, self.vp_2_x_1, self.vp_2_x_2, self.vp_2_x_3, self.vp_2_x_4 = (
            # 0,
            # 0,
            # 0,
            # 0,
            # 0
        # )

    def calculate_or_use_coordinates(
        self, lgt, hgt, top_margin, bottom_margin, left_margin, right_margin
    ):
        if ui.e_manual_set_or_not.current() == 1:
            self.acc_r_y = array_1[0][0]
            self.acc_r_x = array_1[0][1]
            self.acc_l_y = array_1[1][0]
            self.acc_l_x = array_1[1][1]
            self.p_m_y = array_1[2][0]
            self.p_m_x = array_1[2][1]
            self.p_l_y = array_1[3][0]
            self.p_l_x = array_1[3][1]
            self.m_p_l_y = array_2[0][0]
            self.m_p_l_x = array_2[0][1]
            self.m_p_m_y_2 = array_2[1][0]
            self.m_p_m_x_2 = array_2[1][1]
            self.m_p_m_y = array_2[2][0]
            self.m_p_m_x = array_2[2][1]
            self.m_p_r_y = array_2[3][0]
            self.m_p_r_x = array_2[3][1]
            self.vp_y = array_2[4][0]
            self.vp_x_1 = array_2[4][1]
            self.vp_x_2 = array_2[5][1]
            self.vp_x_3 = array_2[6][1]
            self.vp_x_4 = array_2[7][1]
        else:
            act_hgt = hgt - top_margin - bottom_margin
            act_lgt = lgt - left_margin - right_margin
            
            if act_lgt * 1080 < act_hgt * 1920:
                mdf_hgt = int(round(act_lgt / 1920 * 1080, 0))
            else:
                mdf_hgt = act_hgt

            self.p_m_y = int(round(P_M_Y_CO * mdf_hgt + top_margin, 0))
            self.p_m_x = int(round(lgt - P_M_X_CO * mdf_hgt - right_margin, 0))
            # right top || middle
            self.p_l_y = self.p_m_y
            self.p_l_x = int(round(lgt - P_L_X_CO * mdf_hgt - right_margin, 0))
            # right top || left

            self.m_p_m_y_2 = int(round(M_P_M_Y_2_CO * act_hgt + top_margin, 0))
            self.m_p_m_x_2 = int(
                round(M_P_M_X_2_CO * (lgt - left_margin - right_margin) + left_margin, 0)
            )
            # middle PAUSE point (black point)

            self.m_p_l_y = int(round(self.m_p_m_y_2 + M_P_L_Y_CO * mdf_hgt, 0))
            self.m_p_l_x = int(round(self.m_p_m_x_2 - M_P_L_X_CO * mdf_hgt, 0))
            # middle PAUSE left point (white point)
            self.m_p_m_y = int(round(self.m_p_m_y_2 + M_P_M_Y_CO * mdf_hgt, 0))
            self.m_p_m_x = self.m_p_m_x_2
            # middle PAUSE middle point (white point)
            self.m_p_r_y = int(round(self.m_p_m_y_2 - M_P_R_Y_CO * mdf_hgt, 0))
            self.m_p_r_x = int(round(self.m_p_m_x_2 + M_P_R_X_CO * mdf_hgt, 0))
            # middle PAUSE right point (white point)

            self.acc_l_y = int(round(ACC_L_Y_CO * mdf_hgt + top_margin, 0))
            self.acc_l_x = int(round(lgt - ACC_L_X_CO * mdf_hgt - right_margin, 0))
            self.acc_r_y = self.acc_l_y
            self.acc_r_x = int(round(lgt - ACC_R_X_CO * mdf_hgt - right_margin, 0))

            self.vp_y = int(round(VP_Y_CO * act_hgt + top_margin, 0))
            self.vp_x_1 = int(round(VP_X_1_CO * mdf_hgt + left_margin, 0))
            self.vp_x_2 = int(round(VP_X_2_CO * mdf_hgt + left_margin, 0))
            self.vp_x_3 = int(round(VP_X_3_CO * mdf_hgt + left_margin, 0))
            self.vp_x_4 = int(round(VP_X_4_CO * mdf_hgt + left_margin, 0))

            # self.vp_2_y = int(
                # round(VP_Y_CO * act_hgt + top_margin - (VP_Y_CO - VP_2_Y_CO) * mdf_hgt, 0)
            # )
            # self.vp_2_x_1 = int(round(VP_2_X_1_CO * mdf_hgt + left_margin, 0))
            # self.vp_2_x_2 = int(round(VP_2_X_2_CO * mdf_hgt + left_margin, 0))
            # self.vp_2_x_3 = int(round(VP_2_X_3_CO * mdf_hgt + left_margin, 0))
            # self.vp_2_x_4 = int(round(VP_2_X_4_CO * mdf_hgt + left_margin, 0))

            #print(self.p_m_y, self.p_m_x)
            #print(self.p_l_y, self.p_l_x)
            #print(self.m_p_m_y_2, self.m_p_m_x_2)
            #print(self.m_p_l_y, self.m_p_l_x)
            #print(self.m_p_m_y, self.m_p_m_x)
            #print(self.m_p_r_y, self.m_p_r_x)
            #print(self.acc_l_y, self.acc_l_x)
            #print(self.acc_r_y, self.acc_r_x)
            #print(self.vp_y, self.vp_x_1, self.vp_x_2, self.vp_x_3, self.vp_x_4)
            #print(self.vp_2_y, self.vp_2_x_1, self.vp_2_x_2, self.vp_2_x_3, self.vp_2_x_4)
        
        
def is_pause(frame, pc):
    if abs(
            float(sum(frame[pc.p_l_y, pc.p_l_x]) / len(frame[pc.p_l_y, pc.p_l_x]))
            - float(sum(frame[pc.p_m_y, pc.p_m_x]) / len(frame[pc.p_m_y, pc.p_m_x]))
            ) < P_DIFF_TH:
        return True
    white_points = [
        (pc.m_p_l_y, pc.m_p_l_x),
        (pc.m_p_m_y, pc.m_p_m_x),
        (pc.m_p_r_y, pc.m_p_r_x)
    ]
    if all(all(frame[y, x] > WHITE_10) for y, x in white_points):
        return True 
    if (
        all(frame[pc.m_p_m_y, pc.m_p_m_x] > GRAY)
        and all(abs(frame[pc.m_p_m_y, pc.m_p_m_x] - frame[pc.m_p_l_y, pc.m_p_l_x]) < M_P_DIFF_TH)
        and all(abs(frame[pc.m_p_m_y, pc.m_p_m_x] - frame[pc.m_p_r_y, pc.m_p_r_x]) < M_P_DIFF_TH)
        and all(abs(frame[pc.m_p_l_y, pc.m_p_l_x] - frame[pc.m_p_r_y, pc.m_p_r_x]) < M_P_DIFF_TH)
        and all(frame[pc.m_p_m_y_2, pc.m_p_m_x_2] < GRAY)
    ):
        return True
    return False

def is_acceleration(frame, pc):
    if all(frame[pc.acc_r_y, pc.acc_r_x] > WHITE_9) and any(
        frame[pc.acc_l_y, pc.acc_l_x] < WHITE_9
    ):
        return False
    return True

def is_valid_pause(frame, pc):
    #if all(frame[pc.vp_y +5, pc.vp_x_1]  < BLACK_9):
    for dy in [0, -1, 1]:  # offset
        row = pc.vp_y  + dy 
        if (all(GRAY_LOWER <= frame[row, pc.vp_x_1])
            and all(frame[row, pc.vp_x_1] <= GRAY_UPPER) 
            and all(GRAY_LOWER <= frame[row, pc.vp_x_2])
            and all(frame[row, pc.vp_x_2] <= GRAY_UPPER) 
            and all(GRAY_LOWER <= frame[row, pc.vp_x_3])
            and all(frame[row, pc.vp_x_3] <= GRAY_UPPER) 
            and all(GRAY_LOWER <= frame[row, pc.vp_x_4])
            and all(frame[row, pc.vp_x_4] <= GRAY_UPPER) 
        ):
            #print(frame[row, pc.vp_x_1],frame[row, pc.vp_x_2],frame[row, pc.vp_x_3],frame[row, pc.vp_x_4])
            return True 
    #white_cols = (pc.vp_2_x_1,  pc.vp_2_x_2,  pc.vp_2_x_3,  pc.vp_2_x_4) 
    #return any(all(frame[pc.vp_2_y, col] > WHITE_10) for col in white_cols)

def expand_valid_pause_range(frame_cnt, pause_y_n, vp_y_n):
    for i in range(1, frame_cnt - 1):
        if vp_y_n[i] == True and vp_y_n[i - 1] == False and pause_y_n[i - 1] == True:
            a = i - 1
            while pause_y_n[a] == True and a >= 0:
                vp_y_n[a] = True
                a -= 1
        elif vp_y_n[i] == True and vp_y_n[i + 1] == False and pause_y_n[i + 1] == True:
            a = i + 1
            while pause_y_n[a] == True and a < frame_cnt:
                vp_y_n[a] = True
                a += 1
            i = a
            
def remove_ignore_frame_cnt_part(frame_cnt, keep_frame_y_n, vp_y_n):
    a = 0
    start = 0
    flag = 0 
    #flag 0 means keep frame_y_n = True, 1 means vp_y_n = True
    for i in range(1, frame_cnt - 1):
        if keep_frame_y_n[i] == True:
            if flag == 0:
                a += 1
            else:
                if a <= int(ui.e_ignore_frame_cnt.get()):
                    for j in range(start, i - 1):
                        vp_y_n[j] = False
                a = 0
                start = i
                flag = 0
        elif vp_y_n[i] == True:
            if flag == 1:
                a += 1
            else:
                if a <= int(ui.e_ignore_frame_cnt.get()):
                    for j in range(start, i - 1):
                        keep_frame_y_n[j] = False
                a = 0
                start = i
                flag = 1

def print_progress(i, start, end, start_key, end_key, *format_args):
    if i == start:
        logger.info(t(start_key).format(*format_args) if format_args else t(start_key))
    elif i == end:
        logger.info(t(end_key).format(*format_args) if format_args else t(end_key))
    elif (
        (i - start) % ((end - start) / SHOW_PROGRESS_SEG) < 1 and i > start and i < end
    ):
        logger.info(f"{(i - start) / (end - start):.0%}")

def get_file_suffix(vp_value, pause_value):
    if vp_value == True:
        return t("valid_pause")
    elif pause_value == True:
        return t("invalid_pause")
    else:
        return ""

def cleanup(working_path):
    tc = TimeCost()
    tc.time_start(t("log_timing_cleaning_segments"))
    for root, dirs, files in os.walk(working_path):
        for name in files:
            full_file_path = os.path.join(root, name)
            if name.startswith(TEMP_PREFIX):
                os.remove(full_file_path)
                # Remove from cache if present
                if full_file_path in _video_metadata_cache:
                    del _video_metadata_cache[full_file_path]
            elif get_frame_cnt(full_file_path) <= int(ui.e_ignore_frame_cnt.get()) and full_file_path.lower().endswith('.mp4'):
                os.remove(full_file_path)
                # Remove from cache if present
                if full_file_path in _video_metadata_cache:
                    del _video_metadata_cache[full_file_path]
                logger.info(t("log_segment_deleted").format(name))
    tc.time_end()


def update_entry_state(event):
    """Enable/disable widgets based on manual detection mode"""
    if ui.e_manual_set_or_not.current() == 1:
        ui.e_top_margin.config(state="disable")
        ui.e_bottom_margin.config(state="disable")
        ui.e_left_margin.config(state="disable")
        ui.e_right_margin.config(state="disabled")
        ui.b_save_settings.config(state="disabled")
        ui.e_measure_margin_second.config(state="disabled")
        ui.b_measure_margin.config(state="disabled")
        ui.b_crop.config(state="disabled")
        ui.b_cut_with_crop.config(state="disabled")
        ui.e_manual_set_second_1.config(state="normal")
        ui.e_manual_set_second_2.config(state="normal")
        ui.b_manual_set.config(state="normal")
        ui.b_manual_set_sample.config(state="normal")
        ui.b_manual_set_save.config(state="normal")
    else:
        ui.e_top_margin.config(state="normal")
        ui.e_bottom_margin.config(state="normal")
        ui.e_left_margin.config(state="normal")
        ui.e_right_margin.config(state="normal")
        ui.b_save_settings.config(state="normal")
        ui.e_measure_margin_second.config(state="normal")
        ui.b_measure_margin.config(state="normal")
        ui.b_crop.config(state="normal")
        ui.b_cut_with_crop.config(state="normal")
        ui.e_manual_set_second_1.config(state="disabled")
        ui.e_manual_set_second_2.config(state="disabled")
        ui.b_manual_set.config(state="disabled")
        ui.b_manual_set_sample.config(state="disabled")
        ui.b_manual_set_save.config(state="disabled")  

class TimeCost:
    def __init__(self):
        self.start = datetime
        self.end = datetime

    def time_start(self, process_name):
        self.start = datetime.datetime.now()
        logger.info(t("log_timing_for").format(process_name))
        logger.info(t("log_timing_started").format(self.start))

    def time_end(self):
        self.end = datetime.datetime.now()
        logger.info(t("log_timing_ended").format(self.end))
        logger.info(t("log_time_elapsed").format(self.end - self.start))


def lazy_pause_analyze(
    process_num, start_f, end_f, start, end, cap, pc, pause_y_n, vp_y_n, keep_frame_y_n
):   
    cap.set(cv2.CAP_PROP_POS_FRAMES, start)
    skip = True
    for i in range(start, end + 1):
        if i <= end_f:
            ret, frame = cap.read()
        if i < start_f or i > end_f:
            keep_frame_y_n[i] = True
        else:
            # try: 
               # is_pause(frame, pc)
            # except Exception as e:
                # print(frame[pc.p_l_y, pc.p_l_x])
                # if os.path.exists(path + "/log.txt"):
                    # f = open(path + "/log.txt", "a")                  
                    # f.write("error frame is " + str(i) + "\n")
                    # f.close()
            # else:
            if not is_pause(frame, pc):
                if not is_acceleration(frame, pc):
                    if skip:
                        skip = False
                    else:
                        skip = True
                        keep_frame_y_n[i] = True
                else:
                    keep_frame_y_n[i] = True
            else:
                pause_y_n[i] = True
                if is_valid_pause(frame, pc):
                    vp_y_n[i] = True
        print_progress(
            i,
            start,
            end,
            "log_thread_analyze_pause_start",
            "log_thread_100_percent",
            process_num,
        )
    cap.release()

def lazy_video_generate(
    process_num, start, end, cap, keep_frame_y_n, vp_y_n, fps, lgt, hgt
):
    size = (lgt, hgt)  
    out = cv2.VideoWriter(
        working_path + TEMP_PREFIX + str(process_num) + ".mp4", FOURCC, fps, size
    )
    cap.set(cv2.CAP_PROP_POS_FRAMES, start)
    for i in range(start, end):
        ret, frame = cap.read()
        if keep_frame_y_n[i] == True or vp_y_n[i] == True:
            out.write(frame)
        print_progress(
            i,
            start,
            end - 1,
            "log_thread_cut_pause_accel_start",
            "log_thread_100_percent",
            process_num,
        )

    out.release()
    # print("Thread " + str(process_num) + " generated file out_" + str(index) + vp + ".mp4")
    cap.release()

def lazy_video_generate_2(
    process_num, start_f, end_f, start, end, cap, pc, fps, lgt, hgt
):
    size = (lgt, hgt)
    out = cv2.VideoWriter(
        working_path + TEMP_PREFIX + str(process_num) + ".mp4", FOURCC, fps, size
    )
    cap.set(cv2.CAP_PROP_POS_FRAMES, start)
    skip = True
    for i in range(start, end):
        ret, frame = cap.read()
        if i < start_f or i > end_f:
            out.write(frame)
        else:
            if not is_pause(frame, pc):
                if not is_acceleration(frame, pc):
                    if skip:
                        skip = False
                    else:
                        skip = True
                        out.write(frame)
                else:
                    out.write(frame)
            print_progress(
                i,
                start,
                end - 1,
                "log_thread_cut_pause_accel_start",
                "log_thread_100_percent",
                process_num,
            )
    out.release()
    cap.release()

def lazy_version(
    video_path,
    mode,
    top_margin,
    bottom_margin,
    left_margin,
    right_margin,
    start_second,
    end_second,
    thread_num
):
    fps, lgt, hgt, frame_cnt = get_video_info(video_path)

    start_f = start_second * fps  # start frame (will keep frames before this)
    end_f = end_second * fps  # end frame   (will keep frames after this)

    pc = PointCoordinates()
    pc.calculate_or_use_coordinates(
        lgt, hgt, top_margin, bottom_margin, left_margin, right_margin
    )

    pause_y_n = np.full(frame_cnt, False)  # True means a pause, False means not a pause
    vp_y_n = np.full(frame_cnt, False)
    keep_frame_y_n = np.full(frame_cnt, False)  # True means keep, False means no keep
    frame_per_thread = math.floor(frame_cnt / thread_num)

    tc = TimeCost()

    if mode == 2:  # "Lazy mode (keep valid pauses)" index
        tc.time_start(t("log_timing_analyzing_pauses"))

        threads = []

        for thread_idx in range(thread_num):
            cap_t = cv2.VideoCapture(video_path)

            start = thread_idx * frame_per_thread
            end = (thread_idx + 1) * frame_per_thread - 1

            #print("start is", start, ", end is ", end)

            thread = threading.Thread(
                target=lazy_pause_analyze,
                args=(
                    thread_idx,
                    start_f,
                    end_f,
                    start,
                    end,
                    cap_t,
                    pc,
                    pause_y_n,
                    vp_y_n,
                    keep_frame_y_n,
                )
            )

            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        expand_valid_pause_range(frame_cnt, pause_y_n, vp_y_n)
        
        # for i in range(2760, len(keep_frame_y_n)):
            # print("i is ", i, ", keep is ", keep_frame_y_n[i])
        
        if int(ui.e_ignore_frame_cnt.get()) > 0:
            remove_ignore_frame_cnt_part(frame_cnt, keep_frame_y_n, vp_y_n)
        
        
        tc.time_end()

        tc.time_start(t("log_timing_generating_video"))

        threads = []
        f = open(working_path + TEMP_FILENAME, "w")

        for thread_idx in range(thread_num):
            cap_t = cv2.VideoCapture(video_path)

            start = thread_idx * frame_per_thread
            end = (thread_idx + 1) * frame_per_thread if thread_idx != thread_num - 1 else frame_cnt

            thread = threading.Thread(
                target=lazy_video_generate,
                args=(thread_idx, start, end, cap_t, keep_frame_y_n, vp_y_n, fps, lgt, hgt)
            )
            threads.append(thread)
            thread.start()

            f.write("file " + TEMP_PREFIX + str(thread_idx) + ".mp4" + "\n")

        f.close()

        for thread in threads:
            thread.join()

        tc.time_end()

    elif mode == 3:  # Lazy mode (cut all pauses)
        tc.time_start(t("log_timing_generating_video"))

        threads = []
        f = open(working_path + TEMP_FILENAME, "w")

        for thread_idx in range(thread_num):
            cap_t = cv2.VideoCapture(video_path)

            start = thread_idx * frame_per_thread
            end = (thread_idx + 1) * frame_per_thread

            thread = threading.Thread(
                target=lazy_video_generate_2,
                args=(thread_idx, start_f, end_f, start, end, cap_t, pc, fps, lgt, hgt)
            )
            threads.append(thread)
            thread.start()

            f.write("file " + TEMP_PREFIX + str(thread_idx) + ".mp4" + "\n")

        f.close()

        for thread in threads:
            thread.join()

        tc.time_end()

    #cleanup below
    subprocess.call(
        "ffmpeg -loglevel quiet -f concat -safe 0 -i "
        + working_path
        + TEMP_FILENAME
        + " -c copy "
        + working_path
        + "output.mp4",
        shell=True,
    )

    os.remove(working_path + TEMP_FILENAME)
    
    cleanup(working_path)
        

def normal_get_video_audio_bounds(frame_cnt, frame_per_thread, pause_y_n, thread_num):
    bounds = [0]
    seg_cnts = [0]
    seg_cnt = 0
    check = False
    for i in range(1, frame_cnt):
        if len(bounds) == thread_num:
            break
        if pause_y_n[i] != pause_y_n[i - 1]:
            seg_cnt += 1
        if pause_y_n[i] == pause_y_n[i - 1] and i >= frame_per_thread * len(bounds):
            check = True
        elif check and pause_y_n[i] != pause_y_n[i - 1]:
            bounds += [i]
            check = False
            seg_cnts += [seg_cnt]
    return bounds, seg_cnts

def normal_pause_analyze(
    process_num, start_f, end_f, start, end, cap, pc, pause_y_n, vp_y_n
):
    if end_f < start or end < start_f:
        logger.info(t("log_thread_no_intersection").format(process_num))
    else:
        if start < start_f:
            start = start_f
        cap.set(cv2.CAP_PROP_POS_FRAMES, start)
        for i in range(start, end + 1):
            if i <= end_f:
                ret, frame = cap.read()
            if i >= start_f and i <= end:
                if is_pause(frame, pc):
                    pause_y_n[i] = True
                    if is_valid_pause(frame, pc):
                        vp_y_n[i] = True
                        #print("frame ", i, " is valid pause")
                print_progress(
                    i,
                    start,
                    end,
                    "log_thread_analyze_pause_start",
                    "log_thread_100_percent",
                    process_num,
                )
        cap.release()

def normal_video_generate(
    process_num, start_index, start, end, cap, pause_y_n, vp_y_n, fps, lgt, hgt
):
    size = (lgt, hgt) 
    index = start_index
    vp = get_file_suffix(vp_y_n[start], pause_y_n[start])
    out = cv2.VideoWriter(
        working_path + TEMP_PREFIX + str(index) + vp + ".mp4", FOURCC, fps, size
    )
    cap.set(cv2.CAP_PROP_POS_FRAMES, start)
    ret, frame = cap.read()
    out.write(frame)
    for i in range(start + 1, end):
        ret, frame = cap.read()
        if pause_y_n[i] != pause_y_n[i - 1]:
            out.release()
            # print("Thread " + str(process_num) + " generated file out_" + str(index) + vp + ".mp4")
            index += 1
            vp = get_file_suffix(vp_y_n[i], pause_y_n[i])
            out = cv2.VideoWriter(
                working_path + TEMP_PREFIX + str(index) + vp + ".mp4", FOURCC, fps, size
            )
        out.write(frame)
        print_progress(
            i,
            start + 1,
            end - 1,
            "log_thread_generate_video_start",
            "log_thread_100_percent",
            process_num,
        )

    out.release()
    # print("Thread " + str(process_num) + " generated file out_" + str(index) + vp + ".mp4")
    cap.release()

def normal_audio_generate(
    process_num, start_index, start, end, sound, pause_y_n, vp_y_n, fps
):
    start_seg = start
    inc = 1 / fps * 1000
    index = start_index
    vp = get_file_suffix(vp_y_n[start], pause_y_n[start])

    for i in range(start + 1, end):
        if pause_y_n[i] != pause_y_n[i - 1]:
            out_a = sound[start_seg * inc : i * inc + fps]
            # print("start is ", start_seg * inc, ", end is ", i * inc + fps)
            out_a.export(working_path + TEMP_PREFIX + str(index) + vp + ".mp3")
            # print("Thread " + str(process_num) + " generated file out_" + str(index) + vp + ".mp3")
            vp = get_file_suffix(vp_y_n[i], pause_y_n[i])
            index += 1
            start_seg = i
    out_a = sound[start_seg * inc : i * inc + fps]
    # print("start is ", start_seg * inc, ", end is ", i * inc + fps)
    out_a.export(working_path + TEMP_PREFIX + str(index) + vp + ".mp3")
    # print("Thread " + str(process_num) + " generated file out_" + str(index) + vp + ".mp3")

def normal_combine(process_num, prefix, start, end, has_sound, mode):
    for i in range(start, end):
        j = prefix + i
        old_name = working_path + TEMP_PREFIX + str(i)
        new_name = working_path + str(j)
        if has_sound:
            subprocess.call(
                "ffmpeg -loglevel quiet -i "
                + old_name
                + ".mp4"
                + " -i "
                + old_name
                + ".mp3"
                + " -c:v copy -c:a aac "
                + new_name
                + ".mp4",
                shell=True,
            )
            subprocess.call(
                "ffmpeg -loglevel quiet -i "
                + old_name
                + t("valid_pause") + ".mp4"
                + " -i "
                + old_name
                + t("valid_pause") + ".mp3"
                + " -c:v copy -c:a aac "
                + new_name
                + t("valid_pause") + ".mp4",
                shell=True,
            )
            if mode == 1:  # Normal mode (keep invalid pause video)
                subprocess.call(
                    "ffmpeg -loglevel quiet -i "
                    + old_name
                    + t("invalid_pause") + ".mp4"
                    + " -i "
                    + old_name
                    + t("invalid_pause") + ".mp3"
                    + " -c:v copy -c:a aac "
                    + new_name
                    + t("invalid_pause") + ".mp4",
                    shell=True,
                )
            else:
                try:
                    os.rename(                        
                        old_name + t("invalid_pause") + ".mp3",
                        new_name + t("invalid_pause") + ".mp3",
                    )
                except:
                    dummy = 0
            print_progress(
                i,
                start,
                end - 1,
                "log_thread_merge_audio_video_start",
                "log_thread_100_percent",
                process_num,
            )
            i = i + 1
        else:
            try:
                os.rename(
                    old_name + ".mp4",
                    new_name + ".mp4",
                )
            except:
                dummy = 0
            try:
                os.rename(
                    old_name + t("valid_pause") + ".mp4",
                    new_name + t("valid_pause") + ".mp4",
                )
            except:
                dummy = 0
            if mode == 1:  # Normal mode (keep invalid pause video)
                try:
                    os.rename(
                        old_name + t("invalid_pause") + ".mp4",
                        new_name + t("invalid_pause") + ".mp4",
                    )
                except:
                    dummy = 0
            print_progress(
                i,
                start,
                end - 1,
                "log_thread_no_audio_rename",
                "log_thread_100_percent",
                process_num,
            )



def normal_version(
    video_path,
    mode,
    top_margin,
    bottom_margin,
    left_margin,
    right_margin,
    start_second,
    end_second,
    thread_num
):
    fps, lgt, hgt, frame_cnt = get_video_info(video_path)

    start_f = start_second * fps  # start frame (will keep frames before this)
    end_f = end_second * fps  # end frame   (will keep frames after this)

    pc = PointCoordinates()
    pc.calculate_or_use_coordinates(
        lgt, hgt, top_margin, bottom_margin, left_margin, right_margin
    )

    pause_y_n = np.full(frame_cnt, False)  # True means a pause, False means not a pause
    vp_y_n = np.full(frame_cnt, False)

    tc = TimeCost()

    tc.time_start(t("log_timing_analyzing_pauses"))

    threads = []
    frame_per_thread = math.floor(frame_cnt / thread_num)

    for thread_idx in range(thread_num):
        # Create independent VideoCapture object to avoid resource conflicts
        cap_t = cv2.VideoCapture(video_path)

        # Calculate frame range for each thread
        start = thread_idx * frame_per_thread if thread_idx != 0 else start_f
        end = (thread_idx + 1) * frame_per_thread - 1 if thread_idx != thread_num - 1 else end_f

        # Create thread
        thread = threading.Thread(
            target=normal_pause_analyze,
            args=(thread_idx, start_f, end_f, start, end, cap_t, pc, pause_y_n, vp_y_n)
        )

        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    expand_valid_pause_range(frame_cnt, pause_y_n, vp_y_n)
    
    tc.time_end()

    tc.time_start(t("log_timing_generating_video_segments"))

    bounds, seg_cnts = normal_get_video_audio_bounds(
        frame_cnt, frame_per_thread, pause_y_n, thread_num
    )
    # print ("bounds are ", bounds)
    # print ("seg_cnts are ", seg_cnts)
    
    threads = []

    for thread_idx in range(len(bounds)):
        cap_t = cv2.VideoCapture(video_path)

        start = bounds[thread_idx]
        end = bounds[thread_idx + 1] if thread_idx != len(bounds) - 1 else frame_cnt
        start_index = seg_cnts[thread_idx]

        thread = threading.Thread(
            target=normal_video_generate,
            args=(thread_idx, start_index, start, end, cap_t, pause_y_n, vp_y_n, fps, lgt, hgt)
        )
        # print("args are ", thread_idx, start_index, start, end)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    tc.time_end()

    has_sound = True
    try:
        sound = AudioSegment.from_file(
            video_path, format=os.path.splitext(video_path)[1].lstrip('.')
        )
    except:
        has_sound = False

    if has_sound:
        tc.time_start(t("log_timing_generating_audio_segments"))

        threads = []

        for thread_idx in range(len(bounds)):
            start = bounds[thread_idx]
            end = bounds[thread_idx + 1] if thread_idx != len(bounds) - 1 else frame_cnt
            start_index = seg_cnts[thread_idx]

            thread = threading.Thread(
                target=normal_audio_generate,
                args=(thread_idx, start_index, start, end, sound, pause_y_n, vp_y_n, fps)
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        tc.time_end()

    working_folder_list = os.listdir(working_path)

    if has_sound:
        count = int((len(working_folder_list) - 1) / 2)
    else:
        count = len(working_folder_list) - 1

    tc.time_start(t("log_timing_merging_video_audio"))

    threads = []
    file_per_thread = math.floor(count / thread_num)

    for thread_idx in range(thread_num):

        start = thread_idx * file_per_thread
        end = (thread_idx + 1) * file_per_thread if thread_idx != thread_num - 1 else count
        prefix = pow(10, len(str(count)))

        thread = threading.Thread(
            target=normal_combine, args=(thread_idx, prefix, start, end, has_sound, mode)
        )

        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    tc.time_end()

    cleanup(working_path)
    
# main here
win = Tk()
ui = MainWindow(win, working_path, DEFAULT_LANGUAGE)

# Set default values
set_margin(0, 0, 0, 0)
ui.e_thread_num.insert(0, DEFAULT_THREAD_NUM)
ui.e_ignore_frame_cnt.insert(0, DEFAULT_IGNORE_FRAME_CNT)

# Disable manual detection controls initially
ui.e_manual_set_second_1.config(state="disabled")
ui.e_manual_set_second_2.config(state="disabled")
ui.b_manual_set.config(state="disabled")
ui.b_manual_set_sample.config(state="disabled")
ui.b_manual_set_save.config(state="disabled")

# Register callbacks for UI events
ui.b_show_desc.config(command=show_desc)
ui.e_language.bind("<<ComboboxSelected>>", change_language)
ui.e_manual_set_or_not.bind("<<ComboboxSelected>>", update_entry_state)
ui.l_tutorial_url.bind("<ButtonPress-1>", jump_to_tutorial)

ui.b_save_settings.config(
    command=lambda: save_settings(
        ui,
        ui.e_mode.current(),
        ui.e_top_margin.get(),
        ui.e_bottom_margin.get(),
        ui.e_left_margin.get(),
        ui.e_right_margin.get(),
        ui.e_thread_num.get(),
        ui.e_ignore_frame_cnt.get()
    )
)

ui.b_measure_margin.config(
    command=lambda: measure_margin(ui, ui.e_measure_margin_second.get())
)

ui.b_crop.config(
    command=lambda: crop(
        ui,
        ui.e_top_margin.get(),
        ui.e_bottom_margin.get(),
        ui.e_left_margin.get(),
        ui.e_right_margin.get()
    )
)

ui.b_cut_without_crop.config(
    command=lambda: cut_without_crop(
        ui,
        ui.e_mode.current(),
        ui.e_top_margin.get(),
        ui.e_bottom_margin.get(),
        ui.e_left_margin.get(),
        ui.e_right_margin.get(),
        ui.e_start_second.get(),
        ui.e_end_second.get(),
        ui.e_thread_num.get(),
        ui.e_ignore_frame_cnt.get()
    )
)

ui.b_cut_with_crop.config(
    command=lambda: cut_with_crop(
        ui,
        ui.e_mode.current(),
        ui.e_start_second.get(),
        ui.e_end_second.get(),
        ui.e_thread_num.get(),
        ui.e_measure_margin_second.get(),
        ui.e_ignore_frame_cnt.get()
    )
)

ui.b_manual_set.config(
    command=lambda: set_coordinates_manually(ui, ui.e_manual_set_second_1.get(), ui.e_manual_set_second_2.get())
)

ui.b_manual_set_sample.config(
    command=lambda: set_coordinates_sample(ui)
)

ui.b_manual_set_save.config(
    command=lambda: manual_set_save(ui)
)

# Load settings if file exists
if os.path.exists(path + "/settings.txt"):
    with open(path + "/settings.txt") as f:
        ui.e_mode.current(int(f.readline()))
        set_margin(
            int(f.readline()), int(f.readline()), int(f.readline()), int(f.readline())
        )
        set_thread_num(int(f.readline()))
        set_ignore_frame_cnt(int(f.readline()))
        # Read language preference
        lang_line = f.readline().strip()
        if lang_line:
            set_language(lang_line)
            current_language = get_current_language()
            ui.e_language.current(0 if current_language == "cn" else 1 if current_language == "en" else 2)
            ui.update_all_text()

set_coordinates()

# Register language change callback
register_language_change_callback(update_all_text)

win.mainloop()
