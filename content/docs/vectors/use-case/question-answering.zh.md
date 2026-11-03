---
title: "生成式问答（Generative QA）"
linkTitle: "生成式问答"
description: "向量搜索可用于为 OpenAI GPT 系列等生成式模型提供上下文，从而提升输出质量。"
weight: 60
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/use-case/question-answering.md"
math: true
aliases:
  - "/use-case/question-answering/"
icon: fa-solid fa-comments
---

向量搜索还可以用于为生成式模型（例如 OpenAI 的 GPT 系列）提供上下文，从而提升模型输出的质量。

本文将探讨如何使用 `pgvecto.rs` 构建向量知识库并从中检索信息，以增强生成式模型在问答（Question-Answering, QA）任务中的表现。知识库充当了生成式模型的“长期记忆”，为其提供持久化、经过整理且准确的信息作为**上下文（Context）**，供模型在生成问题答案时参考。这样不仅能生成更准确的回答，减少模型产生“幻觉”（毫无事实依据的陈述）的可能性，还能增强用户对输出结果的信任。这项技术被称为检索增强生成（Retrieval-Augmented Generation，简称 RAG）：更多信息请参阅[这篇博文](https://ai.meta.com/blog/retrieval-augmented-generation-streamlining-the-creation-of-intelligent-natural-language-processing-models/)或[相关论文](https://arxiv.org/abs/2005.11401v4)。

## 问答任务概览 {#overview-of-the-question-answering-task}
生成式模型的问答（QA）任务是一种**信息检索（Information Retrieval）**方法。模型接收一个问题，并根据给定的上下文（通常是模型可以查阅以获取回答问题所需信息的文档或其他信息源）生成答案。

在本案例中，我们将使用 Hugging Face 上的 [vishnupriyavr/wiki-movie-plots-with-summaries-faiss-embeddings](https://huggingface.co/datasets/vishnupriyavr/wiki-movie-plots-with-summaries-faiss-embeddings) 数据集，为 OpenAI 的 `gpt-3.5-turbo-instruct` 模型提供上下文，以回答有关电影的问题。

整体工作流程如下所示：
![](/pgvecto-rs/use-case/question-answering/diagram_v3.png)

## 无上下文的问答 {#question-answering-without-context}
首先，让我们尝试在不提供任何上下文的情况下让模型回答几个问题。

我们先定义一个函数，用于简化向模型发送提示词（Prompt）并获取响应的过程：
```python
# pip install openai

import openai

openai.api_key = "YOUR_API_KEY_HERE"
def complete(prompt):
    result = openai.Completion.create(
        engine='gpt-3.5-turbo-instruct',
        prompt=prompt,
        temperature=0,
        max_tokens=400,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    return result['choices'][0]['text'].strip()

```
> [!NOTE]
> 获取 `api_key` 需要拥有 OpenAI 账号。登录后，可从右上角下拉菜单中申请 API 密钥，并将其粘贴替换代码中的 `YOUR_API_KEY_HERE`。


让我们先提问一部知名度较高的电影：
```python
base_prompt = "What is the release year and overall plot of Skyfall?"
print(complete(base_prompt))
```
> [!TIP] 输出：
> The release year of Skyfall is 2012. The overall plot follows James Bond as he investigates an attack on MI6 and uncovers a sinister plot by a former agent seeking revenge on M and the entire agency. Bond must confront his past and protect MI6 from destruction.


回答相当准确，尽管剧情简介略微笼统。但是，如果换作一部知名度低得多的电影呢？
```python
base_prompt_2 = "What is the release year and overall plot of Cat Napping?"
print(complete(base_prompt_2))
```
> [!TIP] 输出：
> The release year of Cat Napping is unknown. The overall plot of Cat Napping is about a group of cats who go on a mission to rescue their friend who has been kidnapped by a group of evil dogs. Along the way, they encounter various challenges and obstacles, but with their cleverness and teamwork, they are able to save their friend and defeat the dogs.

> [!DETAILS] 正确答案：
> 《Cat Napping》（猫咪午睡）实际上是 1951 年上映的一部《猫和老鼠》（Tom and Jerry）动画短片，讲述了汤姆和杰瑞争夺一张吊床的故事。

我们已经触及了模型自身“知识”的边界：它无法给出上映年份，并且仅凭片名编造了一段剧情。接下来，我们将通过构建一个供模型检索的知识库来解决这一问题。

要让模型更好地回答我们的问题，通常有两种选择：
1. 使用目标领域的文本数据（本例中为电影数据）对模型进行微调（Fine-tune）。
2. 采用**检索增强生成（RAG）**，在流程中引入信息检索组件。这使我们能够检索相关信息并将其作为辅助信息源输入给模型。

在本文中，我们将采用第二种方案。

## 构建知识库 {#building-the-knowledge-base}
让我们使用 Hugging Face 上的 [vishnupriyavr/wiki-movie-plots-with-summaries-faiss-embeddings](https://huggingface.co/datasets/vishnupriyavr/wiki-movie-plots-with-summaries-faiss-embeddings) 数据集构建一个电影知识库，以便从中检索相关信息。该数据集包含 33,155 部电影的片名、上映年份、演员阵容、维基百科页面、剧情简介/长度，以及这些信息的向量嵌入（Vector Embeddings）。每部电影还包含一个综合了片名、上映年份、演员阵容和剧情简介的 `text` 字段。在本应用中，我们将使用其中的 `text` 和 `embeddings` 数据。

### 加载数据 {#load-the-data}

首先加载数据集：
```python
# pip install -U datasets
from datasets import load_dataset
dataset = load_dataset("vishnupriyavr/wiki-movie-plots-with-summaries-faiss-embeddings", split='train')

texts = dataset['train']['text']
# texts[0]
# 'Alice in Wonderland \n  starring May Clark \n  released in the year1903 \n  with the following plot  \n Alice follows a large white rabbit down a "Rabbit-hole". She finds a tiny door. When she finds a bottle labeled "Drink me", she does, and shrinks, but not enough to pass through the door. She then eats something labeled "Eat me" and grows larger. She finds a fan when enables her to shrink enough to get into the "Garden" and try to get a "Dog" to play with her. She enters the "White Rabbit\'s tiny House," but suddenly resumes her normal size. In order to get out, she has to use the "magic fan."\r\nShe enters a kitchen, in which there is a cook and a woman holding a baby. She persuades the woman to give her the child and takes the infant outside after the cook starts throwing things around. The baby then turns into a pig and squirms out of her grip. "The Duchess\'s Cheshire Cat" appears and disappears a couple of times to Alice and directs her to the Mad Hatter\'s "Mad Tea-Party." After a while, she leaves.\r\nThe Queen invites Alice to join the "ROYAL PROCESSION": a parade of marching playing cards and others headed by the White Rabbit. When Alice "unintentionally offends the Queen", the latter summons the "Executioner". Alice "boxes the ears", then flees when all the playing cards come for her. Then she wakes up and realizes it was all a dream.'
```

### 生成向量嵌入 {#generate-embeddings}

由于该数据集自带了向量嵌入，您可以跳过生成步骤，直接使用现成的嵌入数据：

```python
embeddings = dataset['train']['embeddings']
```

如果您希望从文本数据生成向量嵌入，可以使用 OpenAI、Cohere 或其他嵌入 API。下面我们提供一个使用 Cohere API 的示例（您可以在[此处](https://dashboard.cohere.com/api-keys)获取 Cohere API 密钥）：
```python
# pip install cohere
import getpass
import os
import cohere

if not os.getenv("COHERE_API_KEY"):
    os.environ["COHERE_API_KEY"] = getpass.getpass("Enter your Cohere API key: ")

co = cohere.Client()
# 嵌入模型可参考此文档：https://docs.cohere.com/docs/cohere-embed
embed = co.embed(
    texts=texts,
    input_type="search_query",
    model="embed-english-v3.0"
)
embeddings = embed.embeddings
```

> [!NOTE]
> 本案例中的嵌入为稠密向量（Dense Vectors）。如需创建稀疏向量（Sparse Vectors），请参阅[稀疏向量章节](/zh/docs/vectors/use-case/sparse-vector/#how-to-create-a-vector-embedding)。


### 将数据插入数据库 {#insert-data-into-the-database}

向量存储与检索需要部署一个 `pgvecto.rs` 实例。我们可以使用官方的 `pgvecto-rs` Docker 镜像：

```bash
docker run \
  --name pgvecto-rs-demo \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  -d tensorchord/pgvecto-rs:pg16-v0.3.0
```
安装用于与 Postgres 交互的 `psycopg` 库，并确保扩展已启用：
```python
#pip install "psycopg[binary,pool]"
import psycopg

URL = "postgresql://postgres:mysecretpassword@localhost:5432/postgres"
# 启用扩展
with psycopg.connect(URL) as conn:
    conn.execute("DROP EXTENSION IF EXISTS vectors;")
    conn.execute("CREATE EXTENSION vectors;")
```

现在，我们创建一张名为 `movies` 的表，包含三个列：ID 列（`id`）、文本列（`text`）和向量列（`embedding`）。
```python
import psycopg
URL = "postgresql://postgres:mysecretpassword@localhost:5432/postgres"

# 创建表
with psycopg.connect(URL) as conn:
    conn.execute("DROP TABLE IF EXISTS movies;")
    conn.execute(f"""
        CREATE TABLE movies (
            id SERIAL PRIMARY KEY, 
            text TEXT NOT NULL,
            embedding vector(768) NOT NULL);
    """
    )
```
> [!NOTE]
> 由于我们处理的是稠密向量嵌入，因此使用 `vector(n)` 类型，其中 `n` 是每个嵌入向量的维度（本例中为 768）。


表创建完成后，我们可以将数据集中的嵌入插入表中：
```python
# 可选安装，但推荐使用以显示进度条：
# pip install tqdm
import psycopg
from tqdm import tqdm
URL = "postgresql://postgres:mysecretpassword@localhost:5432/postgres"

# 插入数据到表中
with psycopg.connect(URL) as conn:
    with conn.cursor() as cursor:    
        for text, embedding in tqdm(zip(texts, embeddings), total=len(texts)):
            cursor.execute(
                """INSERT INTO movies (text, embedding) 
                    VALUES (%s, %s::real[]);""",
                (text, embedding),
            )
        conn.commit()
```
> [!WARNING]
> 根据待插入数据量的大小，此过程可能需要花费一些时间。


### 创建索引 {#create-index}

```python
import psycopg
URL = "postgresql://postgres:mysecretpassword@localhost:5432/postgres"

# 为 embedding 列创建索引
with psycopg.connect(URL) as conn:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE INDEX ON movies 
        USING vectors (embedding vector_l2_ops) 
        WITH (options = \"[indexing.hnsw]\");
    """)
    conn.commit()
```
> [!NOTE]
> 回顾一下，对于稠密向量，`vector_l2_ops` 计算的是平方欧氏距离（Squared Euclidean distance），这也是最常用的距离度量方式：
>
> $$
> D_{L2} = \Sigma (x_i - y_i) ^ 2
> $$


## 结合上下文的问答 {#question-answering-with-context}
为了利用我们的知识库，首先需要对查询语句进行编码，以确定应当检索哪些文本：
```python
# pip install sentence-transformers

from sentence_transformers import SentenceTransformer

# 可选模型：'paraphrase-mpnet-base-v2', 'all-mpnet-base-v2'
encoder = SentenceTransformer('all-mpnet-base-v2')

def encode_query(query): # query 为字符串
    # 预处理查询语句
    query = query.lower()
    query = query.split()
    query = [word for word in query]
    query = ' '.join(query)
    
    # 对查询进行编码
    vector = encoder.encode(query)
    return vector
```

接下来，我们定义一个函数，自动将检索到的上下文拼接到初始提示词中：
```python
import psycopg
URL = "postgresql://postgres:mysecretpassword@localhost:5432/postgres"

def add_context(prompt):
    search_vector = encode_query(prompt).tolist()
    # 构造包含检索上下文的提示词
    prompt_start = (
        "Answer the question based on the following context:\n\n"
    )
    prompt_end = (
        f"\n\nQuestion: {prompt}\nAnswer:"
    )
    with psycopg.connect(URL) as conn:
        cursor = conn.cursor()
        # 根据希望提供给模型的电影文本数量调整 LIMIT 值
        cursor.execute("SELECT text FROM movies ORDER BY embedding <-> %s::real[] LIMIT 3;", 
                  (search_vector,),)
        result = cursor.fetchall()
    context = ""
    for r in result:
        context += r[0] + "\n\n"
    return prompt_start + context + prompt_end
```
> [!NOTE]
> 回顾一下距离操作符的选项：
>
>  - `<->`：平方欧氏距离（Squared Euclidean distance）
>  - `<#>`：负点积（Negative dot product）
>  - `<=>`：余弦距离（Cosine distance）
>
> 有关详细定义，请参阅[概览](/zh/docs/vectors/getting-started/overview/#quick-start)。


现在，让我们附上检索到的上下文，再次尝试之前的提问：
```python
base_prompt_2 = "What is the release year and overall plot of Cat Napping?"

context_prompt_2 = add_context(base_prompt_2)
context_response_2 = complete(context_prompt_2)
print(context_response_2)
```
> [!TIP] 输出：
> The release year of Cat Napping is 1951 and the overall plot involves Tom and Jerry fighting over a hammock, with Jerry ultimately getting revenge on Tom.

现在模型给出了准确的回答！我们甚至可以针对细节进一步追问：
```python
base_prompt_3 = "In Cat Napping, what does Tom do to Jerry?"
print(complete(add_context(base_prompt_3)))
```
> [!TIP] 输出：
> Tom tries to send Jerry sliding into a nearby pond by unhooking the hammock he is sleeping in. He also tries to whack the hammock to send Jerry flying into the air, but Jerry lands in a bird's nest. Tom then picks Jerry up on a spatula and places him onto a walking army of ants, causing Jerry to wake up as he bumps his head on a sprinkler. Tom also tries to chase Jerry with a lawn mower and a baseball bat.


正如我们在前文中所看到的，大语言模型（LLM）本身虽然非常强大，但在面对冷门或特定领域的问题时往往力不从心，容易产生不易察觉的“幻觉”。引入向量知识库能够显著提升回答的事实准确性，进而增强用户对生成结果的信任。

## 更多应用场景 {#further-applications}
当然，这种方法不仅限于电影问答。其他应用场景还包括提取科学论文摘要（不妨试试[这个数据集](https://huggingface.co/datasets/MongoDB/subset_arxiv_papers_with_embeddings)！），或者基于企业内部文档库回答有关公司规章制度的问题。
