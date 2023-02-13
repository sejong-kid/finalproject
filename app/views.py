from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Article, InverseTable,ContentInverseTable
from konlpy.tag import Okt,Komoran,Hannanum
import pickle
import numpy as np
import pandas as pd
import pickle
import time
import datetime
from .utils import *
with open('data14000_코모란','rb') as f:
    data14000 = pickle.load(f)
with open('14000개꼬꼬마데이타_nouns','rb') as f:
    data14000_train = pickle.load(f)
komoran = Komoran()
hannanum = Hannanum()
okt = Okt()
all_article_length = len(Article.objects.all())
# 인덱스 페이지로 가게하는 함수
def index(request):
    return render(request, 'app/index.html')
def search(request):
    '''
    쿼리파라미터를 받아서 다시 인덱스페이지로 데이터를 넘겨주는 함수
    자바스크립트 fetch API로 정보를 받아와야 표적이 되는 데이터를 사용자에게 보여줄수 있는데, 
    가져올 그 정보에 대한 구체적인 참조사항이 필요하기 때문
    '''
    key = request.GET.get('key') ## 검색어가 있을 시 검색어
    mode = request.GET.get('search_mode') ## 제목 내용
    search_period = request.GET.get('search_period') ## 기간
    category = request.GET.get('category') ##카테고리가 있을 시 카테고리
    ## 카테고리 정보가 존재할 때
    if category !=None:
        return render(request, 'app/index.html',{'key':key,'category':category,'search':'category'})
    ## 검색어가 존재할 때
    else:
        return render(request, 'app/index.html',{'key':key,'search_mode':mode,'search_period':search_period,'search':'search'})
