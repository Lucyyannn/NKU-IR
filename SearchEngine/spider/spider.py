import os
import re
import requests
import pdfplumber
from io import BytesIO
from scrapy.selector import Selector
import pandas as pd
from urllib.parse import urlparse, urljoin

### url收集
url_list = []
# # 1.南开要闻
url_list.append('http://news.nankai.edu.cn/ywsd/index.shtml')
for i in range(1, 10):
    url = f'http://news.nankai.edu.cn/ywsd/system/count//0003000/000000000000/000/000/c0003000000000000000_00000000{i}.shtml'
    url_list.append(url)
for i in range(10,100):
    url = f'http://news.nankai.edu.cn/ywsd/system/count//0003000/000000000000/000/000/c0003000000000000000_0000000{i}.shtml'
    url_list.append(url)
for i in range(100,641):
    url = f'http://news.nankai.edu.cn/ywsd/system/count//0003000/000000000000/000/000/c0003000000000000000_000000{i}.shtml'
    url_list.append(url)
# 2. 媒体南开
url_list.append('https://news.nankai.edu.cn/mtnk/index.shtml')
for i in range(1, 10):
    url = f'https://news.nankai.edu.cn/mtnk/system/count//0006000/000000000000/000/000/c0006000000000000000_00000000{i}.shtml'
    url_list.append(url)
for i in range(10, 100):
    url = f'https://news.nankai.edu.cn/mtnk/system/count//0006000/000000000000/000/000/c0006000000000000000_0000000{i}.shtml'
    url_list.append(url)
for i in range(100, 973):
    url = f'https://news.nankai.edu.cn/mtnk/system/count//0006000/000000000000/000/000/c0006000000000000000_000000{i}.shtml'
    url_list.append(url)
# 3. 南开故事
url_list.append('https://news.nankai.edu.cn/nkrw/index.shtml')
for i in range(1, 10):
    url = f'https://news.nankai.edu.cn/nkrw/system/count//0008000/000000000000/000/000/c0008000000000000000_00000000{i}.shtml'
    url_list.append(url)
for i in range(10, 67):
    url = f'https://news.nankai.edu.cn/nkrw/system/count//0008000/000000000000/000/000/c0008000000000000000_0000000{i}.shtml'
    url_list.append(url)
# 4. 南开大学报
url_list.append('https://news.nankai.edu.cn/nkdxb/index.shtml')
for i in range(1, 10):
    url = f'https://news.nankai.edu.cn/nkdxb/system/count//0011000/000000000000/000/000/c0011000000000000000_00000000{i}.shtml'
    url_list.append(url)
for i in range(10, 77):
    url = f'https://news.nankai.edu.cn/nkdxb/system/count//0011000/000000000000/000/000/c0011000000000000000_0000000{i}.shtml'
    url_list.append(url)
# 5.多彩校园
url_list.append('https://news.nankai.edu.cn/dcxy/index.shtml')
for i in range(1, 10):
    url = f'https://news.nankai.edu.cn/dcxy/system/count//0005000/000000000000/000/000/c0005000000000000000_00000000{i}.shtml'
    url_list.append(url)
for i in range(10, 100):
    url = f'https://news.nankai.edu.cn/dcxy/system/count//0005000/000000000000/000/000/c0005000000000000000_0000000{i}.shtml'
    url_list.append(url)
for i in range(100, 526):
    url = f'https://news.nankai.edu.cn/dcxy/system/count//0005000/000000000000/000/000/c0005000000000000000_000000{i}.shtml'
    url_list.append(url)
# 6. 综合新闻
url_list.append('https://news.nankai.edu.cn/zhxw/index.shtml')
for i in range(1, 10):
    url = f'https://news.nankai.edu.cn/zhxw/system/count//0004000/000000000000/000/000/c0004000000000000000_00000000{i}.shtml'
    url_list.append(url)
for i in range(10, 100):
    url = f'https://news.nankai.edu.cn/zhxw/system/count//0004000/000000000000/000/000/c0004000000000000000_0000000{i}.shtml'
    url_list.append(url)
for i in range(100, 834):
    url = f'https://news.nankai.edu.cn/zhxw/system/count//0004000/000000000000/000/000/c0004000000000000000_000000{i}.shtml'
    url_list.append(url)
##################################
# 7.校办文件
for i in range(1,572):
    url = f'https://xb.nankai.edu.cn/category/2/{i}'
    url_list.append(url)
for i in range(1,489):
    url = f'https://xb.nankai.edu.cn/category/8/{i}'
    url_list.append(url)
for i in range(1,84):
    url = f'https://xb.nankai.edu.cn/category/9/{i}'
    url_list.append(url)
for i in range(1,128):
    url = f'https://xb.nankai.edu.cn/category/1/{i}'
    url_list.append(url)

for i in range(1,22):
    url = f'https://xb.nankai.edu.cn/category/3/{i}'
    url_list.append(url)
