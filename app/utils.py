from collections import Counter
from konlpy.tag import Kkma,Okt,Komoran,Hannanum
import pandas as pd
import time
import re
import pickle
import keras
import numpy as np
from .models import *
import requests 
from bs4 import BeautifulSoup as bs ;
import re
import pandas as pd
import datetime
komoran = Komoran()
kkma = Kkma()
hannanum = Hannanum()
okt = Okt()
################################################################################################################################################################################################################################
################################################################################################################################################################################################################################
## 1.1 Article 테이블에 크롤링 데이터 저장
def upload_to_article(data):
    data = get_token(data)
    print('data개수',len(data),'개 \n db업데이트 시작.')
    dir_list = '관람 대회 업체 의견수렴 의회 채용 합격자 전문교육 청소년 주민자치'.split()
    data_nouns =data['nouns']
    for c,dir_ in enumerate(dir_list):
        모델 = keras.models.load_model('files/%s라벨링_꼬꼬마.h5'%dir_,compile = False)
        with open('files/new_labelling_file_%s라벨링_꼬꼬마_vocab'%dir_,'rb') as f:
            vocab = pickle.load(f)
        with open('files/new_labelling_file_%s라벨링_꼬꼬마_idf'%dir_,'rb') as f:
            idf = pickle.load(f)
        tf = data_nouns.apply(lambda x:get_tf(str(x),vocab = vocab))
        tf_idf = tf.apply(lambda x:x*idf )
        tf_idf = pd.DataFrame(dict(tf_idf).values())
        pre_list = []
        for i in 모델.predict(tf_idf):
            if i>0.5:
                pre_list.append(1)
            else:
                pre_list.append(0)
        if c == 0:
            데이타 = pd.concat([data, pd.DataFrame({'%s'%dir_:pre_list})],axis = 1)
        else:
            데이타 = pd.concat([데이타, pd.DataFrame({'%s'%dir_:pre_list})],axis = 1)
    for record_num in range(len(데이타)):
        title = 데이타.iloc[record_num,:]['title']
        content = 데이타.iloc[record_num,:]['content']
        date = 데이타.iloc[record_num,:]['date']
        href = 데이타.iloc[record_num,:]['href']
        writer = 데이타.iloc[record_num,:]['writer']
        nouns = [x for x in 데이타.iloc[record_num,:]['nouns'] if len(x)>1]
        관람 = 데이타.iloc[record_num,:]['관람']
        대회 = 데이타.iloc[record_num,:]['대회']
        업체 = 데이타.iloc[record_num,:]['업체']
        의견수렴 = 데이타.iloc[record_num,:]['의견수렴']
        의회 = 데이타.iloc[record_num,:]['의회']
        채용 = 데이타.iloc[record_num,:]['채용']
        합격자 = 데이타.iloc[record_num,:]['합격자']
        전문교육 = 데이타.iloc[record_num,:]['전문교육']
        청소년 = 데이타.iloc[record_num,:]['청소년']
        주민자치 = 데이타.iloc[record_num,:]['주민자치']
        Article(title=title,content=content,date =date,writer=writer, href=href,title_noun = nouns, 채용=채용,합격자=합격자,의회=의회,관람=관람, 대회=대회, 의견수렴=의견수렴, 업체=업체,  전문교육=전문교육,청소년=청소년,주민자치=주민자치).save()
        print(record_num,'번째 데이터 저장')
## 1.2.1 각 공지사항문장에서 해당하는 vocab에 대한 tf를 구해주는 함수
def get_tf(record,vocab, vocab_length=500, tf_log = 10):
    ze = np.zeros((vocab_length,))
    record=re.sub('[^ㄱ-힣]', ' ',record).split()
    for key, value in Counter(record).items():
        if key in vocab:
            ind = vocab.index(key)
            if tf_log == 'e':
                ze[ind]=1+np.log(value)
            elif tf_log=='10':
                ze[ind]=1+np.log10(value)
            else:
                ze[ind]=1+np.log2(value)
    return ze
## 1.2.2 각 공지사항 문장에 대한 워드 토큰(komoran)을 얻는 과정
def get_token(data):
    print('크롤링데이터에 대한 워드토큰 얻는중...')
    data_titles = data['title']
    lis = []
    for i in data_titles:
        lis.append(komoran.nouns(i))
    data = pd.concat([data,pd.DataFrame({'nouns':lis})],axis = 1)
    return data
