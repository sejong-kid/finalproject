from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Article
from django.forms.models import model_to_dict
import os
from collections import Counter
# !pip install konlpy
from konlpy.tag import Okt
# Create your views here.
import pandas as pd
import pickle
import operator
from django.db.models import Q 
from functools import reduce
import numpy as np
# os.chdir('drive/MyDrive/키워드추출후작업(230111)/동시등장행렬')
import pandas as pd
import pickle
from pykospacing.kospacing import Spacing
from django.core.paginator import Paginator
with open('[중요!][title단어로][filter거리2_3]각단어상위20개.pickle', 'rb') as f:
    동시등장상위20 = pickle.load(f)


def upload(request):
    with open('4315개데이터.pickle', 'rb') as a:
        df = pickle.load(a)
        df = pd.DataFrame(df)
        # print(df.iloc[1,:])
        for i in range(len(df)):
            record = df.iloc[i,:]
            article = Article(site_name = record['writer'], title = record['title'], updated = record['date'],file=record['file'],detail = record['content'], href =record['href'],title_noun = record['title_noun'], content_noun = record['content_noun'] )
            article.save()


    return HttpResponse(df)
def index(request):
    return render(request, 'app/index.html')
def page2(request):
    key = request.GET.get('key')
    original_key = key
    s = Spacing()
    okt = Okt()
    key = s(key)
    key = okt.nouns(key)
    cou = 0
    dic = {}
    for i in key:
        cou+=1
        dic[i]=20*((len(key)-cou/2)/len(key))**1.2
        try:
            for j in 동시등장상위20[i][:5]:
                dic[j[0]]=j[1]
        except:
            pass
    점수리스트 = []
    점수상세리스트 = []
    # 보다 넓은 범위를 찾아주는 단어는 가중치를 조금 낮춰주고(ex공고)
    # 무언가를 특정하는 단어는 가중치를 좀더주면 좋지않을까?
    # 공고는 공고인데 모집!이라는 단어가 원하는 공지사항을 추출하는데 있어 중요도가 높으니까
    all_data = Article.objects.all()
    for  i in all_data:
        df_noun_title =i.title_noun.replace("['",'').replace("']",'').replace("', '",' ').split(' ')
        df_noun_content = i.content_noun.replace("['",'').replace("']",'').replace("', '",' ').split(' ')
        title_nouns = sorted(Counter(list(df_noun_title)).items(), key = lambda x:x[1])
        점수=0
        점수상세 = []
        for noun,counts in title_nouns:
            if counts >3:
                counts = 3
            if noun in dic.keys():
                점수상세.append([noun, dic[noun]])
                점수 +=((dic[noun])*counts)
        content_nouns = sorted(Counter(list(df_noun_content)).items(), key = lambda x:x[1])
        for noun,counts in content_nouns:
            if counts >5:
                counts = 4
            if noun in dic.keys():
                점수상세.append([noun, dic[noun]])
                점수 +=((dic[noun])*counts/5)
        점수리스트.append(점수)
        점수상세리스트.append(점수상세)
    count = len([x for x in 점수리스트 if x>len(key)*3])
        # 여기까지함
    article_list = []
    점수_ = np.array(점수리스트)[np.array(점수리스트).argsort()[::-1][:count]]
    # print(점수_)
    for cc,i in enumerate(np.array(점수리스트).argsort()[::-1][:count]):
        title = Article.objects.get(id = (i+401)).title
        writer = Article.objects.get(id = (i+401)).site_name
        href = Article.objects.get(id = (i+401)).href
        file = Article.objects.get(id = (i+401)).file
        date = Article.objects.get(id = (i+401)).updated
        score = 점수_[cc]
        article_dic={'article_num':cc+1,'title':title, 'writer':writer, 'href':href, 'file':file,'updated':date, 'score':score}
        article_list.append(article_dic)
        cases = len(article_list)
        page = request.GET.get('page')
        paginator = Paginator(article_list,10)
        try:
            page_obj = paginator.page(page)
        except:
            page = 1
            page_obj = paginator.page(page)
        if page ==str(1):
            before_page = page
        else:
            before_page = str(int(page)-1)
        if page != str(cases//10+1):
            after_page = str(1+int(page))
        else:
            after_page = page
        # print(after_page, before_page, page)
        
    return render(request, 'app/page2.html', context = {'key':original_key,'cases':cases, 'page_obj':page_obj, 'paginator':paginator,'before_page_num':before_page,'page_num':page,'after_page_num':after_page})




    
# with open('[중요!][title단어로][filter거리2_3]각단어상위20개.pickle','rb') as f:
#     동시등장확률_최상위20개 = pickle.load(f)

# a = s(a)
# print(a)
# print(a)
# a = okt.nouns(a)
# print(a)
# dic = {}
# # 상위5개
# cou = 0
# for i in a:
#   cou+=1
#   dic[i]=20/cou
#   try:
#     for j in 동시등장확률_최상위20개[i][:5]:
#       dic[j[0]]=j[1]
#   except:
#     pass
# dic
# 점수리스트 = []
# 점수상세리스트 = []
# for i in range(len(df)):
#   title_nouns = sorted(Counter(list(df_noun_title[i])).items(), key = lambda x:x[1])
#   점수=0
#   점수상세 = []

#   for noun,counts in title_nouns:
#     if counts >3:
#       counts = 3
#     if noun in dic.keys():
#       점수상세.append([noun, dic[noun]])
#       점수 +=((dic[noun])*counts)
#   content_nouns = sorted(Counter(list(df_noun_content[i])).items(), key = lambda x:x[1])
#   # 점수=0
#   # 점수상세 = []

#   for noun,counts in content_nouns:
#     if counts >3:
#       counts = 2
#     if noun in dic.keys():
#       점수상세.append([noun, dic[noun]])
#       점수 +=((dic[noun])*counts/2)


#   점수리스트.append(점수)
#   점수상세리스트.append(점수상세)
# print(점수리스트)
# for i in np.array(점수리스트).argsort()[::-1][:20]:
#   print(i)
#   print(점수상세리스트[i])
#   print(df.iloc[i]['title'])
#   # print(df.iloc[i]['content'])
# def article(request):
#     key = request.GET.get('key')
#     print(key)
#     key = key.split(' ')
#     print(key)
#     # okt = Okt()
#     if key[0] =='all':
#         articles = Article.objects.all()
#     else:
#         articles = Article.objects.filter(reduce(operator.and_, (Q(title__contains=x) for x in key)))
#     list_ = []
#     for i in articles:
#         list_.append(model_to_dict(i))
#     return JsonResponse(list_, safe=False)
# def read(request):
#     key = request.GET.get('key')
#     s = Spacing()
#     okt = Okt()
#     key = s(key)
#     key = okt.nouns(key)
#     cou = 0
#     dic = {}
#     for i in key:
#         cou+=1
#         dic[i]=20*((len(key)-cou/2)/len(key))**1.2
#         try:
#             for j in 동시등장상위20[i][:5]:
#                 dic[j[0]]=j[1]
#         except:
#             pass
#     점수리스트 = []
#     점수상세리스트 = []
#     all_data = Article.objects.all()
#     for  i in all_data:
#         df_noun_title =i.title_noun.replace("['",'').replace("']",'').replace("', '",' ').split(' ')
#         df_noun_content = i.content_noun.replace("['",'').replace("']",'').replace("', '",' ').split(' ')
#         title_nouns = sorted(Counter(list(df_noun_title)).items(), key = lambda x:x[1])
#         점수=0
#         점수상세 = []
#         for noun,counts in title_nouns:
#             if counts >3:
#                 counts = 3
#             if noun in dic.keys():
#                 점수상세.append([noun, dic[noun]])
#                 점수 +=((dic[noun])*counts)
#         content_nouns = sorted(Counter(list(df_noun_content)).items(), key = lambda x:x[1])
#         for noun,counts in content_nouns:
#             if counts >5:
#                 counts = 4
#             if noun in dic.keys():
#                 점수상세.append([noun, dic[noun]])
#                 점수 +=((dic[noun])*counts/5)
#         점수리스트.append(점수)
#         점수상세리스트.append(점수상세)
#     count = len([x for x in 점수리스트 if x>len(key)*3])
#     article_list = []
#     점수_ = np.array(점수리스트)[np.array(점수리스트).argsort()[::-1][:count]]
#     print(점수_)
#     for cc,i in enumerate(np.array(점수리스트).argsort()[::-1][:count]):
#         title = Article.objects.get(id = (i+401)).title
#         writer = Article.objects.get(id = (i+401)).site_name
#         href = Article.objects.get(id = (i+401)).href
#         file = Article.objects.get(id = (i+401)).file
#         date = Article.objects.get(id = (i+401)).updated
#         score = 점수_[cc]
#         article_dic={'title':title, 'writer':writer, 'href':href, 'file':file,'updated':date, 'score':score}
#         article_list.append(article_dic)

#     return JsonResponse(article_list, safe=False )
# def search(request):
#     return render(request, 'app/read(algorithm).html')

#   print(np.array(점수리스트)[i])