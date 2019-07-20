import requests
import re
import time
from selenium import webdriver
import Init


header = {
    'Host': 'h5.qzone.qq.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
    'Accept': '*/*',
    'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://user.qzone.qq.com/790178228?_t_=0.22746974226377736',
    'Connection':'keep-alive'

}
                   
#---------------------------这个是为了获取所有好友的名称和QQ号的简单爬取，和爬取空间说说结合使用
def SaveKey(g_tk,g_qzonetoken,cookie):
    file=open("./Data/Key/Key.txt","w",encoding="utf-8")
    file.write(str(g_tk))
    file.write('\n')
    file.write(str(g_qzonetoken))
    file.write('\n')
    file.write(str(cookie))
    file.write('\n')
    file.close()

def GetGtk(cookie):
    hashes=5381
    for letter in cookie['p_skey']:
        hashes+=(hashes<<5)+ord(letter)
    return hashes&0x7fffffff

def Spyder_FriendsInfo():
    webdriver_path=Init.get_webdriver_path()
    qqzone_url=Init.get_qqzone_url()
    username=Init.get_username()
    password=Init.get_password()
    browser=webdriver.Chrome(executable_path=webdriver_path)  # 注意改你安装插件的路径
    browser.get(qqzone_url)

    browser.switch_to.frame('login_frame')
    browser.find_element_by_id("switcher_plogin").click()
    browser.find_element_by_id("u").send_keys(username)
    browser.find_element_by_id("p").send_keys(password)
    browser.find_element_by_id('login_button').click() 

    time.sleep(5)

    cookie_items=browser.get_cookies()
    cookie={}  
    for item in cookie_items:
        cookie[item['name']]=item['value']
    g_tk = GetGtk(cookie)
    html=browser.page_source
    g_qzonetoken = re.search(r'window\.g_qzonetoken = \(function\(\)\{ try\{return (.*?);\} catch\(e\)',html)
    browser.quit()
    SaveKey(g_tk,g_qzonetoken,cookie)
     
    url= 'https://h5.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/tfriend/friend_ship_manager.cgi?uin={}&do=1&rd=0.11376390567557748&fupdate=1&clean=0&g_tk={}'
    url=url.format(username,g_tk)
    req=requests.get(url,headers=header,cookies=cookie)
    url_name='./Data/好友信息/friendsinfo_json.txt'
    with open(url_name,'wb') as file:
        file.write(req.content)
        file.flush()
        file.close()         
        
#if __name__ == "__main__":        
#    Init.__init__()
#    Spyder_FriendsInfo()