################################################################################################################################################################################################################################
################################################################################################################################################################################################################################
## 2.1.1 크롤링 데이터의 타이틀에 있는 단어를 역색인 테이블에 적용    
def change_title_key(datas):
    print('title 역색인 테이블 수정중')
    titles = datas['title']
    ix = datas['id']
    vocab = []
    for i in InverseTable.objects.all():
        vocab.append(i.word)
    cc = 1
    for i,title in zip(ix,titles):
        print(cc,'번째 글')
        for key, value in change_key(title).items():
            if key in vocab:
                record = InverseTable.objects.get(word=key)
                record_loc = eval(record.location)
                record_frequency = record.frequency
                record_loc.append([i,value])
                record_frequency+=1
                record.frequency=record_frequency
                record.location=record_loc
                record.save()
            else:
                vocab.append(key)
                InverseTable(word=key,frequency=1, location=[[i,value]]).save()
        cc+=1
## 2.1.2 크롤링 데이터의 컨텐트에 있는 단어를 역색인 테이블에 적용      
def change_content_key(datas):
    print('content 역색인 테이블 수정중')
    contents = datas['content']
    ix = datas['id']
    vocab = []
    for i in ContentInverseTable.objects.all():
        vocab.append(i.word)
    cc = 1
    for i,content in zip(ix,contents):
        print(cc,'번째 글')
        for key, value in change_key(content).items():
            if key in vocab:
                record = ContentInverseTable.objects.get(word=key)
                record_loc = eval(record.location)
                record_frequency = record.frequency
                record_loc.append([i,value])
                record_frequency+=1
                record.frequency = record_frequency 
                record.location=record_loc
                record.save()
            else:
                vocab.append(key)
                ContentInverseTable(word=key,frequency=1, location=[[i,value]]).save()
        cc+=1
