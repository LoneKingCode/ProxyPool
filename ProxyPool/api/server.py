from flask import Flask,render_template,request,url_for,redirect
from db.sqlhelper import ProxyProtocol, ProxyType
from db.datastore  import sqlhelper
import os
import json
import config
from datetime  import datetime
app = Flask(__name__)

class DataTableModel:
    def __init__(self,draw,recordsTotal,recordsFiltered,data):
        self.draw = draw
        self.recordsTotal = recordsTotal
        self.recordsFiltered = recordsFiltered
        self.data = data
    def tojson(self):
        return {
            'draw':self.draw,
            'recordsTotal':self.recordsTotal,
            'recordsFiltered':self.recordsFiltered,
            'data':self.data,
            }

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
     if request.method == 'POST':
        #f = request.files['proxyfile']
        # f.save(upload_path)
        #格式ip:port
        proxies = request.form.get('proxies')
        models = []
        if proxies:
            proxies = proxies.split('\r\n')
            for p in proxies:
                ip_port = p.split(':')
                ip = ip_port[0]
                port = ip_port[1]
                model = {'ip':ip,'port':port,'speed':0,'score':10,'type':0,'protocol':0,'country':'无','area':'无'}
                models.append(model)
            row_affect = sqlhelper.add(models)
            return json.dumps({'msg':'导入完成，导入{0}条数据'.format(row_affect)})
        else:
            return json.dumps({'msg':'操作失败，内容不存在'})
     return render_template('upload.html')

@app.route('/importdata', methods=['POST'])
def importdata():
        proxies = json.loads(request.data.decode('utf-8'))
        proxies = json.loads(proxies)
        #格式 ip:port
        models = []
        if proxies:
            for p in proxies:
                ip_port = p.split(':')
                ip = ip_port[0]
                port = ip_port[1]
                model = {'ip':ip,'port':port,'speed':0,'score':10,'type':0,'protocol':0,'country':'无','area':'无'}
                models.append(model)
            row_affect = sqlhelper.add(models)
            return json.dumps({'msg':'导入完成，导入{0}条数据'.format(row_affect)})

        else:
            return json.dumps({'msg':'操作失败，内容不存在'})

@app.route('/count', methods=['POST', 'GET'])
def count():
    result = []
    try:
        #/?count=5&condition=speed<3 自定义where条件
        #/?count=5&country=国外 只能输入=的条件
        #/ 获取所有记录
        condition = request.args.get('condition')
        count = request.args.get('count')
        if condition:
             result = sqlhelper.query('select * from Proxy_Main where %s' % condition)
        else:
            result = sqlhelper.get(request.args)
    except:
        return 'error'
    return str(len(result))


@app.route('/get', methods=['POST', 'GET'])
def get():
    result = []
    try:
        #/?count=5&condition=speed<3 自定义where条件
        #/?count=5&country=国外 只能输入=的条件
        #/ 获取所有记录
        condition = request.args.get('condition')
        count = request.args.get('count')
        if condition:
             result = sqlhelper.query('select * from Proxy_Main where %s' % condition,count)
        else:
            result = sqlhelper.get(request.args,count)
    except:
        return 'error'
    json_result = json.dumps(result)
    list_result = '<br/>'.join(["{0}:{1}".format(r['ip'],r['port']) for r in result])
    return list_result

@app.route('/get_pagedata', methods=['POST', 'GET'])
def get_pagedata():
    result = []
    try:
        searchkey = request.values.get('searchKey','')
        orderby = request.values.get('orderBy','id')
        draw = request.values.get('draw','')
        orderdir = request.values.get('orderDir','desc')   #asc or desc
        start = request.values.get('start',0)
        length = request.values.get('length',10)
        sql = 'select {0} from {1} where {2} order by {3} limit {4},{5}'
        result = sqlhelper.query(sql.format('*','Proxy_Main','country like \'%{0}%\' or area like \'%{0}%\''.format(searchkey),orderby + ' ' + orderdir,start,length))
        totalcount = sqlhelper.query('select {0} from {1} where {2}'.format('count(*)','Proxy_Main','country like \'%{0}%\' or area like \'%{0}%\''.format(searchkey)))[0]['count(*)']
    except:
        return 'error'
    count = 0
    for row in result:
        for key,value in row.items():
            if key == 'type':
                result[count][key] = ProxyType(int(value)).name
            elif key == 'protocol':
                result[count][key] = ProxyProtocol(int(value)).name
        count = count + 1
    json_result = json.dumps(DataTableModel(draw,totalcount,totalcount,result).tojson())
    return json_result



@app.route('/delete', methods=['POST', 'GET'])
def delete():
    #/?count=5&country=国外 只能输入=的条件
    params = request.args
    row_affect = json.dumps(sqlhelper.delete(params))
    return json.dumps({'msg':'操作完成，删除{0}条数据'.format(row_affect)})

def start_api_server():
    print('>>>API服务器开启成功,访问地址http://%s:%s' % (config.API_SERVER_IP,config.API_SERVER_PORT))
    app.run(host=config.API_SERVER_IP,
            port = config.API_SERVER_PORT,
            debug=False)



if __name__ == '__main__':
    start_api_server()