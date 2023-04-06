import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import KeyedVectors

EMBEDDING_FILE = 'GoogleNews-vectors-negative300.bin.gz' # from above
word2vec = KeyedVectors.load_word2vec_format(EMBEDDING_FILE, binary=True)

model = word2vec

def get_sentence_embedding(sentence):
    # Split the sentence into individual words
    words = sentence.lower().split()
    # Get the Word2Vec embeddings for each word in the sentence
    embeddings = []
    for word in words:
        if word in model:
            embeddings.append(model[word])
    # Compute the average of the Word2Vec embeddings for the sentence
    if embeddings:
        sentence_embedding = sum(embeddings) / len(embeddings)
    else:
        sentence_embedding = np.zeros(300) # Use a zero vector if no embeddings are found
    return sentence_embedding

#Testing word2vec SVC
custom_review = "wonderful product"
word_embed = get_sentence_embedding(custom_review)
loaded_model_svcwv = joblib.load("./word2vec_SVC.joblib")
result_svcwv = loaded_model_svcwv.predict(word_embed.reshape(1,-1))
print('Result from SVC with word2vec word embedding: ',result_svcwv)

#Testing word2vec MultinomialNB
scaler = MinMaxScaler()
word_embed = get_sentence_embedding(custom_review)
scaler.fit_transform(word_embed.reshape(1,-1))
word_embed_scaler = scaler.transform(word_embed.reshape(1,-1))
loaded_model_MultiNB_wv = joblib.load("./word2vec_multinomialNB.joblib")
result_MultiNB_wv = loaded_model_MultiNB_wv.predict(word_embed_scaler.reshape(1,-1))
print('Result from MultinomialNB with word2vec word embedding: ',result_MultiNB_wv)

#Testing TF-IDF SVC
vectorizer= TfidfVectorizer()
tfidfvectorizer_svc = joblib.load("./tf-idf_vectoriser.joblib")
tf_idf_vector = tfidfvectorizer_svc.transform([custom_review])
loaded_model_svctfidf = joblib.load("./tf-idf_svc.joblib")
result_svctfidf = loaded_model_svctfidf.predict(tf_idf_vector.reshape(1,-1))
print('Result from SVC with TF-IDF word embedding: ',result_svctfidf)

#Testing TF-IDF MultinomialNB
tfidfvectorizer_mulNB = joblib.load("./tf-idf_vectoriser.joblib")
tf_idf_vector = tfidfvectorizer_mulNB.transform([custom_review])
loaded_model = joblib.load("./tf-idf_multinomialNB.joblib")
result_multiNBtfidf = loaded_model.predict(tf_idf_vector.reshape(1,-1))
print('Result from SVC with TF-IDF word embedding: ',result_multiNBtfidf)