## 2.2.1 각 공지사항의 문장을 형태소분석기 앙상블을 통해서 다양하게 단어 토큰화 해주는 함수
def change_key(sentence):
    t= time.time()
    sentence=re.sub('[^ㄱ-힣0-9 ]',' ',str(sentence))
    sentence_okt = [x for x in okt.nouns(sentence) if len(x)>1]
    sentence_komoran = [x for x in komoran.nouns(sentence) if len(x)>1]
    sentence_han = [x for x in hannanum.nouns(sentence) if len(x)>1]
    sentence_okt_gt4 = [x for x in sentence_okt if len(x)>3]
    sentence_komoran_gt4 = [x for x in sentence_komoran if len(x)>3]
    sentence_han_gt4 = [x for x in sentence_han if len(x)>3]
    sentence_okt_gt4_scattered_by_hannanum = []
    sentence_okt_gt4_scattered_by_komoran = []
    for token in  sentence_okt_gt4:
        a=  komoran.nouns(token)
        b=  hannanum.nouns(token)
        if len(a)!=1:
            sentence_okt_gt4_scattered_by_komoran+=[x for x in a if len(x)>1]
        if len(b)!=1:
            sentence_okt_gt4_scattered_by_hannanum+=[x for x in b if len(x)>1]
    sentence_komoran_gt4_scattered_by_hannanum = []
    sentence_komoran_gt4_scattered_by_okt = []
    for token in  sentence_komoran_gt4:
        a=  okt.nouns(token)
        b=  hannanum.nouns(token)
        if len(a)!=1:
            sentence_komoran_gt4_scattered_by_okt+=[x for x in a if len(x)>1]
        if len(b)!=1:
            sentence_komoran_gt4_scattered_by_hannanum+=[x for x in b if len(x)>1]
    sentence_hannanum_gt4_scattered_by_okt = []
    sentence_hannanum_gt4_scattered_by_komoran = []
    for token in  sentence_han_gt4:
        a=  komoran.nouns(token)
        b=  okt.nouns(token)
        if len(a)!=1:
            sentence_hannanum_gt4_scattered_by_komoran+=[x for x in a if len(x)>1]
        if len(b)!=1:
            sentence_hannanum_gt4_scattered_by_okt+=[x for x in b         if len(x)>1]
    sentence_okt_gt4_scattered_by_hannanum_set = set(Counter(sentence_okt_gt4_scattered_by_hannanum).keys()) 
    sentence_okt_gt4_scattered_by_komoran_set = set(Counter(sentence_okt_gt4_scattered_by_komoran).keys())
    hannanum_차집합 = list(sentence_okt_gt4_scattered_by_hannanum_set-sentence_okt_gt4_scattered_by_komoran_set)
    komoran_차집합 = list(sentence_okt_gt4_scattered_by_komoran_set-sentence_okt_gt4_scattered_by_hannanum_set)
    교집합 = list(sentence_okt_gt4_scattered_by_komoran_set&sentence_okt_gt4_scattered_by_hannanum_set)
    okt_dic = {}
    for i in 교집합:
        if Counter(sentence_okt_gt4_scattered_by_hannanum)[i]>Counter(sentence_okt_gt4_scattered_by_komoran)[i]:
            okt_dic[i]=Counter(sentence_okt_gt4_scattered_by_hannanum)[i]
        else:
            okt_dic[i]=Counter(sentence_okt_gt4_scattered_by_komoran)[i]
    for i in hannanum_차집합:
        okt_dic[i] = Counter(sentence_okt_gt4_scattered_by_hannanum)[i]
    for i in komoran_차집합:
        okt_dic[i] = Counter(sentence_okt_gt4_scattered_by_komoran)[i]
    sentence_komoran_gt4_scattered_by_okt_set = set(Counter(sentence_komoran_gt4_scattered_by_okt).keys()) 
    sentence_komoran_gt4_scattered_by_hannanum_set = set(Counter(sentence_komoran_gt4_scattered_by_hannanum).keys())
    okt_차집합 = list(sentence_komoran_gt4_scattered_by_okt_set-sentence_komoran_gt4_scattered_by_hannanum_set)
    hannanum_차집합 = list(sentence_komoran_gt4_scattered_by_hannanum_set-sentence_komoran_gt4_scattered_by_okt_set)
    교집합 = list(sentence_komoran_gt4_scattered_by_hannanum_set&sentence_komoran_gt4_scattered_by_okt_set)
    komoran_dic = {}
    for i in 교집합:
        if Counter(sentence_komoran_gt4_scattered_by_okt)[i]>Counter(sentence_komoran_gt4_scattered_by_hannanum)[i]:
            komoran_dic[i]=Counter(sentence_komoran_gt4_scattered_by_okt)[i]
        else:
            komoran_dic[i]=Counter(sentence_komoran_gt4_scattered_by_hannanum)[i]
    for i in okt_차집합:
        komoran_dic[i] = Counter(sentence_komoran_gt4_scattered_by_okt)[i]
    for i in hannanum_차집합:
        komoran_dic[i] = Counter(sentence_komoran_gt4_scattered_by_hannanum)[i]
    sentence_hannanum_gt4_scattered_by_okt_set = set(Counter(sentence_hannanum_gt4_scattered_by_okt).keys()) 
    sentence_hannanum_gt4_scattered_by_komoran_set = set(Counter(sentence_hannanum_gt4_scattered_by_komoran).keys())
    okt_차집합 = list(sentence_hannanum_gt4_scattered_by_okt_set-sentence_hannanum_gt4_scattered_by_komoran_set)
    komoran_차집합 = list(sentence_hannanum_gt4_scattered_by_komoran_set-sentence_hannanum_gt4_scattered_by_okt_set)
    교집합 = list(sentence_hannanum_gt4_scattered_by_komoran_set&sentence_hannanum_gt4_scattered_by_okt_set)
    han_dic = {}
    for i in 교집합:
        if Counter(sentence_hannanum_gt4_scattered_by_okt)[i]>Counter(sentence_hannanum_gt4_scattered_by_komoran)[i]:
            han_dic[i]=Counter(sentence_hannanum_gt4_scattered_by_okt)[i]
        else:
            han_dic[i]=Counter(sentence_hannanum_gt4_scattered_by_komoran)[i]
    for i in okt_차집합:
        han_dic[i] = Counter(sentence_hannanum_gt4_scattered_by_okt)[i]
    for i in komoran_차집합:
        han_dic[i] = Counter(sentence_hannanum_gt4_scattered_by_komoran)[i]

    for x,y in list(Counter(sentence_okt).items()):
        if len(x)<7:
            if x in okt_dic.keys():
                okt_dic[x]+=y
            else:
                okt_dic[x]=y
    for x,y in list(Counter(sentence_komoran).items()):
        if len(x)<7:
            if x in komoran_dic.keys():
                komoran_dic[x]+=y
            else:
                komoran_dic[x]=y
    for x,y in list(Counter(sentence_han).items()):
        if len(x)<7:
            if x in han_dic.keys():
                han_dic[x]+=y
            else:
                han_dic[x]=y
    final_dic = {}
    for i in list(Counter(list(han_dic.keys()) + list(komoran_dic.keys()) + list(okt_dic.keys())).keys()):
        a=0
        b=0
        c=0
        if i in han_dic.keys():
            a = han_dic[i]
        if i in komoran_dic.keys():
            b = komoran_dic[i]
        if i in okt_dic.keys():
            c = okt_dic[i]
        final_dic[i]=max([a,b,c])
    print('사용자의 검색어를 분석하는데 걸린 시간 : "',round(time.time()-t,3),'" 초.')
    print('사용자의 검색어 분석 결과 : "',final_dic,'"' )
    return final_dic
