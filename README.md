# ShitBot_v3

## 介绍

这是一个基于nonebot2和gocqhttp的简单QQ机器人，主要用于记录每个群的成员的恶臭浓度（即触发关键词频率）  
所有的记录会由插件shitcount记录并存储在本地mysql数据库的表中，表名为shitcount\_[群号]  
如果表在数据库中不存在，则事件处理器会自动创建表  
但注意：如果数据库不存在，事件处理器**不会**自动创建库，所以请自行在本地创建mysql数据库  
每个月28号22:00，updateandsaveshitcount插件会自动将当前数据库中所有表导出为csv文件存放在本地，并清空所有表  

## 如何使用

将./plugins文件夹下所需的插件放入你的项目插件文件夹下，并参照注意事项修改部分内容即可

## 注意事项

1. 每个插件文件夹下需要手动添加 data_source.py ，并在其中自行添加 __init__.py 所需的数据。具体需要数据参见 __init__.py
2. 如果需要用到shitcount插件，请确保本地mysql数据库存在
3. 如果需要使用updateandsaveshitcount插件，请确保同时添加了shitcount插件

**可能会需要自行添加或修改的数据**：botID、数据库连接信息、.env中的配置信息...

This is a QQ bot based on nonebot2 and gocqhttp
Main for keyword counting, with some other functions

I created it for fun