def read_json(request):
    '''
    자바스크립트로 필요한 정보만을 넘겨받기 위해서, 데이터베이스와 통신해야함
    필요한 정보만을 넘겨받으려면 정확히 어떤 정보가 필요한지에 대한 명확한 지시가 필요한데
    이를 
    << 1. 사용자의 검색어 2. 검색 모드(제목 or 내용) 3. 날짜기준 4. 카테고리이름 >> 
    을 통해 구체화 한다.
    1. 사용자의 검색어는 utils.py의 change_search_key()함수를 호출하여 검색어를 여러 방면으로 토큰화해서 이용한다
    2. 검색 모드는 제목 / 내용 두가지 모드가 존재하며, 
       제목은 DataBase의 InverseTable역색인을 참조하고, 내용은 ContentInverseTable을 참조한다
       이 테이블들에서 검색어로 쪼개진 단어를 찾아, 그 단어의 frequency컬럼값으로 idf를 구하고
       location 이중 리스트를 이용해서, 그 단어를 갖고있는 공지사항들의 인덱스와 tf값을 추출해 
       최종적으로 사용자 검색어 토큰을 컬럼으로 하는 tf_idf행렬을 얻는다
       이후에 그 tf_idf행렬을 이용해서 점수를 산출하고
       그 점수를 이용해 정렬을 해서 사용자에게 보여줄수 있도록 한다
    3. 날짜를 직관적으로 나타내주기 위해 정확한 일자형태의 날짜가 아니라, 현재로부터 얼마나 지난 글인지를 파악할수 있게해주는 날짜기준을 사용함
    4. 카테고리이름 ( 어떤 카테고리에 해당하는 글인지를 알아야 가져오니까 )
    --------------------------------------------------------------------------------------------------------
    이모든 과정 
    << 정렬(시간순 정렬, 점수 정렬) 하고, 그것을 필요에 맞게 가공("날짜 가공", "공지사항 중요도 점수 부여" 등)하여 JSON형태로 웹을통해 넘겨주는 과정 >>
    을 망라하는 코드가 필요한데,
    그것들을 구현한 코드가 아래 쓰여져있다.
    '''
    time_ = time.time()
    key = request.GET.get('key')##사용자의 검색어
    print('사용자의 검색어 : ',key)
    category = request.GET.get('category') ## 카테고리 값
    print('카테고리 :' , category)
    today = datetime.datetime.today()
    날짜기준 = '오늘 / 어제 / 이번 주 / 지난 주 / 이번달 / 지난달 / 2달 전 / 3달 전 / 4달 전 / 5달 전 / 6달 전 / 6개월 이상 / 1년 이상'.split(' / ')
    # 1 카테고리가 없을 때 
    if category==None:
        ## 1-1 넘겨받은 검색어가 없을 때 
        ### 전체 조회 ( 최신 순 )
        mode = request.GET.get('mode')##검색모드 [ 제목 / 내용 ]
        search_period = request.GET.get('search_period')
        if key=='':
            cc= 1 
            article_list = []
            for i in Article.objects.all():
                date = i.date
                s_date_ = datetime.datetime.strptime(date, '%Y-%m-%d')
                s_date = (today-s_date_).days
                title = i.title
                writer = i.writer
                href = i.href
                if s_date<=7:
                    search_period_ = '1주이내'
                elif 7<s_date<=31:
                    search_period_ = '1달이내'
                elif 31<s_date<=31*3:
                    search_period_ = '3달이내'
                elif 31*3<s_date<=365 :
                    search_period_ = '1년이내'
                else: 
                    search_period_ = '1년이후'
                ## '오늘 / 어제 / 이번 주 / 지난 주 / 이번달 / 지난달 / 2달 전 / 3달 전 / 4달 전 / 5달 전 / 6개월 이상 / 1년 이상'
                if s_date==0:
                    date_ = 날짜기준[0]
                elif s_date==1:
                    date_=날짜기준[1]
                else:
                    w_d = (today-datetime.timedelta(today.weekday())-s_date_).days
                    if w_d<=0:
                        date_=날짜기준[2]
                    elif 0<w_d<8:
                        date_ = 날짜기준[3]
                    else:
                        if (today-datetime.timedelta(today.day-1)-s_date_).days<=0:
                            date_ = 날짜기준[4]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 1):
                            date_=날짜기준[5]
                        elif s_date<=31*2:
                            date_=날짜기준[6]
                        elif 31*2<s_date<=31*3:
                            date_=날짜기준[7]
                        elif 31*3<s_date<=31*4:
                            date_=날짜기준[8]
                        elif 31*4<s_date<=31*5:
                            date_=날짜기준[9]
                        elif 31*5<s_date<=31*6:
                            date_=날짜기준[10]
                        elif 31*6<s_date<=365:
                            date_=날짜기준[11]
                        else:
                            date_=날짜기준[-1]
                article_dic={'title':title, 'writer':writer, 'href':href, 'updated':date_,'s_date':s_date,'search_period':search_period_}
                article_list.append(article_dic)
                cc+=1
            article_list = sorted(article_list, key=lambda x:x['s_date'])
            xxx = 1
            ar = []
            if search_period == '1주이내':
                for i in article_list:
                    if i['search_period']=='1주이내':
                        i['article_num']=xxx
                        xxx+=1
                        ar.append(i)
            elif search_period =='1달이내':
                for i in article_list:
                    if i['search_period']=='1달이내' or i['search_period']== '1주이내' :
                        i['article_num']=xxx
                        ar.append(i)
                        xxx+=1
            elif search_period =='3달이내':
                for i in article_list:
                    if i['search_period']=='1달이내' or i['search_period']== '1주이내'or i['search_period']== '3달이내' :
                        i['article_num']=xxx
                        ar.append(i)
                        xxx+=1
            elif search_period =='1년이내':
                for i in article_list:
                    if i['search_period']=='1년이내' or i['search_period']=='1달이내' or i['search_period']=='1주이내'or i['search_period']=='3달이내':
                        i['article_num']=xxx
                        ar.append(i)
                        xxx+=1
            elif search_period =='1년이후':
                for i in article_list:
                    if i['search_period']=='1년이후':
                        i['article_num']=xxx
                        ar.append(i)
                        xxx+=1
            else:
                for i in article_list:
                    i['article_num']=xxx
                    ar.append(i)
                    xxx+=1
            return JsonResponse(ar, safe=False)
        ## 1-2 넘겨받은 검색어가 있을 때
        ### 검색 토큰에 대해 점수가 높은 공지사항 순으로 출력
        elif key!='':
            print(key,'key')
            # key_nospace = key.replace(' ','')
            # print(key_nospace)
            # key = list(change_key_search(key+' '+key_nospace).keys())
            key = list(change_key_search(key).keys())
            print(key)
            length = all_article_length
            globa_list = []
            score = {}
            for token in key:
                if mode == 'title':
                    if len(InverseTable.objects.filter(word=token))==1:
                        record = InverseTable.objects.get(word=token)
                        idf = np.log(length/(1+record.frequency))
                        location=eval(record.location)
                        for x in location:
                            globa=x[0]
                            local = x[1]
                            if globa not in score.keys():
                                globa_list.append(globa)
                                score[globa]=(1+np.log(1+local))*idf
                            else:
                                score[globa]+=(1+np.log(1+local))*idf 
                else:
                    if  len(ContentInverseTable.objects.filter(word=token))==1:
                        record = ContentInverseTable.objects.get(word=token)
                        idf = np.log(length/(1+record.frequency))
                        location=eval(record.location)
                        for x in location:
                            globa =x[0]
                            local = x[1]
                            if globa not in score.keys():
                                globa_list.append(globa)
                                score[globa]=(1+np.log(1+local))*idf
                            else:
                                score[globa]+=(1+np.log(1+local))*idf 
            cc=0
            article_list = []
            for g in globa_list:
                article = Article.objects.get(id = g)
                date = article.date
                s_date_ = datetime.datetime.strptime(date, '%Y-%m-%d')
                s_date = (today-s_date_).days
                if s_date<=7:
                    search_period_ = '1주이내'
                elif 7<s_date<=31:
                    search_period_ = '1달이내'
                elif 31<s_date<=31*3:
                    search_period_ = '3달이내'
                elif 31*3<s_date<=365 :
                    search_period_ = '1년이내'
                else: 
                    search_period_ = '1년이후'
                if s_date==0:
                    date_ = 날짜기준[0]
                elif s_date==1:
                    date_=날짜기준[1]
                else:
                    w_d = (today-datetime.timedelta(today.weekday())-s_date_).days
                    if w_d<=0:
                        date_=날짜기준[2]
                    elif 0<w_d<8:
                        date_ = 날짜기준[3]
                    else:
                        if (today-datetime.timedelta(today.day-1)-s_date_).days<=0:
                            date_ = 날짜기준[4]
                        elif (today.year, today.month)==ch_calender(s_date_,differ = 1):
                            date_=날짜기준[5]
                        elif s_date<=31*2:
                            date_=날짜기준[6]
                        elif 31*2<s_date<=31*3:
                            date_=날짜기준[7]
                        elif 31*3<s_date<=31*4:
                            date_=날짜기준[8]
                        elif 31*4<s_date<=31*5:
                            date_=날짜기준[9]
                        elif 31*5<s_date<=31*6:
                            date_=날짜기준[10]
                        elif 31*6<s_date<=365:
                            date_=날짜기준[11]
                        else:
                            date_=날짜기준[-1]
                title = article.title
                writer = article.writer
                href = article.href
                scores = score[g]
                article_dic={'title':title, 'writer':writer, 'href':href, 'updated':date_,'score':scores,'search_period':search_period_}
                article_list.append(article_dic)
                cc+=1
            print('총 소요시간 : ',round(time.time()-time_,4))
            article_list= sorted(article_list,key=lambda x:-x['score'])
            xxx = 1
            ar = []
            if search_period == '1주이내':
                for i in article_list:
                    if i['search_period']=='1주이내':
                        i['article_num']=xxx
                        ar.append(i)
                        xxx+=1
            elif search_period =='1달이내':
                for i in article_list:
                    if i['search_period']=='1달이내' or i['search_period']=='1주이내' :
                        i['article_num']=xxx
                        ar.append(i)
                        xxx+=1
            elif search_period =='3달이내':
                for i in article_list:
                    if i['search_period']=='1달이내' or i['search_period']=='1주이내' or i['search_period']=='3달이내' :
                        i['article_num']=xxx
                        ar.append(i)
                        xxx+=1
            elif search_period =='1년이내':
                for i in article_list:
                    if i['search_period']=='1년이내' or i['search_period']=='1달이내' or i['search_period']=='1주이내' or i['search_period']=='3달이내':
                        i['article_num']=xxx
                        ar.append(i)
                        xxx+=1
            elif search_period =='1년이후':
                for i in article_list:
                    if i['search_period']=='1년이후':
                        i['article_num']=xxx
                        ar.append(i)
                        xxx+=1
            elif search_period=='전체':
                for i in article_list:
                    i['article_num']=xxx
                    ar.append(i)
                    xxx+=1
                
            return JsonResponse(ar, safe=False)
    ## 2 카테고리가 있을 때
    ### 해당 카테고리에 대해서 최신순으로 정렬
    elif category !=None:
        article_list = []
        cc= 1
        if category=='채용':
            arts = Article.objects.filter(채용='1')
        elif category=='업체모집':
            arts =  Article.objects.filter(업체='1')
        elif category=='주민의견수렴':
            arts = Article.objects.filter(의견수렴='1')
        elif category=='청소년':
            arts = Article.objects.filter(청소년='1')
        elif category=='관람거리':
            arts = Article.objects.filter(관람='1')
        elif category=='주민자치교육':
            arts = Article.objects.filter(주민자치='1')
        elif category=='전문교육':
            arts = Article.objects.filter(전문교육='1')
        elif category=='의회_시청일정':
            arts = Article.objects.filter(의회='1')
        elif category=='대회_공모전':
            arts = Article.objects.filter(대회='1')
        elif category=='합격_당첨결과':
            arts = Article.objects.filter(합격자='1')
        for i in arts:
            title = i.title
            writer = i.writer
            href = i.href
            date = i.date
            s_date_ = datetime.datetime.strptime(date, '%Y-%m-%d')
            s_date = (today-s_date_).days\
            ## '오늘 / 어제 / 이번 주 / 지난 주 / 이번달 / 지난달 / 2달 전 / 3달 전 / 4달 전 / 5달 전 / 6개월 이상 / 1년 이상'
            if s_date==0:
                date_ = 날짜기준[0]
            elif s_date==1:
                date_=날짜기준[1]
            else:
                w_d = (today-datetime.timedelta(today.weekday())-s_date_).days
                if w_d<=0:
                    date_=날짜기준[2]
                elif 0<w_d<8:
                    date_ = 날짜기준[3]
                else:
                    if (today-datetime.timedelta(today.day-1)-s_date_).days<=0:
                        date_ = 날짜기준[4]
                    elif (today.year, today.month)==ch_calender(s_date_,differ = 1):
                        date_=날짜기준[5]
                    elif s_date<=31*2:
                        date_=날짜기준[6]
                    elif 31*2<s_date<=31*3:
                        date_=날짜기준[7]
                    elif 31*3<s_date<=31*4:
                        date_=날짜기준[8]
                    elif 31*4<s_date<=31*5:
                        date_=날짜기준[9]
                    elif 31*5<s_date<=31*6:
                        date_=날짜기준[10]
                    elif 31*6<s_date<=365:
                        date_=날짜기준[11]
                    else:
                        date_=날짜기준[-1]
            article_dic={'title':title, 'writer':writer, 'href':href, 'updated':date_,'s_date':s_date}
            article_list.append(article_dic)
            cc+=1
        article_list = sorted(article_list, key=lambda x:x['s_date'])
        for c,i in enumerate(article_list):
            i['article_num'] = c+1
        return JsonResponse(article_list, safe=False)
