import time
import random
import requests
from bs4 import BeautifulSoup
import pymysql

#Some User Agents
hds=[
{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
{'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},\
{'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},\
{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16'}
]

def book_spider(douseries_num):
	page_num = 1
	book_list = []
	try_times = 0
	
	while True:
		#https://book.douban.com/series/586?page=1
		douseries_url ='https://book.douban.com/series/'+str(douseries_num)+'?page='+str(page_num)
		
		time.sleep(random.random())
		
		try:
			req = requests.get(douseries_url,headers=hds[page_num%len(hds)])
	
			plain_txt = req.text
		except requests.exceptions.ConnectionError as e:
			print('获取网页url错误！————>',e)
			
		
		soup = BeautifulSoup(plain_txt)
		
		list_soup = soup.find_all('li',class_='subject-item')
		
		try_times +=1
		if list_soup == None and try_times<200:
			continue
		elif list_soup == None or len(list_soup)<=1:
			break
		
		for book_info in list_soup:
			#书名
			title = book_info.find_all('a')[1].stripped_strings #返回迭代器
			title_list =list(title)
			
			#链接
			book_link = book_info.find('a',class_='nbg').get('href')
			
			#作者，出版社，出版年
			desc = book_info.find('div',class_='pub').string.strip()
			desc_list = desc.split('/')
			
			
			#评分，评价人数
			rating_nums = book_info.find('span',class_='rating_nums')
			rating_pl = book_info.find('span',class_='pl')
			
			try:
				book_name = str(title_list[0]+title_list[1])
			except:
				book_name = str(title_list[0])
				
			try:
				star_info = '书籍评分： '+rating_nums.string.strip()
			except:
				star_info = '书籍评分： 暂无'
			try:
				person_info = '评价人数： '+rating_pl.string.strip()
			except:
				person_info = '评价人数：暂无'
					
			if len(desc_list) ==4:
				try:
					book_name = str(title_list[0]+title_list[1])
				except:
					book_name = str(title_list[0])
				
				try:
					author_info = '作者/译者：'+ desc_list[0].strip()
				except:
					author_info = '作者/译者：暂无'
					
				try:
					pub_info = '出版社： '+ desc_list[1].strip()
				except:
					pub_info = '出版社： 暂无'
					
				try:
					time_info = '出版年月： '+ desc_list[2].strip()
				except:
					time_info = '出版年月： 暂无'

				try:
					price_info = '价格： ' + desc_list[3].strip()
				except:
					price_info = '价格： 暂无'
				
			elif len(desc_list) ==5:
				try:
					author_info = '作者/译者：'+ desc_list[0].strip()+'/'+desc_list[1].strip()
				except:
					author_info = '作者/译者：暂无'
					
				try:
					pub_info = '出版社： '+  desc_list[2].strip()
				except:
					pub_info = '出版社： 暂无'
					
				try:
					time_info = '出版年月： '+ desc_list[3].strip()
				except:
					time_info = '出版年月： 暂无'

				try:
					price_info = '价格： ' + desc_list[4].strip()
				except:
					price_info = '价格： 暂无'
				
			
			book_list.append([book_name,author_info,pub_info,time_info,star_info,person_info,book_link])
		
		print('获取书籍————第%d页'%page_num,'\n')
		page_num +=1
	
	#douseries_title = soup.title.get_text()
	#douseries_about = soup.select('div[class=douseries_about')[0]
	
	print('\n总共收集到%d本书！'%len(book_list))
	return(book_list)
		

def do_spider(douseries_num):
	
	book_list= book_spider(douseries_num)
	
	book_list = sorted(book_list,key=lambda x:x[4],reverse=True)
	
	return(book_list)

def connect_douseries():	
	try:
		ds = pymysql.connect(host='127.0.0.1',user='banquan',password='12345',db='douseries')
		
		ds_cur = ds.cursor()
		print('数据库连接成功！')
	except:
		print('连接数据库douseries失败！')
	
	return(ds,ds_cur)
	
def create_table(ds_cur):
	try:
		sql_create = '''create table douseries (
					book_name varchar(255),
					author_info varchar(255),
					pub_info varchar(255),
					time_info varchar(255),
					star_info varchar(255),
					pl_info varchar(255),
					book_link varchar(255)
				
				)'''

		ds_cur.execute(sql_create)
		
		print('创建数据库表格成功！')
	
	except:
		print('创建数据库表格失败！')

def ins_table(ds_cur,book_list):
	for bl in book_list:
		sql_insert = 'insert into douseries values (%s,%s,%s,%s,%s,%s,%s)'
		try:
			ds_cur.execute(sql_insert,(bl[0],bl[1],bl[2],bl[3],bl[4],bl[5],bl[6]))
			ds.commit()
		except:
			ds_cur.rollback()
			print('写入数据库出错！')
		ds.commit()

def drop_table(ds_cur):
	try:		
		ds_cur.execute('drop table douseries')
		print('删除表格成功！')
	except:
		print('删除表格失败！')
		

def close_ds(ds):
	
	ds.close()
	print('关闭数据库')
			
			
if __name__ =='__main__':
	
	#运行时间
	time.clock()
	
	#586 677 865 282
	douseries_num = 586
	
	book_list= do_spider(douseries_num)
	
	ds,ds_cur = connect_douseries()
	create_table(ds_cur)
	
	ins_table(ds_cur,book_list)
	
	close_ds(ds)
	
	t1 = time.clock()
	print('\n 运行时间： ',t1)