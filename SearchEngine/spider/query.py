from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from whoosh import scoring
from urllib.parse import unquote
import json
import numpy as np
import sqlite3
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter

#读取索引
ix = open_dir("./spider/index")
#读取pagerank字典
with open("./spider/pagerank.json", 'r') as f:
    pagerank = json.load(f)
with open("./spider/url_path.json","r") as dic:
    url_path = json.load(dic)

#清理输出
def clean_content(content):
    if content.startswith("[键入文字]"):
        content = content[9:]
    # 按行分割
    lines = content.splitlines()
    # 去除空行,清理每行前后的空白字符
    cleaned_lines = [line.strip() for line in lines if line.strip()]
    # 合并
    cleaned_content = "\n".join(cleaned_lines)
    
    return cleaned_content
#########################  数据库历史记录表访问 #############
# 访问历史
def get_history_to_display(conn,user_id):
    history = conn.execute("""
        SELECT query, MAX(timestamp) AS latest_timestamp
        FROM search_history
        WHERE user_id = ?
        GROUP BY query
        ORDER BY latest_timestamp DESC
        LIMIT 10
    """, (user_id,)).fetchall()
    return history

def get_history_to_compute(conn,user_id):
    queries = conn.execute("""
        SELECT query, timestamp
        FROM search_history
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, (user_id,)).fetchall()
    return queries


#############################  快照 ##########################
# 读取本地快照路径
def snapshot(results):
    for result in results:
        url = result['path']
        # 根据url查找对应的本地快照路径
        local_path = url_path.get(url)
        result['local_snapshot_path'] = local_path  # 添加本地路径字段
    return results

############################ 个性推荐 ########################

def clean_recommendation(recommendations):
    unique_recommendations = {}

    for result in recommendations:
        path = result['path']
        
        # 如果 path 已存在，更新权重和score
        if path in unique_recommendations:
            existing_result = unique_recommendations[path]
    
            existing_result['score']+=result['score']
        else:# 如果 path 不存在，直接添加
            unique_recommendations[path] = result

    # 将字典中的结果转换回列表
    final_recommendations = list(unique_recommendations.values())
    return final_recommendations

def recommend_search(history):
    # 提取所有查询历史中的查询词
    query_list = [q['query'] for q in history]
    if len(query_list)==0:
        return []
    length = float(len(query_list))
    
    # 统计每个查询词的出现次数
    query_counter = Counter(query_list)
    print("query_counter:",query_counter)
    query_frequency = {query: query_counter[query] / length for query in query_counter}
    print("query_frequency:",query_frequency)
    
    # 对查询列表去重，排序
    all_queries = [item[0] for item in query_counter.most_common()]  
    print("all_queries:",all_queries)

    recommendations = []
    limit_n = 10/len(all_queries) if len(all_queries) <3 else 3
    times = min(3,len(all_queries))
    for i in range(times):#只对频率最高的三个进行查询
        query_text = all_queries[i]
        if '*'in query_text or '?' in query_text:#跳过通配查询
            continue
        with ix.searcher(weighting=scoring.TF_IDF()) as searcher:
            query = QueryParser("content", ix.schema).parse(query_text)
            results = searcher.search(query, limit=limit_n)
            for result in results:
                result_copy = {
                    'title': unquote(result['title']),
                    'path': result['path'],
                    'score': result.score,  
                    'pagerank': pagerank.get(result['path'], 0),
                    'weight': query_frequency[query_text]  
                }
                result_copy['score']*=result_copy['weight']
                recommendations.append(result_copy)
    # 去重
    recommendations = clean_recommendation(recommendations)
    #将所有结果排序
    sorted_recommendations = sorted(recommendations, key=lambda r: (r['score'], r['pagerank']), reverse=True)
    
    # 返回最多9个推荐结果
    return sorted_recommendations[:9] if len(sorted_recommendations) >= 9 else sorted_recommendations


############################ 查询检索 #########################

# 基础查询，添加个性化检索功能后不再使用此函数
# # 搜索
# def basic_search(query_str,limit=None):
#     with ix.searcher(weighting=scoring.TF_IDF()) as searcher:#加权策略：TF-IDF
#         query = QueryParser("content", ix.schema).parse(query_str)# 解析查询
#         results = searcher.search(query, limit=None)#执行查询
        
#         # 排序：先按相关性排序，再按PageRank排序
#         sorted_results = sorted(results, key=lambda r: (r.score, pagerank.get(r['path'], 0)), reverse=True)

#         # 格式化输出
#         formatted_results = []
#         for result in sorted_results:
#             format_result={}
#             format_result['title']=unquote(result['title'])
#             format_result['content']=clean_content(result['raw_content'])
#             format_result['path']=result['path']
#             formatted_results.append(format_result)
#         return formatted_results
    
def compute_cosine_similarity(key, doc_content):
    # 创建 TfidfVectorizer 实例
    vectorizer = TfidfVectorizer()

    all_texts = [key,doc_content]

    # 使用 fit_transform 对所有文本进行合并训练
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # 计算查询文本与文档内容的余弦相似度
    cos_sim = cosine_similarity(tfidf_matrix[0,:], tfidf_matrix[1,:])

    # 返回余弦相似度
    return cos_sim[0][0]

def update_weights(interest_keywords, results, weights):
    for key in interest_keywords:
        for i in range(len(results)):
            doc_content = results[i]['content']
            cos = compute_cosine_similarity(key, doc_content)
            
            # 更新权重（如果文档已存在，加上新的相似度值，否则初始化为相似度值）
            if results[i]['path'] in weights:
                weights[results[i]['path']] += cos
            else:
                weights[results[i]['path']] = cos
                
    return weights

# 个性化搜索
def personalized_search(conn,query_str,user_id,limit=None):
    with ix.searcher(weighting=scoring.TF_IDF()) as searcher:#加权策略：TF-IDF
        query = QueryParser("content", ix.schema).parse(query_str)# 解析查询
        results = searcher.search(query, limit=None)#执行查询

        if len(results)==0:
            return []

        # 初始排序：先按相关性排序，再按PageRank排序
        sorted_results = sorted(results, key=lambda r: (r.score, pagerank.get(r['path'], 0)), reverse=True)
        #格式化
        formatted_results = []
        for result in sorted_results:
            format_result={}
            format_result['title']=unquote(result['title'])
            format_result['content']=clean_content(result['content'])
            format_result['raw_content']=clean_content(result['raw_content'])
            format_result['path']=result['path']
            formatted_results.append(format_result)

        # 获取用户兴趣
        interest1 = conn.execute("""SELECT interest1 FROM users WHERE id = ?""", (user_id,)).fetchall()
        interest2 = conn.execute("""SELECT interest2 FROM users WHERE id = ?""", (user_id,)).fetchall()
        interest3 = conn.execute("""SELECT interest3 FROM users WHERE id = ?""", (user_id,)).fetchall()
        interest_keywords = [interest1[0][0],interest2[0][0],interest3[0][0]]
        print("interest_keywords:",interest_keywords)
            
            
        resorted_length = min(50,len(results))
            
        #个性化排序：计算与兴趣词的余弦相似度
        weights={}
        weights=update_weights(interest_keywords, formatted_results[:resorted_length], weights)

        # 结合查询score与兴趣，综合加权,重新排序
        max_score = sorted_results[0].score
        min_score = sorted_results[resorted_length-1].score
        base = max_score-min_score
            
        for i in range(resorted_length):
            score= (sorted_results[i].score-min_score)/base
            weights[formatted_results[i]['path']]=weights[formatted_results[i]['path']]*0.2+score*0.8*3
        final_results = sorted(formatted_results[:resorted_length], key=lambda x: weights[x['path']], reverse=True)
        if len(sorted_results)>50:
            final_results.extend(formatted_results[resorted_length:])

        return final_results
    
