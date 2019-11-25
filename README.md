# Academic Aggregation open

## 简介

>本项目是基于《基于爬虫及AI开放平台的学术资源聚合系统》的开源项目

>使用 request-html 解析多个学术资源站点的HTML，将各个站点的搜索结果处理后展示给用户，同时具备一定的学术资源管理功能。

>由于目前已经移除百度AI开放平台的技术，使用本地实现的相关算法，故中文名变更为“X学术聚合系统”

## 特性

- Celery支撑的异步爬虫，后台自动爬取相关文献
- 爬虫获取的结果自动存至数据库
- Bootstrap响应式布局，适配常见尺寸的设备
- NLP技术，辅助处理爬虫结果

## 使用的NLP相关技术
- 短文本相似
- 语种识别 (langid.py)
- 分词 (jieba)

## 示例站点
（暂无）

## 截图
<img src="README/1.jpg" width="80%"/>

## TODO
支持更多的平台，将个人的一些想法加入进来

## 免责说明
本项目仅作为爬虫技术交流学习，__切勿非法使用__

## 相关项目

[requests-html](https://github.com/psf/requests-html)

[django](https://github.com/django/django)

[celery](https://github.com/celery/celery)

[django-celery](https://github.com/celery/django-celery)

[langid.py](https://github.com/saffsd/langid.py)

[jieba](https://github.com/fxsjy/jieba)