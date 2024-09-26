# 自动化识别框架

这是在帮助我的好朋友实现 `抖店自动发送消息` 的时候实现的一个框架，本来很简陋，然后被我硬生生的拿来做了一个简单的自动化识别框架，现在手游一开刷个牙回来就刷完了

## 技术栈

- pandas
- cv2
- pyautogui
- functools

## 常用的几个方法

- `click_image` 点击图片
- `click_image_until_another_appears` 点击图片直到下一个图片出现
- `click_image_sequence` 点击一系列图片，可以传入 List
- `type_text` 输入文字
- `screenshot_and_click` OCR后找到指定文字点击
- `process_screenshot_for_ocr` OCR图片得到数据

## 心理测试自动化逻辑（招聘用）

@todo 主要是有图片，有时间单独开一个仓库公开代码

## 物华弥新自动化逻辑

@todo 主要是有图片，有时间单独开一个仓库公开代码

## 框架代码

```python
import hashlib
import math
import pandas as pd
import pyperclip
import requests
import base64
import cv2
import pyautogui
import time
import random
import numpy as np
import logging
from io import BytesIO
from functools import wraps
from functools import lru_cache
from config import SCREENSHOT_REGION

logging.basicConfig(level=logging.INFO)


def retry_on_failure(retries=3, delay=1):
    """
    装饰器，用于在函数失败时重试
    :param retries: 重试次数
    :param delay: 重试间隔时间
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                result = func(*args, **kwargs)
                if result:
                    return result
                logging.warning(f"尝试 {attempt + 1} 失败，正在重试...")
                time.sleep(delay)
            logging.error(f"所有 {retries} 次尝试失败。")
            return None

        return wrapper

    return decorator


class AutomationTool:
    # 定义常量
    LEFT = 'left'
    RIGHT = 'right'
    FULL = 'full'

    # 缓存最近一次的截图和 OCR 结果
    _last_screenshot = None
    _last_screenshot_time = 0
    _last_screenshot_hash = None
    _last_ocr_result = None
    _screenshot_cache_duration = 1  # 缓存持续时间（秒）

    UMI_OCR_URL = "http://127.0.0.1:1224/api/ocr"

    @staticmethod
    @lru_cache(maxsize=None)
    def read_excel(excel_path, usecols="A") -> pd.DataFrame:
        """
        读取Excel文件中指定的列数据
        :param excel_path: Excel文件路径
        :param usecols: 要读取的列（默认读取第A列）
        :return: 包含指定列数据的DataFrame
        """
        df = pd.read_excel(excel_path, usecols=usecols)
        return df

    @staticmethod
    def ocr_image(base64_image_data):
        """
        发送HTTP请求到Umi-OCR
        :param base64_image_data:
        :return:
        """
        try:
            response = requests.post(AutomationTool.UMI_OCR_URL, json={ "base64": base64_image_data })
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"OCR请求失败: {e}")
            return None

    @staticmethod
    def capture_screenshot():
        """
        截取屏幕并返回PIL格式的图像
        :return:
        """
        # 如果SCREENSHOT_REGION为空
        region = SCREENSHOT_REGION if SCREENSHOT_REGION else AutomationTool.FULL
        # 判断SCREENSHOT_REGION（截图是左半部分还是全屏幕）
        if region == AutomationTool.LEFT:
            logging.info("截取屏幕的左半部分")
            return AutomationTool.capture_screenshot_half(AutomationTool.LEFT)
        elif region == AutomationTool.RIGHT:
            logging.info("截取屏幕的右半部分")
            return AutomationTool.capture_screenshot_half(AutomationTool.RIGHT)
        elif region == AutomationTool.FULL:
            logging.info("截取整个屏幕")
            return pyautogui.screenshot()
        else:
            raise ValueError("截图区域无效。请使用'left'、'right'或'full'")

    @staticmethod
    def capture_screenshot_half(side=LEFT):
        """
        截取屏幕的左半部分或右半部分
        :param side: 'left' 或 'right'，默认为 'left'
        :return: 截取的图像
        """
        # 获取屏幕的宽度和高度
        screen_width, screen_height = pyautogui.size()
        # 截取整个屏幕
        screenshot = pyautogui.screenshot()
        # 计算宽度的 73%
        width_73_percent = int(screen_width * 0.73)
        
        if side == AutomationTool.LEFT:
            # 裁剪出左半部分
            half = screenshot.crop((0, 0, width_73_percent, screen_height))
        elif side == AutomationTool.RIGHT:
            # 裁剪出右半部分
            half = screenshot.crop((screen_width - width_73_percent, 0, screen_width, screen_height))
        else:
            raise ValueError("无效的side参数。请使用'left'或'right'")
        
        # half.save(f"{side}_region.png") # 调试使用
        return half

    @staticmethod
    def convert_image_to_base64(pil_image) -> str:
        """
        将PIL格式图像转换为Base64编码
        :param pil_image:
        :return:
        """
        buffered = BytesIO()
        pil_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return img_base64

    @staticmethod
    def convert_image_to_opencv(pil_image):
        """
        将PIL格式图像转换为OpenCV格式
        :param pil_image:
        :return:
        """
        np_image = np.array(pil_image)
        return cv2.cvtColor(np_image, cv2.COLOR_RGB2BGR)

    @staticmethod
    def extract_text_in_box(ocr_data, x1, y1, x2, y2):
        """
        提取给定坐标框内的文字。
        :param ocr_data: OCR 结果数据
        :param x1, y1, x2, y2: 指定的坐标框 (左上角 x1, y1 和 右下角 x2, y2)
        :return: 识别到的文字
        """
        for item in ocr_data['data']:
            box = item['box']
            text = item['text']
            x_min = min([point[0] for point in box])
            y_min = min([point[1] for point in box])
            x_max = max([point[0] for point in box])
            y_max = max([point[1] for point in box])
            # 判断 box 是否在指定范围内
            if x_min >= x1 and y_min >= y1 and x_max <= x2 and y_max <= y2:
                return text
        return None

    @staticmethod
    def click_on_text(ocr_data, target_text):
        """
        根据识别到的文字，移动鼠标并点击目标文字的位置
        :param ocr_data:
        :param target_text:
        :return:
        """
        for item in ocr_data['data']:
            text = item['text']
            if target_text in text:
                box = item['box']
                x_min = min([point[0] for point in box])
                y_min = min([point[1] for point in box])
                x_max = max([point[0] for point in box])
                y_max = max([point[1] for point in box])
                # 计算中心位置并添加随机偏移
                center_x = (x_min + x_max) // 2 + AutomationTool.human_like_offset()
                center_y = (y_min + y_max) // 2 + AutomationTool.human_like_offset()
                # 获取当前鼠标位置
                current_x, current_y = pyautogui.position()
                # 模拟人类鼠标移动
                AutomationTool.move_mouse_smoothly((current_x, current_y), (center_x, center_y))
                # 等待随机时间
                time.sleep(AutomationTool.human_like_delay())
                # 点击
                pyautogui.click()
                logging.info(f"点击了文字: {text}, 位置: {center_x}, {center_y}")
                return True
        logging.warning(f"未找到目标文字: {target_text}")
        return False

    @staticmethod
    def type_text(input_text):
        """
        像粘贴一样在当前焦点输入框中快速输入指定文字
        :param input_text:
        :return:
        """
        try:
            # 将文本复制到剪贴板
            pyperclip.copy(str(input_text))
            # 模拟 Ctrl + V 粘贴（Windows/Linux），或者 Command + V（macOS）
            pyautogui.hotkey('ctrl', 'v')
        except Exception as e:
            logging.error(f"输入文字失败: {e}")

    @staticmethod
    @retry_on_failure(retries=3, delay=1)
    def screenshot_and_click(target_text):
        """
        截图并点击指定文字
        :param target_text:
        :return:
        """
        ocr_data = AutomationTool.process_screenshot_for_ocr()
        if ocr_data:
            # 根据目标文字进行点击
            clicked = AutomationTool.click_on_text(ocr_data, target_text)
            if clicked:
                time.sleep(1)
            logging.info(f"成功点击目标文字: {target_text}")
            return True
        else:
            logging.warning(f"未找到目标文字: {target_text}")
            return False

    @staticmethod
    def find_text_in_screen(target_text: str) -> bool:
        """
        截图并判断是否存在某个文字
        :param target_text:
        :return:
        """
        ocr_data = AutomationTool.process_screenshot_for_ocr()
        if ocr_data:
            # 遍历所有识别到的文字，判断是否已经包含了发送的消息
            for item in ocr_data['data']:
                if target_text in item['text']:
                    logging.info(f"找到相应目标文字：{target_text}")
                    return True
        logging.warning(f"未找到相应目标文字：{target_text}")
        return False

    @staticmethod
    def find_image_in_screenshot(template_path, threshold=0.8):
        """
        在屏幕截图中查找给定图片模板（使用灰度图）
        :param template_path:
        :param threshold: 匹配阈值
        :return:
        """
        screenshot = AutomationTool.capture_screenshot()
        screenshot_cv = AutomationTool.convert_image_to_opencv(screenshot)
        # 转换为灰度图
        screenshot_gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
        # 读取模板图片并转换为灰度图
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            logging.error(f"无法读取模板图片：{template_path}")
            return None
        # 获取模板的宽高
        h, w = template.shape[:2]
        # 使用模板匹配查找模板
        res = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        # 获取最佳匹配位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > threshold:
            top_left = max_loc
            center_x = top_left[0] + w // 2
            center_y = top_left[1] + h // 2
            return center_x, center_y
        else:
            logging.info("未找到匹配的图片")
            return None

    @staticmethod
    @retry_on_failure(retries=3, delay=2)
    def click_image(template_path):
        """
        在屏幕上查找图片并点击
        :param template_path:
        :return:
        """
        position = AutomationTool.find_image_in_screenshot(template_path)
        logging.info(f"图片位置: {position}")
        if position:
            # 获取当前鼠标位置
            current_x, current_y = pyautogui.position()
            # 移动鼠标到目标位置
            AutomationTool.move_mouse_smoothly((current_x, current_y), position, duration=0.3)
            # 等待随机时间
            time.sleep(AutomationTool.human_like_delay())
            # 点击
            pyautogui.click()
            logging.info(f"点击了图片位置: {position}")
            return True
        else:
            logging.warning(f"未找到图片: {template_path}")
            return False
    
    @staticmethod
    def click_image_until_another_appears(click_image_path, stop_image_path, max_attempts=10, delay_between_clicks=1):
        """
        持续点击一个图片，直到另一个图片出现为止。

        :param click_image_path: 要点击的图片路径
        :param stop_image_path: 出现后停止点击的图片路径
        :param max_attempts: 最大尝试次数
        :param delay_between_clicks: 每次点击之间的延迟（秒）
        :return: 如果成功找到停止图片返回True，否则返回False
        """
        for attempt in range(max_attempts):
            # 检查停止图片是否出现
            if AutomationTool.find_image_in_screenshot(stop_image_path):
                logging.info(f"找到停止图片: {stop_image_path}")
                return True

            # 点击指定图片
            AutomationTool.click_image(click_image_path)
            logging.info(f"点击图片: {click_image_path}，尝试次数: {attempt + 1}")

            # 等待指定时间
            time.sleep(delay_between_clicks)

        logging.warning(f"达到最大尝试次数 {max_attempts}，未找到停止图片: {stop_image_path}")
        return False

    @staticmethod
    def process_screenshot_for_ocr():
        """
        截取屏幕并进行 OCR 处理，使用缓存优化
        :return: OCR 数据
        """
        current_time = time.time()
        # 检查缓存是否有效
        if AutomationTool._last_screenshot is not None:
            if current_time - AutomationTool._last_screenshot_time < AutomationTool._screenshot_cache_duration:
                logging.info("使用缓存的 OCR 结果")
                return AutomationTool._last_ocr_result

        # 截取屏幕
        image = AutomationTool.capture_screenshot()
        # 计算截图的哈希值
        image_hash = AutomationTool._calculate_image_hash(image)

        # 如果截图内容未变化，直接返回缓存的 OCR 结果
        if AutomationTool._last_screenshot_hash == image_hash:
            logging.info("截图内容未变化，使用缓存的 OCR 结果")
            AutomationTool._last_screenshot_time = current_time
            return AutomationTool._last_ocr_result

        # 更新缓存
        AutomationTool._last_screenshot = image
        AutomationTool._last_screenshot_hash = image_hash
        AutomationTool._last_screenshot_time = current_time

        # 进行 OCR 识别
        image_base64 = AutomationTool.convert_image_to_base64(image)
        ocr_result = AutomationTool.ocr_image(image_base64)

        # 缓存 OCR 结果
        AutomationTool._last_ocr_result = ocr_result

        return ocr_result

    @staticmethod
    def _calculate_image_hash(image):
        """
        计算图像的哈希值
        :param image: PIL 图像
        :return: 哈希值字符串
        """
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()
        return hashlib.md5(image_bytes).hexdigest()

    @staticmethod
    def click_image_sequence(image_paths, delay_between=1, max_wait=10):
        """
        按顺序识别并点击一系列图片。
        :param image_paths: 图片路径列表
        :param delay_between: 每次尝试之间的延迟
        :param max_wait: 等待第二张图片出现的最大时间（秒）
        :return: 如果成功点击所有图片返回True，否则返回False
        """
        for image_path in image_paths:
            start_time = time.time()
            while True:
                if AutomationTool.click_image(image_path):
                    break
                if time.time() - start_time > max_wait:
                    logging.warning(f"未能在规定时间内找到图片: {image_path}")
                    return False
                time.sleep(delay_between)
        logging.info("成功点击所有图片")
        return True

    @staticmethod
    def move_and_swipe_with_hold(image_path, swipe_distance=200, direction='right', duration=0.5, button='left'):
        """
        将鼠标移动到图片的位置，然后向右滑动指定的距离。

        :param image_path: 图片的位置
        :param swipe_distance: 向右滑动的距离（像素）
        :param direction: 滑动的方向，可以是 'right', 'left', 'top', 'bottom'
        :param duration: 移动和滑动的持续时间（秒）,
        :param button: 按住的鼠标按钮，可以是 'left', 'right', 'middle'
        """
        # 移动到目标位置
        position = AutomationTool.find_image_in_screenshot(image_path, 0.7)
        if position is None:
            logging.error(f"未找到图片：{image_path}")
            return False
        x, y = position

        # 获取当前鼠标位置
        current_x, current_y = pyautogui.position()
        # 移动鼠标到图片位置
        AutomationTool.move_mouse_smoothly((current_x, current_y), (x, y), duration=0.3)

        # 等待一段时间，确保鼠标已经移动到目标位置
        time.sleep(AutomationTool.human_like_delay())

        # 按下鼠标按钮
        pyautogui.mouseDown(button=button)

        # 根据方向参数计算目标位置
        if direction == 'right':
            target_x = x + swipe_distance
            target_y = y
        elif direction == 'left':
            target_x = x - swipe_distance
            target_y = y
        elif direction == 'top':
            target_x = x
            target_y = y - swipe_distance
        elif direction == 'bottom':
            target_x = x
            target_y = y + swipe_distance
        else:
            raise ValueError("Invalid direction. Use 'right', 'left', 'top', or 'bottom'.")

        # 按住鼠标并滑动到目标位置
        AutomationTool.move_mouse_smoothly((x, y), (target_x, target_y), duration=duration, hold_button=button)
        # 等待随机时间
        time.sleep(AutomationTool.human_like_delay())

        logging.info(f"从位置 ({x}, {y}) 滑动到 ({target_x}, {target_y})，方向：{direction}")
        return True

    @staticmethod
    def press_enter():
        """
        按下回车键
        """
        pyautogui.press('enter')

    @staticmethod
    def press_esc():
        """
        按下esc键
        """
        pyautogui.press('esc')

    @staticmethod
    def human_like_delay(min_delay=0.1, max_delay=0.3):
        """
        返回一个介于 min_delay 和 max_delay 之间的随机等待时间
        """
        return random.uniform(min_delay, max_delay)

    @staticmethod
    def human_like_offset(offset_range=2):
        """
        返回一个在 -offset_range 到 offset_range 之间的随机偏移
        """
        return random.randint(-offset_range, offset_range)

    @staticmethod
    def move_mouse_smoothly(start_pos, end_pos, duration=0.5, hold_button=None):
        """
        模拟人类的鼠标移动，使用 pyautogui 的 tween 函数
        :param start_pos: 起始位置 (x, y)
        :param end_pos: 结束位置 (x, y)
        :param duration: 总持续时间（秒）
        :param hold_button: 如果需要在移动过程中按住鼠标按钮，可以指定 'left', 'right', 'middle'
        """
        # 添加随机偏移到结束位置
        offset_x = AutomationTool.human_like_offset()
        offset_y = AutomationTool.human_like_offset()
        end_pos = (end_pos[0] + offset_x, end_pos[1] + offset_y)

        # 随机选择一个缓动函数
        tween_funcs = [
            pyautogui.easeInQuad,
            pyautogui.easeOutQuad,
            pyautogui.easeInOutQuad,
            pyautogui.easeInBounce,
            pyautogui.easeOutBounce,
            pyautogui.easeInElastic,
            pyautogui.easeOutElastic
        ]
        tween_func = random.choice(tween_funcs)

        # 按下鼠标按钮（如果需要）
        if hold_button:
            pyautogui.mouseDown(button=hold_button)

        # 使用 pyautogui 的 moveTo 函数，指定持续时间和缓动函数
        pyautogui.moveTo(end_pos[0], end_pos[1], duration=duration, tween=tween_func)

        # 释放鼠标按钮（如果需要）
        if hold_button:
            pyautogui.mouseUp(button=hold_button)

    def custom_tween(x):
        """
        自定义缓动函数，可以调整 x 的幂次来控制速度曲线
        """
        return x ** 2  # 或者其他数学函数

    @staticmethod
    def _bezier_curve(points, n=50):
        """
        生成贝塞尔曲线的点集
        :param points: 控制点列表
        :param n: 点的数量
        :return: 点的列表
        """
        result = []
        for i in range(n + 1):
            t = i / n
            x = 0
            y = 0
            n_points = len(points)
            for j, (px, py) in enumerate(points):
                bernstein = AutomationTool._bernstein_poly(j, n_points - 1, t)
                x += px * bernstein
                y += py * bernstein
            result.append((x, y))
        return result

    @staticmethod
    def _bernstein_poly(i, n, t):
        """
        计算伯恩斯坦多项式值
        """
        return math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))

```
