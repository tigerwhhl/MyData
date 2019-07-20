import json
import os
from pandas import DataFrame
#import FriendsInfoSpyder  #搞不懂为什么不要引用能直接调用

#读取文件中保存的所有好友信息
def GetAllFriends_Info():
    path="./Data/好友信息/friendsinfo_json.txt"
    if os.path.exists(path):
        all_friends=open(path, encoding='UTF-8').read()
    else:
        FriendsInfoSpyder.Spyder_FriendsInfo()
        all_friends=open(path, encoding='UTF-8').read()
     #去掉BOM头， Unexpected UTF-8 BOM (decode using utf-8-sig)
    if all_friends.startswith(u'\ufeff'):
        all_friends =all_friends.encode('utf8')[3:].decode('utf8')
    return all_friends


#转为字典格式，读取每个好友的QQ号构成QQ空间网址，返回pandas二维数组
def GetAllFriends_Uin():
    all_friends=GetAllFriends_Info()
    #all_friends=all_friends[10:-2]   
    #处理为合法的字典转换格式
    all_friends=all_friends.replace("_Callback(","")
    all_friends=all_friends.replace(");","")
    Data=json.loads(all_friends)
    
    qqzone_url_list=[]
    qqfriend_name_list=[]
    qquin_list=[]
    url="https://user.qzone.qq.com/"
    
    for each_friend in Data["data"]["items_list"]:
        qqzone_url=url+str(each_friend["uin"])+"/311"
        qqfriend_name_list.append(each_friend["name"])
        qqzone_url_list.append(qqzone_url)
        qquin_list.append(each_friend["uin"])
    
    data={"url":qqzone_url_list,"uin":qquin_list}
    df=DataFrame(data,index=qqfriend_name_list)
    print(df)
    print("好友信息已收集完毕")
    return df


#GetAllFriends_Uin()