# ProxyPool
预览网址：http://proxy.lk1.cc/

修改配置config.py后运行start.py即可，目前配置文件中抓取网址，可以保持在2000左右代理数据  

# config.py 配置文件说明
##### 这里只说网址规则，其余查看config.py注释
type支持xpath,regular,custom  regular为正则，custom为自定义方法,在crawler.parser.ParserExtension中定义  
pattern为匹配规则  
position为匹配结果指定数据所在位置  
urls为网址列表
```python
 {
        'name':'云代理',
        'urls':['http://www.ip3366.net/free/?stype=%s&page=%s' % (t,p) for t in range(1,5) for p in range(1,8)],
        'type':'xpath',
        'pattern':'//*[@id="list"]/table/tbody/tr[position()>1]',
        'position':{'ip':'./td[1]','port':'./td[2]','type':'','protocol':'',},
 }
```
# API接口文档
地址 | 参数 | 值  | 作用 | 请求方式
-|-|-|-|-
/get | count | 整数 | 获取的数量 | get/post
/get | condition | sql where条件 | 较危险，例如speed<3   | get/post
/get | 字段名 | 值 | 相当于=条件，可多个 | get/post
/delete | 字段名 | 值 | 相当于=条件，可多个 | get/post
/upload | proxies | 文件 | 导入文件数据 | post
/importdata | data | 代理数据ip:port多个换行 | 导入代理数据 | post

### 字段type  
值 | 含义  
-|-
0 | 高匿
1 | 匿名
2 | 透明

### 字段protocol
值 | 含义  
-|-
0 | http
1 | https
2 | http_https

/get?count=5&condition=speed<3 自定义where条件 获取速度小于3且数量为5  
/get?count=5&country=国外 只能输入=的条件 获取国家为国外且数量为5  
/delete?country=国外&type=1 删除国家为国外且类型为1(匿名)的代理数据  
/upload可在线导入以及上传文件入库  
首页为代理数据列表页  
![image](https://i.loli.net/2019/10/30/bz4qhJrFjHdOPCm.png)
