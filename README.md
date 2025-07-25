# 两个小项目，用python的flask开发框架
数据库sql文件上传到谷歌云盘了：https://drive.google.com/drive/folders/1J04PbhxA8uB9eEUlKjmrkmgFAhuNnt2C?usp=drive_link
# 配置环境就安装requirements.txt
两个项目用一个环境就好，数据库配置的话先看下config.py的数据库名称，推荐先创建同名数据库，再运行对应sql文件，云盘中的beijing_house_data.sql不是这两个项目的，不必下载
# 如果安装requirements.txt失败，看下是不是少了pkg-config libmysqlclient-dev
运行
```bash
sudo apt update
sudo apt install pkg-config libmysqlclient-dev
```
# 正常情况配置好数据库和python包后就可以直接到对应项目目录下运行 python app.py
数据库配置很重要，若不连接好数据库是无法正常运行