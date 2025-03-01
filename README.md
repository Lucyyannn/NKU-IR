**本仓库记录了《信息检索系统原理》课程重点作业和课程设计。**

## experiment
本实验基于斯坦福大学CS276/LING286课程代码框架，主要实现了BSBI算法的倒排索引构建、索引压缩、布尔检索等。

## paper
顶会论文精读：一篇解决组合时尚图像检索中多模态不平衡问题的文章。
附一篇本人idea的功能技术文档，主要想法是借助强化学习技术实现组合图像检索的多轮优化。

## SearchEngine
实现了一个较为完整的小型搜索引擎，关键技术：
- 数据源构建：10W+网页爬取
- 借助 Whoosh 构建索引，借助 networkx 连接分析
- 基于向量空间模型实现文档查询、短语查询、通配查询、查询日志、网页快照等服务
- 个性化推荐与个性化检索
- 网站搭建：借助flask开发者模式，支持四个主要页面
