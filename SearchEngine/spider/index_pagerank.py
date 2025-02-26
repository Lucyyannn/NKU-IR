"""
此文件主要用于解析网页内容、构建索引、计算pagerank
"""
from whoosh.fields import Schema, TEXT, ID,BOOLEAN
from whoosh.index import create_in
import os
from bs4 import BeautifulSoup
import networkx as nx
import pandas as pd
from urllib.parse import urljoin
import json
import fitz  # PyMuPDF

entrys = pd.read_csv('./entry.csv')


####################################  辅助函数  #######################################
import jieba
#去停用词
with open('hit_stopwords.txt', 'r', encoding='utf-8') as f:
    stopwords = f.read().splitlines()
print(stopwords)
def filter_stopwords(words):
    filtered_words = [word for word in words if word not in stopwords]
    return ' '.join(filtered_words)

def process_text(text):
    #分词
    words = jieba.lcut(text)
    #去停用词
    content = filter_stopwords(words)
    return content

###################################  构建索引 +计算pagerank ######################################

# 定义索引模式
schema = Schema(
    title=TEXT(stored=True),        # 标题
    content=TEXT(stored=True),      # 正文内容（分词、去停用词后）
    raw_content=TEXT(stored=True),  # 原始内容
    path=ID(stored=True),           # 网址
    anchor_texts=TEXT(stored=True), # 存储锚文本
    #is_pdf=BOOLEAN(stored=True)     # 是否为pdf文件
)

# 创建索引目录
index_dir = "index"
if not os.path.exists(index_dir):
    os.mkdir(index_dir)
# 创建索引
ix = create_in(index_dir, schema)

# 创建一个有向图 存储网页之间链接关系
G = nx.DiGraph()

batch_size = 1000
count = 0
# 遍历所有网页，解析网页内容，构建索引，计算pagerank
with ix.writer() as writer:
    for i in range(entrys.shape[0]-1, -1, -1):
        # 读取并解析 HTML/pdf 文件
        url = entrys.iloc[i,1] if pd.notna(entrys.iloc[i, 1]) else "NoUrl"
        title = entrys.iloc[i,2] if pd.notna(entrys.iloc[i, 2]) else "NoTitle"
        is_pdf = entrys.iloc[i,3]
        file_path = entrys.iloc[i,4]
        if not is_pdf:#对于非pdf的html
            with open(file_path, 'r', encoding='utf-8') as file:
                html_whole_content = file.read()
        
            soup = BeautifulSoup(html_whole_content, 'html.parser')
            # 提取正文内容 和 锚文本
            content = soup.find('td', id='txt').get_text(strip=True) if soup.find('td', id='txt') else ""
            anchor_texts = [a.get_text(strip=True) for a in soup.find_all('a')]
            anchor_texts = anchor_texts if anchor_texts else "" 

            # 所有链接,构建 PageRank 图
            links = [a['href'] for a in soup.find_all('a', href=True)]
            for link in links:
                if not link.startswith('http'):
                    link = urljoin(url, link)
                G.add_edge(url, link)

        else:#对于pdf文件
            content = ""
            with fitz.open(file_path) as doc:
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)  # 加载页面
                    content += page.get_text("text")  # 获取页面的纯文本
            anchor_texts=""
 
        # 正文内容清洗
        cleaned_content = process_text(content) if content!= "" else ""

        # 添加当前文档到索引
        writer.add_document(
            title=title,
            content=cleaned_content,
            raw_content=content,
            path=url,
            anchor_texts=" ".join(anchor_texts) if anchor_texts!= "" else "",
            #is_pdf=is_pdf
        )
        # 每处理1000个提交一次
        count += 1
        if count % batch_size == 0 or i == entrys.shape[0]-1:
            print(f"已处理{count}个网页")

            
# 计算 PageRank，保存到json文件
pagerank = nx.pagerank(G)
with open('./pagerank2.json', 'w') as f:
    json.dump(pagerank, f, indent=4)
print("PageRank 计算完成!")