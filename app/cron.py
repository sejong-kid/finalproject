# from django_apscheduler.jobstores import register_events, DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from django.db.models import Max
from .models import Article
from .utils import *
def job():
    print('정기적인 크롤링 시작.')
    dic = crolling() ## 오늘자 업로드 된 공지사항을 크롤링소스코드에 날짜비교연산 코드를 추가해주어 작동되도록 함 
    ## 최종 반환형태는 딕셔너리 형태임
    print('크롤링완료')
    iii = []
    for i in Article.objects.all():
        ix= int(i.id )
        iii.append(ix)
    last_id = sorted(iii,reverse=True)[0]
    print('마지막인덱스',last_id)
    # last_id = int(Article.objects.all().aggregate(Max('id'))['id__max'])
    ids = last_id+1
    ## 중복체크
    #중복체크는 href 즉 링크 주소가 정확히 일치하는게 1개라도 있으면 중복으로 체크하여, 새로운 공지사항데이터가 아닌 중복데이터로 인식하게 둔다
    #최종적으로 그 중복데이터는 새로저장하는 데이터에서 제외한다.
    #제외되지 않는 데이터만 딕셔너리형태로 datas 변수에 담는다
    print('기존 db내 데이터와 중복여부 대조 및 완전히 새로운 데이터만 데이터프레임에 담기')
    href_=[]
    date_=[]
    content_=[]
    title_=[]
    writer_=[]
    id_ = []
    for i in range(len(dic['id'])):
        if len(Article.objects.filter(href=dic['href'][i]))==0:
            id_.append(ids)
            href_.append(dic['href'][i])
            date_.append(dic['date'][i] )
            content_.append(dic['content'][i])
            title_.append(dic['title'][i])
            writer_.append(dic['writer'][i])
            ids+=1
    datas = pd.DataFrame({'id':id_,'title':title_,'content':content_, "href":href_, "date":date_,"writer":writer_})    
    if len(datas)!=0: ## 중복 안되는 완전 새로운 데이터가 1개도 없을시 생기는 오류를 대비해서 1개 이상일때만 실행되도록 함수를 구성
        upload_to_article(datas) ## Article테이블에 업로드하는 함수 # utils.py 내부에 존재 
                                 # 미리 저장해둔 h5파일과 그에 맞는 부속파일들을 불러와서 이진분류 후 그 정보도 같이 업로드
        change_content_key(datas) ## 각공지사항에 출현하는 단어를 역색인 참조 테이블 ContentInverseTable에 [공지사항 인덱스, 그 단어의 출현수]형태로
                                  # 위치를 저장시키고, 총 몇개의 공지사항에서 그 단어를 가지고있는지도 frequency컬럼에 저장하도록 함
        change_title_key(datas)## 각공지사항에 출현하는 단어를 역색인 참조 테이블 InverseTable에 [공지사항 인덱스, 그 단어의 출현수]형태로
                                # 위치를 저장시키고, 총 몇개의 공지사항에서 그 단어를 가지고있는지도 frequency컬럼에 저장하도록 함
    print("모든 작업 끝 ok")
def main():
    sched = BackgroundScheduler()
    sched.add_job(job,'interval',hours = 1) ##1시간 간격으로 위 코드가 실행되도록 함
    sched.start()
