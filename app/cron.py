import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events, DjangoJobStore
import requests 
from bs4 import BeautifulSoup as bs ;
import re
import pandas as pd
def job():
    url_link = "https://www.sejong.go.kr/bbs/R0071/list.do?PageIndex=%s"
    page_num = 1
    dic = {}
    article_path_list =[]
    article_title_list =[]
    article_detail_list = []
    upload_time_list = []
    file_ox = []
    for i in range(50):
        site_name = '세종시청'
        full_url = url_link%page_num
        response = requests.get(full_url)
        response_text = response.text
        response_html = bs(response_text)
        article_table = response_html.select('tbody')[0]
        article_list = article_table.select('tr')[1:]
        for article in article_list:
            unit_list = article.select('td')
            article_path = re.sub('[\n\t\r]',' ',unit_list[1].select_one('a')['href']).strip()
            article_path = 'https://www.sejong.go.kr/'+article_path
            article_title = re.sub('[\n\t\r]',' ',unit_list[1].select_one('a').text).strip()
            upload_time = re.sub('[\n\t\r]',' ',unit_list[4].text).strip()
            file_ox
            res = requests.get(article_path)
            article_html = bs(res.text)
            article_detail = article_html.select_one('div.bbs--view--content').text
            
            file = article.select('td')[5]
            if file.text.strip() == '':
                file = 0
            else :
                file = 1
            article_path_list.append(article_path)
            article_title_list.append(article_title)
            article_detail_list.append(article_detail)
            upload_time_list.append(upload_time)
            file_ox.append(file)
        page_num +=1



        
    dic['article_title']=article_title_list
    dic['upload_time']=upload_time_list
    dic['article_path']=article_path_list
    dic['article_detail']=article_detail_list
    dic['file_ox'] = file_ox
    
def main():
    sched = BackgroundScheduler()
    sched.add_job(job,'interval', seconds=3600, id='test')
    sched.start()