## 2.2.2 사용자 검색에 대해서 단어 토큰으로 나눠주는 코드
def change_key_search(sentence):
    t= time.time()
    sentence=re.sub('[^ㄱ-힣0-9 ]',' ',str(sentence))
    sentence_okt = [x for x in okt.nouns(sentence) if len(x)>1]
    sentence_komoran = [x for x in komoran.nouns(sentence) if len(x)>1]
    sentence_han = [x for x in hannanum.nouns(sentence) if len(x)>1]
    sentence_okt_gt4 = [x for x in sentence_okt if len(x)>3]
    sentence_komoran_gt4 = [x for x in sentence_komoran if len(x)>3]
    sentence_han_gt4 = [x for x in sentence_han if len(x)>3]
    sentence_okt_gt4_scattered_by_hannanum = []
    sentence_okt_gt4_scattered_by_komoran = []
    for token in  sentence_okt_gt4:
        a=  komoran.nouns(token)
        b=  hannanum.nouns(token)
        if len(a)!=1:
            sentence_okt_gt4_scattered_by_komoran+=[x for x in a if len(x)>1]
        if len(b)!=1:
            sentence_okt_gt4_scattered_by_hannanum+=[x for x in b if len(x)>1]
    sentence_komoran_gt4_scattered_by_hannanum = []
    sentence_komoran_gt4_scattered_by_okt = []
    for token in  sentence_komoran_gt4:
        a=  okt.nouns(token)
        b=  hannanum.nouns(token)
        if len(a)!=1:
            sentence_komoran_gt4_scattered_by_okt+=[x for x in a if len(x)>1]
        if len(b)!=1:
            sentence_komoran_gt4_scattered_by_hannanum+=[x for x in b if len(x)>1]
    sentence_hannanum_gt4_scattered_by_okt = []
    sentence_hannanum_gt4_scattered_by_komoran = []
    for token in  sentence_han_gt4:
        a=  komoran.nouns(token)
        b=  okt.nouns(token)
        if len(a)!=1:
            sentence_hannanum_gt4_scattered_by_komoran+=[x for x in a if len(x)>1]
        if len(b)!=1:
            sentence_hannanum_gt4_scattered_by_okt+=[x for x in b         if len(x)>1]
    sentence_okt_gt4_scattered_by_hannanum_set = set(Counter(sentence_okt_gt4_scattered_by_hannanum).keys()) 
    sentence_okt_gt4_scattered_by_komoran_set = set(Counter(sentence_okt_gt4_scattered_by_komoran).keys())
    hannanum_차집합 = list(sentence_okt_gt4_scattered_by_hannanum_set-sentence_okt_gt4_scattered_by_komoran_set)
    komoran_차집합 = list(sentence_okt_gt4_scattered_by_komoran_set-sentence_okt_gt4_scattered_by_hannanum_set)
    교집합 = list(sentence_okt_gt4_scattered_by_komoran_set&sentence_okt_gt4_scattered_by_hannanum_set)
    okt_dic = {}
    for i in 교집합:
        if Counter(sentence_okt_gt4_scattered_by_hannanum)[i]>Counter(sentence_okt_gt4_scattered_by_komoran)[i]:
            okt_dic[i]=Counter(sentence_okt_gt4_scattered_by_hannanum)[i]
        else:
            okt_dic[i]=Counter(sentence_okt_gt4_scattered_by_komoran)[i]
    for i in hannanum_차집합:
        okt_dic[i] = Counter(sentence_okt_gt4_scattered_by_hannanum)[i]
    for i in komoran_차집합:
        okt_dic[i] = Counter(sentence_okt_gt4_scattered_by_komoran)[i]
    sentence_komoran_gt4_scattered_by_okt_set = set(Counter(sentence_komoran_gt4_scattered_by_okt).keys()) 
    sentence_komoran_gt4_scattered_by_hannanum_set = set(Counter(sentence_komoran_gt4_scattered_by_hannanum).keys())
    okt_차집합 = list(sentence_komoran_gt4_scattered_by_okt_set-sentence_komoran_gt4_scattered_by_hannanum_set)
    hannanum_차집합 = list(sentence_komoran_gt4_scattered_by_hannanum_set-sentence_komoran_gt4_scattered_by_okt_set)
    교집합 = list(sentence_komoran_gt4_scattered_by_hannanum_set&sentence_komoran_gt4_scattered_by_okt_set)
    komoran_dic = {}
    for i in 교집합:
        if Counter(sentence_komoran_gt4_scattered_by_okt)[i]>Counter(sentence_komoran_gt4_scattered_by_hannanum)[i]:
            komoran_dic[i]=Counter(sentence_komoran_gt4_scattered_by_okt)[i]
        else:
            komoran_dic[i]=Counter(sentence_komoran_gt4_scattered_by_hannanum)[i]
    for i in okt_차집합:
        komoran_dic[i] = Counter(sentence_komoran_gt4_scattered_by_okt)[i]
    for i in hannanum_차집합:
        komoran_dic[i] = Counter(sentence_komoran_gt4_scattered_by_hannanum)[i]
    sentence_hannanum_gt4_scattered_by_okt_set = set(Counter(sentence_hannanum_gt4_scattered_by_okt).keys()) 
    sentence_hannanum_gt4_scattered_by_komoran_set = set(Counter(sentence_hannanum_gt4_scattered_by_komoran).keys())
    okt_차집합 = list(sentence_hannanum_gt4_scattered_by_okt_set-sentence_hannanum_gt4_scattered_by_komoran_set)
    komoran_차집합 = list(sentence_hannanum_gt4_scattered_by_komoran_set-sentence_hannanum_gt4_scattered_by_okt_set)
    교집합 = list(sentence_hannanum_gt4_scattered_by_komoran_set&sentence_hannanum_gt4_scattered_by_okt_set)
    han_dic = {}
    for i in 교집합:
        if Counter(sentence_hannanum_gt4_scattered_by_okt)[i]>Counter(sentence_hannanum_gt4_scattered_by_komoran)[i]:
            han_dic[i]=Counter(sentence_hannanum_gt4_scattered_by_okt)[i]
        else:
            han_dic[i]=Counter(sentence_hannanum_gt4_scattered_by_komoran)[i]
    for i in okt_차집합:
        han_dic[i] = Counter(sentence_hannanum_gt4_scattered_by_okt)[i]
    for i in komoran_차집합:
        han_dic[i] = Counter(sentence_hannanum_gt4_scattered_by_komoran)[i]

    for x,y in list(Counter(sentence_okt).items()):
        if len(x)<7:
            if x in okt_dic.keys():
                okt_dic[x]+=y
            else:
                okt_dic[x]=y
    for x,y in list(Counter(sentence_komoran).items()):
        if len(x)<7:
            if x in komoran_dic.keys():
                komoran_dic[x]+=y
            else:
                komoran_dic[x]=y
    for x,y in list(Counter(sentence_han).items()):
        if len(x)<7:
            if x in han_dic.keys():
                han_dic[x]+=y
            else:
                han_dic[x]=y
    final_dic = {}
    for i in list(Counter(list(han_dic.keys()) + list(komoran_dic.keys()) + list(okt_dic.keys())).keys()):
        a=0
        b=0
        c=0
        if i in han_dic.keys():
            a = han_dic[i]
        if i in komoran_dic.keys():
            b = komoran_dic[i]
        if i in okt_dic.keys():
            c = okt_dic[i]
        final_dic[i]=max([a,b,c])
    print('사용자의 검색어를 분석하는데 걸린 시간 : "',round(time.time()-t,3),'" 초.')
    print('사용자의 검색어 분석 결과 : "',final_dic,'"' )
    return final_dic
