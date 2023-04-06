import re
import random
import pandas as pd

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException

import time

# pandas读取数据
my_excel = pd.read_excel("./data.xls")
company_names = my_excel.iloc[:, 2]

# TODO 从第n条数据开始爬
# selenium爬取数据
n = 0

options = webdriver.EdgeOptions()
options.add_argument('--headless')
options.add_argument('--disable-animations')
# TODO 添加浏览器引擎，例如：C:\\Users\\Administrator\\Documents\\PythonWorkSpace\\Test\\msedgedriver.exe
s = Service(r"")

driver = webdriver.Edge(options=options, service=s)

driver.get("https://www.syntaogf.com/")
#隐性等待3秒，打不开页面才报错
driver.implicitly_wait(3)

wait = WebDriverWait(driver, 10)
driver.execute_script("window.scrollBy(0,700)")
# 所有数据
test_company = company_names
# 第一次的位置
with open("res_2.txt", "a") as f:
    ele = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_form_1"]/form/input[1]')))
    ele.send_keys(test_company[n])
    btn = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_form_1"]/form/input[2]'))).click()
    # 等待标签
    try:
        label = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_html"]/div/div[1]/a'))).click()
    except ElementNotInteractableException:
        wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="no_search_html"]/div/div[2]/a'))).click()
        time.sleep(2)
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_form_1"]/form/i'))).click()
        ele = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_form_1"]/form/input[1]')))
        ele.send_keys("航锦科技股份有限公司")
        btn = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="search_form_1"]/form/input[2]'))).click()
        ele = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="search_form_2"]/form/input[1]'))).clear()
        time.sleep(2)
    # list = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_html"]/div/div[1]/div[5]')))
    list = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="search_html"]/div/div[1]/div[5]/div')))
    reg = r'^\d{4}|[A-Z][+-]?$'
    temp_str = test_company[n] + " "
    for item in list:
        match_res = re.findall(reg, item.text)
        temp_str = temp_str + ":".join(match_res) + " "
    temp_str += "\n"
    f.write(temp_str)
    time.sleep(2)
    print(test_company[n] + "完成")

    for com in test_company[n+1:]:
        temp_str = com + " "
        ele = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_form_2"]/form/input[1]')))
        time.sleep(random.randint(1, 2))
        ele.send_keys(com)
        time.sleep(random.randint(1, 2))
        btn = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_form_2"]/form/input[2]'))).click()
        time.sleep(random.randint(1, 2))

        # 等待标签
        # label = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_html"]/div/div[1]/a'))).click()
        # time.sleep(1)
        # list = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_html"]/div/div[1]/div[5]')))
        list = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="search_html"]/div/div[1]/div[5]/div')))
        for item in list:
            match_res: list = re.findall(reg, item.text)
            temp_str = temp_str + ":".join(match_res) + " "
        temp_str += "\n"
        f.write(temp_str)
        # 如果不存在这个公司
        try:
            ele = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="search_form_2"]/form/input[1]'))).clear()
        except ElementNotInteractableException:
            wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="no_search_html"]/div/div[2]/a'))).click()
            time.sleep(2)
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_form_1"]/form/i'))).click()
            ele = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="search_form_1"]/form/input[1]')))
            ele.send_keys("航锦科技股份有限公司")
            btn = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="search_form_1"]/form/input[2]'))).click()
            ele = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="search_form_2"]/form/input[1]'))).clear()
            time.sleep(2)
            print(com + "完成")
            continue
        time.sleep(random.randint(1, 2))
        print(com + "完成")