from django.test import TestCase

# Create your tests here.

"""
商品和广告,可能是由两个团队分别维护的,所以这里创建两个app应用: contents(广告内容) 和 goods(商品)
APP 创建完成后,首先要注册到 APP_INSTALL, 然后创建模型类之后才能顺利的进行数据库迁移
先有的数据表设计和表间关系, 后面才有 模型类

------------------------------------------------
docker run -dti --network=host --name tracker -v /var/fdfs/tracker:/var/fdfs delron/fastdfs tracker  # 先开启tracker, 再开启 storage

docker run -it --name=myubuntu ubuntu /bin/bash

docker run -dit --name=myubuntu2 ubuntu
docker run -dti --network=host --name storage -e TRACKER_SERVER=192.168.129.167:22122 -v /var/fdfs/storage:/var/fdfs delron/fastdfs storage

docker container ls

----------------------------------------

python manage.py shell 的使用：
　- 是 Django用来交互的.  会用解释器来操作, 这个时候的 入口 就是'manage.py' ; 所以 导包 以入口 manage.py的同级目录作为 '基准'

client.upload_by_filename(文件名)
ret = client.upload_by_filename('/Users/delron/Desktop/1.png')

上传成功之后,会有提示信息, 拿到远端的文件名 'group1/M00/00/00/wKiBp1ufSnaAIdM0AAHHjjn2qwE783.jpg' , 然后访问 nginx hots:8888/ 文件名 
********
我们在使用FastDFS部署一个分布式文件系统的时候，通过FastDFS的客户端API来进行文件的上传、下载、删除等操作。同时通过FastDFS的HTTP服务器来提供HTTP服务。
但是FastDFS的HTTP服务较为简单，无法提供负载均衡等高性能的服务，所以FastDFS的开发者——淘宝的架构师余庆同学，为我们提供了Nginx上使用的FastDFS模块（也可以叫FastDFS的Nginx模块）。
其使用非常简单。FastDFS通过Tracker服务器,将文件放在Storage服务器存储,但是同组之间的服务器需要复制文件,有延迟的问题.假设Tracker服务器将文件上传到了192.168.1.80,
文件ID已经返回客户端,这时,后台会将这个文件复制到192.168.1.30,如果复制没有完成,客户端就用这个ID在192.168.1.30取文件,肯定会出现错误。这个fastdfs-nginx-module可以
重定向连接到源服务器取文件,避免客户端由于复制延迟的问题,出现错误。
********

字段 指定为 ImageField , Django会操作 默认的文件存储系统(在admin中)  问题:存储在本地服务器中，影响性能　　＝＞　 指导　Django 传递给 fastDFS的 Storage中

django 会在 _save() 方法 调用结束后,将其结果name(半个url)返回 并保存到数据库;  
exists()方法如果返回 False ,那么一定会调用 _save()方法
url()方法的返回值作用:　Ｄｊａｎｇｏ保存到数据库的是半个url, 而我们调用 字段 image.url的时候就是调用的 url()方法取得其返回值.

*********
写模型类中的字段并不是难点和重点,在工作中更重要的是 分析数据库表和表之间的关系, 而这个又是结合着 实际产品需求和原型来的.
1.库表结构
2.表间关联
3.字段
4.优化(冗余)

图片问题保存问题 => 解决: 从工程的角度去思考,如何实现 使用(运营人员在admin操作商品上架的时候上传图片)
保存在数据库:＝＞ 在本地只能保存 url 节约空间,即将name和content分开, 将contents保存到 成熟的解决方案中FastDFS, 而它是由C语言写成的,
python调用的时候,只需要调用一个函数 upload_by_filename() |  upload_by_buffer() 即可以,  tracker 和 Storage 的通信则封装在内部.

这样我们即可以 使用 Django的admin站点中 封装的(ImageField字段)对应的上传图片功能--Django文件存储系统, 方便操作, 同时把部分url保存到本地数据库,又可以把内容保存到 Storage中,

---------------------------------------
admin站点管理

sku 没有 delete 方法,没懂?

这附近有点难


python 脚本
1. 添加路径(和之前的启动路径不同)
2. 配置Django环境
3. Django初始化
4. 导包
5. 加声明( which Python)  # 注意这里要用虚拟环境的解释器
6. 添加脚本权限

学会:python脚本的 写 配置 调用 

生成的界面图片,说明图片链接缺少: 考虑后台 tracker 和 Storage 停机. 通过 docker container ls 发现没有开启;
然后使用: 
docker container start tracker  
docker container start storage

-------------------------------
浏览记录  
- 业务逻辑:访问详情页添加到浏览记录, 登录个人中心才可以查看, 限制查看总条数
- 需求: 1.有序; 2.不重复
- 使用技术：　redis的list  也可以 zset(时间戳来区分先后)
    - 浏览记录相对添加频率频繁(每访问一个商品详情页就去操作一次),不适合 mysql 来保存
    - 在redis 中保存 sku_id 即可, 当要通过 点击进入 详情页的时候,才去查和跳转
    - redis 中: string(其实是字节型,是一切的基础) hash(类似dict, 但是key和value都必须是str) list(多个字符串的序列,无序,可重复) set(不重复) zset(有序,不重复)
- 两个接口:ＰＯＳＴ　和　ＧＥＴ
    - 难题:sku_id 不能用常规的 ModelSerializer的方法,因为字段 id 默认是后端自生成,不能接收相当于'read_only'
    - 解决:直接继承 Serializer






"""