def add_word(request):
    if request.method == 'POST':
        words = request.POST.get('word')
        mode = request.POST.get('mode')
        words = words.split()
        for word in words:
            print(word)
            if mode =='title':
                if len(InverseTable.objects.filter(word=word))==0:
                    lis= []
                    for article in Article.objects.all():
                            
                        if word in article.title:
                            if word == '1월':
                                if article.title.count('1월')>article.title.count('11월'):
                                    lis.append([article.id, article.title.count(word)]) 
                            elif word == '2월':
                                if article.title.count('2월')>article.title.count('12월'):
                                    lis.append([article.id, article.title.count(word)]) 
                            else:
                                lis.append([article.id, article.title.count(word)]) 

                    InverseTable(word=word, frequency = len(lis),location = lis).save()
            else:
                if len(ContentInverseTable.objects.filter(word=word))==0:
                    lis= []
                    for article in Article.objects.all():
                        if word in article.content:
                            print(1)
                            if word == '1월':
                                if article.content.count('1월')>article.content.count('11월'):
                                    lis.append([article.id, article.content.count(word)]) 
                            elif word == '2월':
                                if article.content.count('2월')>article.content.count('12월'):
                                    lis.append([article.id, article.content.count(word)]) 
                            else:
                                lis.append([article.id, article.content.count(word)]) 
                    ContentInverseTable(word=word, frequency = len(lis),location = lis).save()
        return HttpResponse('add_your_word in %s \n\n word : %s' %(mode, words))
    else: 
        return render(request,'app/add_word.html')
