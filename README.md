
## Main Features

- Oauth with Github, Google, Facebook
- Website Scraping (devto, spiderum and maybe more)
- Post recommendations with BERT and Consine Similarity
- Background task with Celery and Redis cache system



## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`SQLALCHEMY_DATABASE_URI`
`SQLALCHEMY_DATABASE_URI_TEST`
`GOOGLE_CLIENT_ID`
`GOOGLE_CLIENT_SECRET`
`GITHUB_CLIENT_ID`
`GITHUB_REDIRECT_URI`
`FACEBOOK_CLIENT_ID`
`CELERY_BROKER_URL`
`CELERY_RESULT_BACKEND`



## hehe

**Flask** 

**Database:** Sqlite, MongoDB


## First look

This ugly interface:
<img width="1427" alt="Screenshot 2024-08-31 at 11 58 51" src="https://github.com/user-attachments/assets/44f59eb0-43dd-420a-b7a0-ed2ada5ebc77">


## Consine Similarity

Load models and preprocessing

```python
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased', clean_up_tokenization_spaces=True)
model = DistilBertModel.from_pretrained('distilbert-base-uncased')

@cache.cached(timeout=300)
def get_articles_embeddings() -> list:
    articles = Article.query.all()
    article_embeddings = [embed_text(article.title) for article in articles]
    return article_embeddings

def embed_text(text: str):
    inputs = tokenizer(text, return_tensors ='pt', max_length=512, truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze()
```

Post recommends:
```python
def get_recommendations_with_bert(user_history_indices: list):
    """
        Get recommendation articles with BERT
    """
    articles = Article.query.all()
    
    # Embedded tất cả title  của mỗi articles sang dạng vector, sau đó lưu vào list
    article_embeddings = get_articles_embeddings()
    
    #Embeded tất cả các title của mỗi artiles có trong lịch sử người xem
    user_embeddings = [article_embeddings[i] for i in user_history_indices]
    
    # Tính toán giá trị trung bình của tất cả vector trong user_embedding
    mean_user_embeddings = torch.mean(torch.stack(user_embeddings), dim = 0)
    
    sim_scores = cosine_similarity(
        [mean_user_embeddings.numpy()],
        [embedding.numpy() for embedding in article_embeddings]
    ).flatten()
    
    recommend_indices = np.argsort(sim_scores)[::-1]
    recommend_indices = [i for i in recommend_indices if i not in user_history_indices]
    recommend_articles = [articles[i] for i in recommend_indices]
    
    return recommend_articles
```