################################################################################################################################################################################################################################
################################################################################################################################################################################################################################
## 해당 공지사항이 얼마나 지난 글인지 반환해주는 함수
def ch_calender(date, differ='', mode='none',range_=[6,12]):
    if mode == 'none':
        year = date.year
        month = date.month+differ 
        if 24>=month >12:
            month -=12
            year +=1
        if month >24:
            month -=24
            year +=2
        return (year, month)
    else:
        l = []
        st = range_[0]
        fi = range_[1]
        for i in range(st,fi):
            year = date.year
            month = date.month+i
            if 24>=month >12:
                month -=12
                year +=1
            if month >24:
                month -=24
                year +=2
            l.append((year,month))
        return l 
################################################################################################################################################################################################################################
################################################################################################################################################################################################################################
## 크롤링 해주는 함수
def crolling():
    dic= {}
    id_l = []
    title_l=[]
    content_l=[]
    writer_l = []
    date_l = []
    href_l = []
    count = 0
    nows = datetime.datetime.now()
    # set_delta = (nows-datetime.datetime.strptime('2023-01-12','%Y-%m-%d')).days
    set_delta = 0
    t_delta = 0
    n=1
    #읍면동
    while True:
        if t_delta>set_delta:
            break
        print('읍면동 크롤링...')
        res = bs(requests.get('https://www.sejong.go.kr/bbs/R0126/list.do?pageIndex=%s'%n).text,features="lxml")
        tlist = res.select('tbody tr')
        for i in tlist:
            date = i.select('td')[4].text
            t_delta  = (nows-datetime.datetime.strptime(date,'%Y-%m-%d')).days
            if t_delta>set_delta:
                break
            count+=1
            title = i.select_one('td.subject').select_one('a').text
            link = 'https://www.sejong.go.kr'+ i.select_one('td.subject').select_one('a')['href']
            writer = '[읍면동]'+i.select('td')[2].text
            re1 = bs(requests.get(link).text,features="lxml")
            content = re1.select('div.bbs--view--content')[0].text.strip()
            content = re.sub('[^a-zA-Z가-힣0-9 ]','',content)
            id_l.append(count)
            title_l.append(title)
            content_l.append(content)
            writer_l.append(writer)
            date_l.append(date)
            href_l.append(link)
        n+=1
    # 시청
    t_delta = 0
    n=1
    while True:
        if t_delta>set_delta:
            break
        print("시청 크롤링...")
        res = bs(requests.get('https://www.sejong.go.kr/bbs/R0071/list.do?pageIndex=%s'%n).text,features="lxml")
        tlist = res.select('tbody tr')
        for i in tlist:
            date = i.select('td')[4].text
            t_delta  = (nows-datetime.datetime.strptime(date,'%Y-%m-%d')).days
            if t_delta>set_delta:
                break
            count+=1
            title = i.select_one('td.subject').select_one('a').text
            link = 'https://www.sejong.go.kr'+ i.select_one('td.subject').select_one('a')['href']
            writer = '[세종시청]'+i.select('td')[2].text
            re1 = bs(requests.get(link).text,features="lxml")
            content = re1.select('div.bbs--view--content')[0].text.strip()
            content = re.sub('[^a-zA-Z가-힣 ]','',content)
            id_l.append(count)
            title_l.append(title)
            content_l.append(content)
            writer_l.append(writer)
            date_l.append(date)
            href_l.append(link)
        n+=1
    #시의회
    t_delta = 0
    n=1
    while True:
        if t_delta>set_delta:
            break
        print("시의회 크롤링...")
        res = bs(requests.get('https://council.sejong.go.kr/mnu/noc/noticeList.do?pageNo=%s'%n).text,features="lxml")
        tlist = res.select('tbody tr')
        for i in tlist:
            date = i.select('td.b_date')[0].text
            t_delta  = (nows-datetime.datetime.strptime(date,'%Y-%m-%d')).days
            if t_delta>set_delta:
                break
            count+=1
            title = i.select_one('td.b_subject.left').select_one('a').text
            link = 'https://council.sejong.go.kr'+ i.select_one('td.b_subject.left').select_one('a')['href']
            writer = '[세종시의회]'+i.select('td.b_writer')[0].text
            re1 = bs(requests.get(link).text,features="lxml")
            content = re1.select('td.contentview')[0].text.strip()
            content = re.sub('[^a-zA-Z가-힣 ]','',content)
            id_l.append(count)
            title_l.append(title)
            content_l.append(content)
            writer_l.append(writer)
            href_l.append(link)
            date_l.append(date)
        n+=1
    #보건소
    t_delta = 0
    n=1
    while True:
        if t_delta>set_delta:
            break
        print("보건소 크롤링...")
        res = bs(requests.get('https://www.sejong.go.kr/bbs/R2002/list.do?pageIndex=%s'%n).text,features="lxml")
        tlist = res.select('tbody tr')
        for i in tlist:
            date = i.select('td')[4].text
            t_delta  = (nows-datetime.datetime.strptime(date,'%Y-%m-%d')).days
            if t_delta>set_delta:
                break
            count+=1
            title = i.select_one('td.subject').select_one('a').text
            link = 'https://www.sejong.go.kr'+ i.select_one('td.subject').select_one('a')['href']
            writer = '[세종보건소]'+i.select('td')[2].text
            re1 = bs(requests.get(link).text,features="lxml")
            content = re1.select('div.bbs--view--content')[0].text.strip()
            content = re.sub('[^a-zA-Z가-힣 ]','',content)
            id_l.append(count)
            title_l.append(title)
            content_l.append(content)
            writer_l.append(writer)
            href_l.append(link)
            date_l.append(date)
        n+=1
    #농업기술
    t_delta = 0
    n=1
    while True:
        if t_delta>set_delta:
            break
        print('농업기술 크롤링...')
        res = bs(requests.get('https://www.sejong.go.kr/bbs/R3165/list.do?pageIndex=%s'%n).text,features="lxml")
        tlist = res.select('tbody tr')
        for i in tlist:
            date = i.select('td')[4].text
            t_delta  = (nows-datetime.datetime.strptime(date,'%Y-%m-%d')).days
            if t_delta>set_delta:
                break
            count+=1
            title = i.select_one('td.subject').select_one('a').text
            link = 'https://www.sejong.go.kr'+ i.select_one('td.subject').select_one('a')['href']
            writer = '[세종농업기술센터]'+i.select('td')[2].text
            re1 = bs(requests.get(link).text,features="lxml")
            content = re1.select('div.bbs--view--content')[0].text.strip()
            content = re.sub('[^a-zA-Z가-힣 ]','',content)
            id_l.append(count)
            title_l.append(title)
            content_l.append(content)
            writer_l.append(writer)
            href_l.append(link)
            date_l.append(date)
        n+=1
    #시설관리사업소
    t_delta = 0
    n=1
    while True:
        if t_delta>set_delta:
            break
        print('시설관리사업소 크롤링...')
        res = bs(requests.get('https://www.sejong.go.kr/bbs/R3162/list.do?pageIndex=%s'%n).text,features="lxml")
        tlist = res.select('tbody tr')
        for i in tlist:
            date = i.select('td')[4].text
            t_delta  = (nows-datetime.datetime.strptime(date,'%Y-%m-%d')).days
            if t_delta>set_delta:
                break
            count+=1
            title = i.select_one('td.subject').select_one('a').text
            link = 'https://www.sejong.go.kr'+ i.select_one('td.subject').select_one('a')['href']
            writer = '[세종시설관리사업소]'+i.select('td')[2].text
            re1 = bs(requests.get(link).text,features="lxml")
            content = re1.select('div.bbs--view--content')[0].text.strip()
            content = re.sub('[^a-zA-Z가-힣 ]','',content)
            id_l.append(count)
            title_l.append(title)
            content_l.append(content)
            writer_l.append(writer)
            href_l.append(link)
            date_l.append(date)
        n+=1
    #경찰청
    t_delta = 0
    n=1
    while True:
        if t_delta>set_delta:
            break
        try:
            print('경찰청 크롤링...')
            res = bs(requests.get('https://www.sjpolice.go.kr/site/main.php?mxPn=02_01&kf1=sub&bo=notify1&p=%s'%n).text,"html.parser")
            tlist = res.select('tbody.text-align--center tr')
            for i in tlist:
                date = i.select('td.m-table__date')[0].text
                t_delta  = (nows-datetime.datetime.strptime(date,'%Y-%m-%d')).days
                if t_delta>set_delta:
                    break
                count+=1
                title = i.select_one('td.text-align--left.m-table__title').select_one('a').text
                link = 'https://www.sjpolice.go.kr/site/main.php'+ i.select_one('td.text-align--left.m-table__title').select_one('a')['href']
                writer = '[세종 경찰청]'+i.select['td'][3]
                re1 = bs(requests.get(link).text,features="lxml")
                content = re1.select('div#html')[0].text.strip()
                content = re.sub('[^a-zA-Z가-힣 ]','',content)
                id_l.append(count)
                title_l.append(title)
                content_l.append(content)
                writer_l.append(writer)
                href_l.append(link)
                date_l.append(date)
            n+=1
        except:
            break
    #경찰청 채용공고
    t_delta = 0
    n=1
    while True:
        if t_delta>set_delta:
            break
        try:
            res = bs(requests.get('https://www.sjpolice.go.kr/site/main.php?mxPn=02_03_02&kf1=sub&kf2=&kw=&bo=sjpol1&p=%s'%n).text,"html.parser")
            tlist = res.select('tbody.text-align--center tr')
            for i in tlist:
                date = i.select('td.m-table__date')[0].text
                t_delta  = (nows-datetime.datetime.strptime(date,'%Y-%m-%d')).days
                if t_delta>set_delta:
                    break
                count+=1
                title = i.select_one('td.text-align--left.m-table__title').select_one('a').text
                link = 'https://www.sjpolice.go.kr/site/main.php'+ i.select_one('td.text-align--left.m-table__title').select_one('a')['href']
                writer = '[세종 경찰청]'+i.select['td'][3]
                re1 = bs(requests.get(link).text,features="lxml")
                content = re1.select('div#html')[0].text.strip()
                content = re.sub('[^a-zA-Z가-힣 ]','',content)
                id_l.append(count)
                title_l.append(title)
                content_l.append(content)
                writer_l.append(writer)
                href_l.append(link)
                date_l.append(date)
            n+=1
        except:
            break
    #북부경찰서
    t_delta = 0
    n=1
    while True:
        if t_delta>set_delta:
            break
        try:
            print('북부경찰서 크롤링...')
            res = bs(requests.get('https://www.sjpolice.go.kr/SEO/SJ/main.php?mxPn=02_01&kf1=sub&kf2=&kw=&bo=notify1&p=%s'%n).text,"html.parser")
            tlist = res.select('tbody.text-align--center tr')
            for i in tlist:
                date = i.select('td.m-table__date')[0].text
                t_delta  = (nows-datetime.datetime.strptime(date,'%Y-%m-%d')).days
                if t_delta>set_delta:
                    break
                count+=1
                title = i.select_one('td.text-align--left.m-table__title').select_one('a').text
                link = 'https://www.sjpolice.go.kr/site/main.php'+ i.select_one('td.text-align--left.m-table__title').select_one('a')['href']
                writer = '[세종 경찰청]'+i.select['td'][3]
                re1 = bs(requests.get(link).text,features="lxml")
                content = re1.select('div#html')[0].text.strip()
                content = re.sub('[^a-zA-Z가-힣 ]','',content)
                id_l.append(count)
                title_l.append(title)
                content_l.append(content)
                writer_l.append(writer)
                href_l.append(link)
                date_l.append(date)
            n+=1
        except:
            break
    #북부경찰서 채용공고
    t_delta = 0
    n=1
    while True:
        if t_delta>set_delta:
            break
        try:
            res = bs(requests.get('https://www.sjpolice.go.kr/SEO/SJ/main.php?mxPn=02_03_02&p=%s'%n).text,"html.parser")
            tlist = res.select('tbody.text-align--center tr')
            for i in tlist:
                date = i.select('td.m-table__date')[0].text
                t_delta  = (nows-datetime.datetime.strptime(date,'%Y-%m-%d')).days
                if t_delta>set_delta:
                    break
                count+=1
                title = i.select_one('td.text-align--left.m-table__title').select_one('a').text
                link = 'https://www.sjpolice.go.kr/site/main.php'+ i.select_one('td.text-align--left.m-table__title').select_one('a')['href']
                writer = '[세종 경찰청]'+i.select['td'][3]
                re1 = bs(requests.get(link).text,features="lxml")
                content = re1.select('div#html')[0].text.strip()
                content = re.sub('[^a-zA-Z가-힣 ]','',content)
                id_l.append(count)
                title_l.append(title)
                content_l.append(content)
                writer_l.append(writer)
                href_l.append(link)
                date_l.append(date)
            n+=1
        except:
            break
    #남부경찰서
    t_delta = 0
    n=1
    while True:
        if t_delta>set_delta:
            break
        try:
            print('남부경찰서 크롤링...')
            res = bs(requests.get('https://www.sjpolice.go.kr/SEO/NB/main.php?mxPn=02_01&kf1=sub&kf2=&kw=&bo=notify1&p=%s'%n).text,"html.parser")
            tlist = res.select('tbody.text-align--center tr')
            for i in tlist:
                date = i.select('td.m-table__date')[0].text
                t_delta  = (nows-datetime.datetime.strptime(date,'%Y-%m-%d')).days
                if t_delta>set_delta:
                    break
                count+=1
                title = i.select_one('td.text-align--left.m-table__title').select_one('a').text
                link = 'https://www.sjpolice.go.kr/site/main.php'+ i.select_one('td.text-align--left.m-table__title').select_one('a')['href']
                writer = '[세종 경찰청]'+i.select['td'][3]
                re1 = bs(requests.get(link).text,features="lxml")
                content = re1.select('div#html')[0].text.strip()
                content = re.sub('[^a-zA-Z가-힣 ]','',content)
                id_l.append(count)
                title_l.append(title)
                content_l.append(content)
                writer_l.append(writer)
                href_l.append(link)
                date_l.append(date)
            n+=1
        except:
            break
    #남부경찰서 채용공고
    t_delta = 0
    n=1
    while True:
        if t_delta>set_delta:
            break
        try:
            res = bs(requests.get('https://www.sjpolice.go.kr/SEO/NB/main.php?mxPn=02_03_02&p=%s'%n).text,"html.parser")
            tlist = res.select('tbody.text-align--center tr')
            for i in tlist:
                date = i.select('td.m-table__date')[0].text
                t_delta  = (nows-datetime.datetime.strptime(date,'%Y-%m-%d')).days
                if t_delta>set_delta:
                    break
                count+=1
                title = i.select_one('td.text-align--left.m-table__title').select_one('a').text
                link = 'https://www.sjpolice.go.kr/site/main.php'+ i.select_one('td.text-align--left.m-table__title').select_one('a')['href']
                writer = '[세종 경찰청]'+i.select['td'][3]
                re1 = bs(requests.get(link).text,features="lxml")
                content = re1.select('div#html')[0].text.strip()
                content = re.sub('[^a-zA-Z가-힣 ]','',content)
                id_l.append(count)
                title_l.append(title)
                content_l.append(content)
                writer_l.append(writer)
                href_l.append(link)
                date_l.append(date)
            n+=1
        except:
            break
    print('총',count,'개 데이터 수집 완료')
    dic['id']=id_l
    dic['content']=content_l
    dic['title']=title_l
    dic['writer']=writer_l
    dic['date']=date_l
    dic['href']=href_l
    return dic