# def upload_inverse(request):
#     with open('형태소분석기_앙상블/02역색인테이블만들기/vocab_title_table','rb') as f:
#         vocab_title_table = pickle.load(f)
#     with open('형태소분석기_앙상블/02역색인테이블만들기/vocab_con_table','rb') as f:
#         vocab_content_table = pickle.load(f)
#     for i in range(len(vocab_title_table)):
#         print(i/len(vocab_title_table))
#         InverseTable(word=vocab_title_table['vocab'].iloc[i],frequency=vocab_title_table['idf'].iloc[i],location=vocab_title_table['location'].iloc[i]).save()
#     for i in range(len(vocab_content_table)):
#         print(i/len(vocab_content_table))
#         ContentInverseTable(word=vocab_content_table['vocab'].iloc[i],frequency=vocab_content_table['idf'].iloc[i],location=vocab_content_table['location'].iloc[i]).save()
#     return HttpResponse(1)

# def upload(request):
#     dir_list = '관람 대회 업체 의견수렴 의회 채용 합격자 행사 전체교육 전문교육 청소년 주민자치'.split()
#     data =data14000_train['nouns']
#     for c,dir_ in enumerate(dir_list):
#         모델 = keras.models.load_model('files/%s라벨링_꼬꼬마.h5'%dir_,compile = False)
#         with open('files/new_labelling_file_%s라벨링_꼬꼬마_vocab'%dir_,'rb') as f:
#             vocab = pickle.load(f)
#         with open('files/new_labelling_file_%s라벨링_꼬꼬마_idf'%dir_,'rb') as f:
#             idf = pickle.load(f)
#         tf = data.apply(lambda x:get_tf(str(x),vocab = vocab))
#         tf_idf = tf.apply(lambda x:x*idf )
#         tf_idf = pd.DataFrame(dict(tf_idf).values())
#         pre_list = []
#         for i in 모델.predict(tf_idf):
#             if i>0.5:
#                 pre_list.append(1)
#             else:
#                 pre_list.append(0)
#         if c == 0:
#             데이타 = pd.concat([data14000, pd.DataFrame({'%s'%dir_:pre_list})],axis = 1)
#         else:
#             데이타 = pd.concat([데이타, pd.DataFrame({'%s'%dir_:pre_list})],axis = 1)
#     for record_num in range(len(데이타)):
#         title = 데이타.iloc[record_num,:]['title']
#         content = 데이타.iloc[record_num,:]['content']
#         date = 데이타.iloc[record_num,:]['date']
#         href = 데이타.iloc[record_num,:]['href']
#         writer = 데이타.iloc[record_num,:]['writer']
#         nouns = [x for x in 데이타.iloc[record_num,:]['title_nouns'] if len(x)>1]
#         관람 = 데이타.iloc[record_num,:]['관람']
#         대회 = 데이타.iloc[record_num,:]['대회']
#         업체 = 데이타.iloc[record_num,:]['업체']
#         의견수렴 = 데이타.iloc[record_num,:]['의견수렴']
#         의회 = 데이타.iloc[record_num,:]['의회']
#         채용 = 데이타.iloc[record_num,:]['채용']
#         합격자 = 데이타.iloc[record_num,:]['합격자']
#         행사 = 데이타.iloc[record_num,:]['행사']
#         전체교육 =데이타.iloc[record_num,:]['전체교육']
#         전문교육 = 데이타.iloc[record_num,:]['전문교육']
#         청소년 = 데이타.iloc[record_num,:]['청소년']
#         주민자치 = 데이타.iloc[record_num,:]['주민자치']
#         Article(title=title,content=content,date =date,writer=writer, href=href,title_noun = nouns, 채용=채용,합격자=합격자,의회=의회, 행사=행사,관람=관람, 대회=대회, 의견수렴=의견수렴, 업체=업체, 전체교육=전체교육, 전문교육=전문교육,청소년=청소년,주민자치=주민자치).save()
#         print(record_num/len(데이타))
#     return HttpResponse(1)