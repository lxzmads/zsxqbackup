# ZSXQ-BackUp
![](https://img.shields.io/packagist/l/doctrine/orm.svg) ![](https://img.shields.io/badge/python-3.6-ff69b4.svg)

知识星球备份，星球/话题/评论/图片/文件。

api version v2

## Usage
1. 安装 `chromedriver`
> 仅用于自动登录，如果你愿意自己抓包，则不需要安装
  * `brew install chromedriver`
  * 或前往[官网](http://www.seleniumhq.org/download/)/[镜像](http://npm.taobao.org/mirrors/chromedriver/)下载
    * 将包含可执行文件的目录添加至环境变量
    * 或设置`settings.py/CHROME_DRIVER_PATH`为完整执行路径
2. 安装 `ZSXQ-BackUp`
```bash
git clone git@github.com:lxzmads/zsxqbackup.git
cd zsxqbackup
mv zsxq/settings.exammple.py zsxq/settings.py
pyenv shell python3.6.9
pip install -r requirements.txt
```

3. 运行
  * `scrapy crawl backup`
  * 手动指定`token`及`User-Agent`
    * 浏览器端登录后抓包获取`cookies`中的`zsxq_access_token`和`User-Agent`字段
    * 在`zsxq/settings.py`末尾将其设置为`ZSXQ_ACCESS_TOKEN`和`ZSXQ_USER_AGENT`

## Reference
- https://github.com/lxzmads/XMQ-BackUp