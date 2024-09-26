# 飞鸽知识库导出

这个需求是帮助我的好朋友导出飞鸽（来自于抖店机器人）的知识库数据，界面相当复杂，每天0点数据变化还会导致 xpath 发生变化，如果下面的脚本失效更改 xpath 即可解决

## 技术栈
- pandas
- selenium

## 大致逻辑介绍

### 文件系统

启动&主要逻辑 -- main.py
Excel操作 -- excel_io.py
实例化对象 -- knowledge.py
关闭Edge，方便selenium -- shutdown_edge.bat
一些工具 -- util.py

### 逻辑

1. 下载驱动 && 找到 Edge 所在的位置

本次使用的是 Edge 浏览器
> https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH

大部分直接安装都会在：
> C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe

2. 首先使用默认用户的数据，尝试过携带 Cookie 会失效

```python
brave_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
options = webdriver.EdgeOptions()
# options.binary_location = brave_path
# 加载已有的用户数据目录
options.add_argument(r"--user-data-dir=C:\Users\Administrator\AppData\Local\Microsoft\Edge\User Data")
options.add_argument(r"--profile-directory=Default")  # 加载默认的用户配置文件

service = webdriver.EdgeService(executable_path=r"C:\Users\Administrator\Desktop\Migration\msedgedriver.exe")

driver = webdriver.Edge(options=options, service=service)
```

3. 打开飞鸽的知识库
```python
driver.get('https://im.jinritemai.com/pc_seller_v2/main/setting/robot/knowledge')
```

4. 一些主要逻辑

- a. 获取主要分类
- b. 点击分类
- c. 找到二级分类
- d. 点击自定义知识
- e. 在二级分类下找到所有数据 -- 找到页码（计算） -- 找到下一页（跳转） -- 点击每页显示100条数据（最大获取）
- f. 在显示100条数据这里考虑如果不存在的一些情况，以及页面为空的情况
- g. 计算分页逻辑，计算的公式：`total_pages = (total_data_count + page_size - 1) // page_size`
- h. 然后就开始分页的每一页循环，最大为分页逻辑计算出来的最大页码
- i. 获取每一个知识点的信息 -> 转换为 Knowledge 实体 -> 保存到 list -> 保存到excel
- j. excel 每进行 20 次数据增量，就备份一次，一是防止数据丢失，二是方便我的好朋友进行观测
- k. 等待完成

## 效果

已经落地实现，由于商业问题所以不公开任何数据

![](./images/ref-3-1.png)

[点击查看代码](https://github.com/zhiyu1998/feige_knowledge_export)
