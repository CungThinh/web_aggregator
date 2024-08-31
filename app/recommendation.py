from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .models import Article
from transformers import DistilBertTokenizer, DistilBertModel
import torch
from . import cache

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
    

# def get_recommendations(user_history_indices: list):
#     """
#         Get recommendation articles with TfidVectorizer
#     """
#     articles = Article.query.all()
#     articles_title = [article.title for article in articles]    
    
#     # Ma trận TF-IDF
#     tfidf_vectorizer = TfidfVectorizer()
#     tfidf_matrix = tfidf_vectorizer.fit_transform(articles_title)
#     cosine_sim = cosine_similarity(tfidf_matrix)
    
#     sim_scores = np.mean(cosine_sim[user_history_indices], axis=0)

#     recommended_indices = np.argsort(sim_scores)[::-1]
#     recommended_indices = [i for i in recommended_indices if i not in user_history_indices]

#     recommended_articles = [articles[i] for i in recommended_indices]
    
#     return recommended_articles

    