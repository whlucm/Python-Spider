from bs4 import BeautifulSoup
import re
import requests
import time
import cx_Oracle


#得到网页源代码
def gethtml(url):
      try:
            r = requests.get(url, timeout=10,headers = {'User-Agent': 'Mozilla/5.0','Accept-Language':'zh-CN,zh'})
            return r.text
      except:
            print("网页无法访问")
            return""


#存储图片
def jpgsave(pictureurl,picturename,saveaddress):
      path = str(saveaddress)+str(picturename)
      try:
            jpg = requests.get(pictureurl,timeout=10)
            with open(path,'wb') as f:
                  f.write(jpg.content)#r.content 返回的2进制类型文件
            f.close
      except:
            print("图片获取失败")

#视频信息存入数据库
def saveOracle(movtitle,movurl,picturename,pictureurl,saveaddress,upload,movlong,movcrtime,creattime,cursor):
      cursor.execute ("INSERT INTO VIDEO (movtitle,movurl,picturename,pictureurl,saveaddress,upload,movlong,movcrtime,creattime)VALUES('%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(str(movtitle),str(movurl),str(picturename),str(pictureurl),str(saveaddress),str(upload),str(movlong),str(movcrtime),str(creattime)))
     
#核心解析
def parserhtml(soup,sn,conn,cursor):
      for div in soup.find_all('div',attrs = {'class':'listchannel'}):
            a = div.find('a')
            img =a.find('img')
            divtext = div.get_text() #解析div中的文本内容
            divtext = divtext.replace(' ', '')
             #视频名称
            movtitle = img.get('title')
            #视频地址
            movurl= a.get('href')
            #图片名称
            picturename =str(movtitle)+str(sn)+".jpg"
            #图片存储地址
            saveaddress = "D:/picture/"
            #图片地址
            pictureurl =img.get('src')
            #时长信息
            movlong = re.findall(r"时长:(.+)",divtext,re.M)
            movlong = str(movlong)[2:-2]
            #视频上传时间
            movcrtime= re.findall(r"添加时间:(.+)",divtext,re.M)
            movcrtime = str(movcrtime)[2:-2]
            #上传者
            upload =re.findall(r'作者:\n(.*)\n查看',divtext)
            upload = str(upload)[2:-2]
            #记录创建时间
            creattime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            #存储图片
            jpgsave(pictureurl,picturename,saveaddress)
            #视频信息存入数据库
            saveOracle(movtitle,movurl,picturename,pictureurl,saveaddress,upload,movlong,movcrtime,creattime,cursor)
            print(movtitle)
      conn.commit() #数据库数据提交
            
            

#url自动连接
def urladd(urlbegin,s,n,conn,cursor):
      for i in range(n):
            sn = s+i
            url = str(urlbegin)+str(sn)
            html = gethtml(url)  #每个网页的源代码
            soup = BeautifulSoup(html,"html.parser") #网页解析
            parserhtml(soup,sn,conn,cursor)#核心解析 



#main函数
def main():
      s = 1 #起始页码
      n = 1#遍历页数
      urlbegin='http://url.com'
      conn = cx_Oracle.connect('pythondb/admin@192.168.1.2/odb')#链接数据库
      cursor =conn.cursor() #建立游标
      urladd(urlbegin,s,n,conn,cursor) #网址自动链接→进入核心解析→存储图片及数据
      cursor .close() #关闭游标
      conn.close() #关闭数据库链接

main()


