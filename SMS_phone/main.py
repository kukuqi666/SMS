import time
import random
from collections import Counter
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import TimeoutException

# 设置 Firefox 浏览器选项
def get_firefox_options():
    options = Options()
    options.binary_location = r'D:\Mozilla Firefox\firefox.exe'
    options.headless = False  # 设置为 True 则为无头模式
    try:
        options.set_preference('general.useragent.override', UserAgent().random)  # 随机 UserAgent
    except Exception:
        options.set_preference('general.useragent.override', "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")  # 默认
    return options

BAIDU_URL = 'https://www.baidu.com/'
TEL_NUMBER = '17865536290'  # 手机号码
TEL_NAME = ''  # 名字(可选)
ENABLE_OTP = False  # 如果为True ,且页面元素存在‘去官网按钮’则进入官网发送验证码

titles = ["医生", "护士", "主任", "医师", "院长", "专家", "同志", "大夫"]
relatives = ["我的儿子", "我的孙子", "我的女儿", "我的外甥", "我的弟弟", "我的妹妹"]
situations = ["有一些毛病", "需要帮助", "需要紧急处理","麻烦您了"]
contact_methods = ["请尽快联系我 {number}", "情况紧急，请求帮助，请拨打 {number}"]
greetings = ["您好", "你好", "hello"]

def process_tab(url, success_counter, total_len):
    driver = None
    try:
        # 为每个线程单独创建 WebDriver 实例
        service = Service(r'C:\Users\Administrator\Desktop\scripts\sms\geckodriver.exe')
        driver = webdriver.Firefox(service=service, options=get_firefox_options())
        driver.get(url)
        
        # 等待页面元素加载
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.imlp-component-typebox-input')))
        component_input = driver.find_element(By.CSS_SELECTOR, '.imlp-component-typebox-input')

        if component_input:
            title = random.choice(titles)
            relative = random.choice(relatives)
            situation = random.choice(situations)
            contact_method_template = random.choice(contact_methods)
            contact_method = contact_method_template.replace("{number}", TEL_NUMBER)
            greeting = random.choice(greetings)

            template = f"{greeting}{title}，{relative} {TEL_NAME} {situation}，{contact_method}。"
            print(template)
            component_input.send_keys(template)

            # 点击发送按钮
            send_button = driver.find_element(By.CSS_SELECTOR, '.imlp-component-typebox-send-btn')
            send_button.click()

            # 等待页面反馈，确保消息发送
            time.sleep(5)  # 发送后等待 5 秒，确保操作完成

    except TimeoutException:
        print(f"Timeout while processing {url}")
    except Exception as e:
        print(f"An error occurred: {e}, url: {url}")
    finally:
        if driver:
            driver.quit()  # 关闭 WebDriver 实例
        success_counter.update([url])

def iterate_api(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        urls = file.readlines()
        total_len = len(urls)
        random.shuffle(urls)

    success_counter = Counter()
    max_workers = 5  # 最大并行线程数
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 为每个 URL 启动一个线程
        for result in executor.map(lambda url: process_tab(url, success_counter, total_len), urls):
            pass

if __name__ == '__main__':
    if TEL_NUMBER.isdigit():
        start_time = time.time()
        iterate_api('api.txt')
        end_time = time.time()
        print(f"结束！总耗时: {end_time - start_time} seconds")
    else:
        print("请先输入有效的手机号码")