for i in range(1,19):
    url = f'https://xb.nankai.edu.cn/category/4/{i}'
    url_list.append(url)
for i in range(1,22):
    url = f'https://xb.nankai.edu.cn/category/5/{i}'
    url_list.append(url)
for i in range(1,89):
    url = f'https://xb.nankai.edu.cn/category/6/{i}'
    url_list.append(url)
for i in range(1,87):
    url = f'https://xb.nankai.edu.cn/category/13/{i}'
    url_list.append(url)
for i in range(1,81):
    url = f'https://xb.nankai.edu.cn/category/14/{i}'
    url_list.append(url)
for i in range(1,233):
    url = f'https://xb.nankai.edu.cn/category/15/{i}'
    url_list.append(url)


# 创建数据结构 存储爬虫到的内容
content_df = pd.DataFrame(columns=['url','title','is_pdf','save_path'])
content_df.index.name = 'doc_id'
url_id=dict()

doc_id = 0
total_num = 0

# 目录页
def Spider(url):
    global doc_id,total_num
    if not url_id.get(url,None):#去重
        doc_id +=1
        this_id = doc_id#当前网页的doc_id
        response = requests.get(url,allow_redirects=True)
        if response.status_code not in [200]:
            print(f'Error in Requesting Page: {response.status_code} - {url}')
            return
        selector = Selector(response)
        title = selector.css('title::text').get()


        # 获取links
        links = selector.css('a::attr(href)').getall()
        for link in links:
            # 跳过邮件
            if link.startswith('mailto:'):
                continue
            if not link.startswith("http"):
                link = urljoin(url, link)
            if not url_id.get(link,None):
                doc_id +=1
                link_id=doc_id
                #对该网页进一步分析
                Page_extract(link,link_id)

        # 保存该目录页
        path_name = f'h{str(this_id)}'
        save_path = f'./FinalPages3/{path_name}.html'
        with open(save_path, mode='w', encoding='utf-8') as f:
            f.write(response.text)
        content_df.loc[doc_id] = [url,title,0,save_path]
        url_id[url]=this_id
        total_num += 1
        print(f'Total: {total_num} - Id: {this_id} - {url}')

# 基本页
def Page_extract(url,this_id):
    global total_num
    if not url_id.get(url,None):#去重
        try:
            response = requests.get(url,allow_redirects=True)
            real_url = response.url
            if response.status_code not in [200]:
                print(f'Error in Requesting Page: {response.status_code} - {real_url}')
                return
            selector = Selector(response)
            title = selector.css('title::text').get()

            if not title:#处理无标题——默认NoTitle
                title = "NoTitle"

            save_path = ''
            is_pdf = 0
            # 下载pdf文件
            if real_url.endswith('.pdf'):
                is_pdf = 1
                save_path,title =download_pdf(real_url,this_id)
            #保存网页内容
            else:
                path_name = f'h{str(this_id)}'
                save_path = f'./FinalPages3/{path_name}.html'
                with open(save_path, mode='w', encoding='utf-8') as f:
                    f.write(response.text)
            #将信息登记入csv文件
            content_df.loc[doc_id] = [url,title,is_pdf,save_path]
            total_num += 1
            url_id[url]=this_id
            print(f'Total: {total_num} - Id: {this_id} - {url}')

        except Exception as e:
            print(f'Error in Requesting Page: {e} - {url}')

#下载pdf文件
def download_pdf(url,this_id):
    title = extract_title(url)#获取pdf标题
    try:
        response = requests.get(url,allow_redirects=True)
        if response.status_code == 200:
            path_name=f'p{str(this_id)}'
            pdf_path = f'./pdfs/{path_name}.pdf'
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            print(f'PDF downloaded: {pdf_path}')
        else:
            print(f'Failed to download PDF: {url}')
    except Exception as e:
        print(f'Error downloading PDF: {e} - {url}')
    return pdf_path,title

def extract_title(url):
    match = re.search(r'/([^/]+)\.pdf$',url)
    if match:
        return match.group(1)
    else:
        return 'NoTitle'

if __name__ == '__main__':
    # 创建文件夹 存放爬虫到的页面
    if not os.path.exists('./FinalPages3'):
        os.makedirs('./FinalPages3')
    if not os.path.exists('./pdfs'):
        os.makedirs('./pdfs')
    
    # 开始爬虫
    for url in url_list:
        Spider(url)
        
    content_df.to_csv("./entry3.csv", mode='a', header=False, index=True) #追加
            
    print(f'爬虫结束，共爬取{total_num}个网页')
    print(f'共记录{len(content_df)}个条目')
    print(f'共保存{len(content_df[content_df["is_pdf"]==1])}个pdf文件')


# & D:/Anaconda/envs/irse/python.exe d:/IRSearchEngine/spider/spider.py
