import requests
import re
import time
import json
import os
from utils import Init
from utils import GetFriendsInfo
from selenium import webdriver

header = {
    'Host': 'h5.qzone.qq.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Accept': '*/*',
    'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://user.qzone.qq.com/790178228?_t_=0.22746974226377736',
    'Connection':'keep-alive'

}
                                            

#计算当前时间与文件修改时间的差值，如果超过27分钟则要重新修改，return True
def TimeDifference():
    statinfo=os.stat("./Data//Key/Key.txt")
    if time.time()-statinfo.st_mtime>1650:  #大概是27分钟左右
        return True
    else :
        return False

def SaveKey(g_tk,g_qzonetoken,cookie):
    file=open("./Data/Key/Key.txt","w",encoding="utf-8")
    file.write(str(g_tk))
    file.write('\n')
    file.write(str(g_qzonetoken))
    file.write('\n')
    file.write(str(cookie))
    file.write('\n')
    file.close()
    
def GetKey():
    list=[]
    if os.path.getsize("./Data/Key/Key.txt")!=0:
        with open("./Data/Key/Key.txt","r") as file:
            for line in file:
                list.append(line)
        g_tk=int(list[0])      #注意gtk是int类型不是str的
        g_qzonetoken=list[1]
        cookie=eval(list[2])   #eval转为字典
        return g_tk,g_qzonetoken,cookie
    return 0,0,0

# 获得gtk
def GetGtk(cookie):
    hashes=5381
    for letter in cookie['p_skey']:
        hashes+=(hashes<<5)+ord(letter)
    return hashes&0x7fffffff


def QQzone_Login():
    webdriver_path=Init.get_webdriver_path()
    browser=webdriver.Chrome(executable_path=webdriver_path)  # 注意改你安装插件的路径
    browser.get(Init.get_qqzone_url())

    #<iframe id="login_frame" name="login_frame" height="100%" scrolling="no" width="100%"...</iframe>
    #要首先定位到这个frame才能找到里面的id=switcher_plogin的元素
    #find_element_by_name,find_element_by_id,find_element_by_xpath,find_element_by_class_name,find_element_by_css_selector,
    browser.switch_to.frame('login_frame')
    browser.find_element_by_id("switcher_plogin").click()
    browser.find_element_by_id("u").send_keys(Init.get_username())
    browser.find_element_by_id("p").send_keys(Init.get_password())
    browser.find_element_by_id('login_button').click() 

    time.sleep(5)

    #组装cookie字符串,http://www.9191boke.com/649094288.html这个是登陆雅虎邮箱的也是用'name'和'value’来组装的cookie
    cookie_items=browser.get_cookies()
    cookie={}  
    for item in cookie_items:
        cookie[item['name']]=item['value']
    html=browser.page_source
    g_qzonetoken = re.search(r'window\.g_qzonetoken = \(function\(\)\{ try\{return (.*?);\} catch\(e\)',html)
    g_tk = GetGtk(cookie)
    browser.quit()
    
    print("获取gtk值和g_qzonetoken值成功")
    print("gtk值:"+str(g_tk))
    print("g_qzonetoken值:")
    print(g_qzonetoken)
    print("cookie值: "+str(cookie))
    
    #将当前的关键值保存到文本
    SaveKey(g_tk,g_qzonetoken,cookie)
    return g_tk,g_qzonetoken,cookie

def QQzone_Spyder():
    #现在我明白为什么要求gtk和qzonetoken了，仍然是动态加载，在XHR中的emotion_cgi_...那个文件才是要请求的真正url，
    #那个对应的Response是一个JSON文件，里面的每一个'content'就是第一页每条说说的主体内容，当然其他所有信息包括评论等也在里面
    friends_info=GetFriendsInfo.GetAllFriends_Uin()         #获取好友关键信息
    username=Init.get_username()                            #自己的账号
    #-----------这段逻辑是先从文本中读取已保存的关键值，如果有效就不必重新用selenium获取，否则才更新关键值
    Session=requests.session()
    g_tk,g_qzonetoken,cookie=GetKey()
    test_param={
                'uin': username,
                #'uin':'3616855204',  #此账号空间说说数量为0仍可以正常继续
                #'uin':'3203688190',  #此账号空间设置了权限则下载数量为0
                'ftype':'0',
                'sort':'0',
                'pos':0,
                'num':'20',
                'replynum':'100',
                'g_tk':g_tk,
                'callback': '_preloadCallback',
                'code_version': '1',
                'format': 'jsonp',
                'need_private_comment': '1',
                'qzonetoken': g_qzonetoken
            }
    respond=Session.get("https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6",params=test_param,headers=header,cookies=cookie)
    if TimeDifference()==True or g_tk==0 or respond.status_code!=200:
        print("请求非法!")
        respond.close()
        g_tk,g_qzonetoken,cookie=QQzone_Login()  #重新获取关键值
    else:
        print("保存的关键值仍有效")
        respond.close()
    
    
    friend_count=0
    total=len(friends_info)
    for index,row in friends_info.iterrows():     
        
        friend_count=friend_count+1   #当前已下载的好友数
        if friend_count!=4 :
            continue
        content_num=0                 #记录当前好友已下载的说说数量
        content_list=[]               #存储每一条说说的内容
        
        for i in range(1000):  #按页码循环
            pos=i*20
            param={
                'uin':str(row["uin"]),
                'ftype':'0',
                'sort':'0',
                'pos':pos,
                'num':'20',
                'replynum':'100',
                'g_tk':g_tk,
                'callback': '_preloadCallback',
                'code_version': '1',
                'format': 'jsonp',
                'need_private_comment': '1',
                'qzonetoken': g_qzonetoken
            }
            #注意这个url就是XHR里面那个，params是？后面的一堆键值对，这两者构成了一个完整的请求的url网址
            respond=Session.get("https://h5.qzone.qq.com/proxy/domain/taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6",params=param,headers=header,cookies=cookie)
    
            #需要去掉前面这个英文单词才符合正确的JSON转换格式
            res=re.sub("_preloadCallback", "", respond.text)
            test = res[1:-2]
            Data = json.loads(test)   #转为字典格式的Data
    
            if not re.search('lbs', test):
                print(index+"的"+str(content_num)+'条说说下载完成')
                print("已下载了"+str(friend_count)+"个朋友的说说，当前进度为: %"+str(friend_count/total*100))
                break
   
            for each_data in Data["msglist"]:
                content=each_data["content"]
                print(content)
                content_list.append(content)
                content_num=content_num+1
        
        #将好友的说说保存到Data文件下
        print("将"+index+"的说说保存到本地中....")
        save_path="./Data/好友说说/"+index+".txt"
        #在window平台，文件的默认编码是gbk， 此时如果写入的字符串的编码是utf-8
        #就会引发这种错误，打开文件的编码必须与字符串的编码一致
        file=open(save_path,'w',encoding='utf-8')
        for content in content_list:
            file.write(content)
            file.write('\n')
        file.close()
        print("保存完毕，准备进行下一个好友的说说下载")
        

if __name__ == "__main__":
    Init.__init__()
    QQzone_Spyder()

    
    
    
    
    