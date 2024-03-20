# 采集中国企业ESG评级
这个需求是帮助我的好朋友采集中国企业的ESG评级数据，这个数据是从一个网站上采集的，网站的地址是：[http://www.esgchina.org/](http://www.esgchina.org/)。

## 技术栈
- pandas
- selenium

## 逻辑
大致逻辑是打开网页搜索把数据放到Excel中，并且支持断开后下次还能继续采集。

1. 首先你要找到你要采集的Excel有哪些数据
```python
# pandas读取数据
my_excel = pd.read_excel("./data.xls")
company_names = my_excel.iloc[:, 2]
```
2. 断开后继续开始的位置
```python
# TODO 从第n条数据开始爬
# selenium爬取数据
n = 0
```
3. 下载驱动后写一下驱动的位置
- 驱动（要和浏览器版本相同）：https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH
```python
options = webdriver.EdgeOptions()
options.add_argument('--headless')
options.add_argument('--disable-animations')
# TODO 添加浏览器引擎，例如：C:\\Users\\Administrator\\Documents\\PythonWorkSpace\\Test\\msedgedriver.exe
s = Service(r"")
```
4. 开始采集数据

[点击查看代码](2-extra_syntaogf.py)