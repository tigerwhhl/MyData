import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def GetContent(friend_name):
    file=open("./Data/好友说说/"+friend_name+".txt",mode='r',encoding='utf-8')
    text=file.read()
    return text

def stopwordslist(filepath):  
    stopwords = [line.strip() for line in open(filepath, 'r').readlines()]  
    return stopwords

def jiebaText(text):
    mywordlist=[]
    seg_list=jieba.cut(text,cut_all=False,HMM=True)
    liststr="/".join(seg_list)
    stopwords=stopwordslist("./Data/Key/中文停用词表.txt")
    print(stopwords)
    for myword in liststr.split("/"):
        if not myword in stopwords and len(myword.strip())>1:
            mywordlist.append(myword)
    #print(mywordlist)
    return ' '.join(mywordlist)

def CreateWordCloud(friend_name):
    text=GetContent(friend_name)
    mytext=jiebaText(text)
    wordcloud = WordCloud(
        font_path="C:\Windows\Fonts\simhei.ttf",
        height=2500,
        width=4000
        ).generate(mytext)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")