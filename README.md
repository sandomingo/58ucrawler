#58同城用户抓取
author: SanDomingo 

email: whyzxm@gmail.com

##项目包含两个程序：
1. 在搜索页面的用户id抓取
2. 在用户页面的用户信息抓取

##抓取思路：
1. 在搜索页面抓取用户id（按城市），并通过翻页持续抓取，将抓到的id写入数据库
2. 使用用户id ＋ baseurl拼成用户的个人页面url，抓取其中内容，写入数据库

##程序环境依赖：
* python2.6+
* sqlite

##程序包依赖：
* import lxml  
* sqlite3 


##程序启动过程：
程序入口为app.py，还有一个city.txt的资源文件.

1. 创建数据库：

    `$ python app.py setup`
2. 启动uid爬虫，需要多少个线程根据网络调试, 可以使用nohup命令后台运行程序

    `$ python app.py crawluid  # 一个线程`
    
    `$ python app.py crawluid 3  # 三个线程`
3. 启动page爬虫，需要多少个线程请根据网络调试，可以使用nohup命令后台运行程序

    `$ python app.py crawlpage  # 一个线程`
    
    `$ python app.py crawlpage 3  # 三个线程`
4. 完成数据抓取，可以从数据库导出数据

    * 方法一：
    
        找到tc_skill.db文件所在目录，打开终端，以此执行以下几条命令
        
        `$ sqlite3 tc_skill.db # 进入数据库管理程序`
        
        `$ .output result.csv # 将管理程序的输出重定向到文件（默认是标准输出stdout）`
        
        `$ select * from t_tc_user; # 查询表中所有数据（上一步已经重定向输出，查询的结果被输出到文件）`
        
    * 方法二：
    
        继续使用app.py
        
        `$ python app.py export result.csv`
