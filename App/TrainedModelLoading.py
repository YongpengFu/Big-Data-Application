import string
import re
from nltk.corpus import stopwords
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import joblib
import nltk
import pathlib
from nltk import word_tokenize
from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from scipy.sparse import csr_matrix
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer


# https://stackoverflow.com/questions/36382937/nltk-doesnt-add-nltk-data-to-search-path
# https://stackoverflow.com/questions/3522372/how-to-config-nltk-data-directory-from-code

DATA_PATH = pathlib.Path(__file__).parent.joinpath("./trained_models").resolve()

nltk.data.path.append(DATA_PATH)
stop_words = stopwords.words('english')

# EMBEDDING_FILE = './trained_models/GoogleNews-vectors-negative300.bin.gz'  # from above
# word2vec = KeyedVectors.load_word2vec_format(EMBEDDING_FILE, binary=True)
# model = word2vec


# Load a model
sia = SentimentIntensityAnalyzer()
# This is from Yong
NaiveBayesClassifier = joblib.load(
    DATA_PATH.joinpath("NaiveBayesClassifier.joblib"))
# The following four are from Sneha
tf_idf_vectoriser = joblib.load(DATA_PATH.joinpath("tf-idf_vectoriser.joblib"))
MultinomialNBTFIDF = joblib.load(DATA_PATH.joinpath("tf-idf_multinomialNB.joblib"))
SVCwithTFIDF = joblib.load(DATA_PATH.joinpath("tf-idf_svc.joblib"))
# The following two are from Stu:
MultinomialNBCountVector = joblib.load(DATA_PATH.joinpath("MultinomialNB_Model.joblib"))
MLPCountVector = joblib.load(DATA_PATH.joinpath("MLP_Model.joblib"))

# Get the sentiment result

# 1: VADER result
def sia_result(review):
    score = sia.polarity_scores(str(review))['compound']
    if score <= -0.05:
        return "Negative"
    elif score >= 0.05:
        return "Positive"
    else:
        return "Neutral"

# 2: NLTK Naive bayes:


def remove_noise(review_tokens, stopwords=()):
    cleaned_tokens = []

    for token, tag in pos_tag(review_tokens):
        # remove link
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', token)
        # remove any @text
        token = re.sub("(@[A-Za-z0-9_]+)", "", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        lemmatizer = WordNetLemmatizer()
        token = lemmatizer.lemmatize(token, pos)
        # If we still have string left
        if len(token) > 0 and token not in string.punctuation and token.lower() not in stopwords:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens

# Clean the reviews
def NaiveBayesClassifier_clean(review):
    custom_tokens = remove_noise(word_tokenize(review), stop_words)
    return dict([token, True] for token in custom_tokens)


def NaiveBayesClassifier_result(review):
    return NaiveBayesClassifier.classify(NaiveBayesClassifier_clean(review))

# 3: MultinomialNBCountVector


def pull_training(link):
    train1 = pd.read_csv(link)
    train1['tokenized'] = train1['tokenized'].apply(
        lambda x: x.replace("'", ""))
    train1["Review Body wop"] = train1['Review Body'].str.replace(
        '[^\w\s]', '', regex=True)
    train1['Review Body token'] = train1['Review Body'].apply(
        lambda x: ' '.join([word for word in x.split() if word not in (stop_words)]))
    train1['tokenized'] = [nltk.word_tokenize(
        sentence) for sentence in train1['Review Body token']]
    return train1

train1 = pull_training(DATA_PATH.joinpath("train_MNB.csv"))

def MultinomialNBCountVector_result(review):
    review_wo = review.replace('[^\w\s]', '')
    review_wo = word_tokenize(review_wo)
    review_wo_sw = []
    for word in review_wo:
        if word not in (stop_words):
            review_wo_sw.append(word)

    x_train = train1['tokenized'].values.tolist()

    # Join the list of sentences into a single string using a space separator
    x_train = [" ".join(sentences) for sentences in x_train]

    # Vectorize the training data
    vectorizer = CountVectorizer()
    vectorizer.fit_transform(x_train)

    # Convert sample sentence to vector
    sentence = ' '.join(review_wo_sw)  # join words in list
    review_vec = vectorizer.transform([sentence])

    # Convert sparse matrix to CSR format
    x_sample_vec = csr_matrix(review_vec)

    result = MultinomialNBCountVector .predict(x_sample_vec)
    return result


# 4: MLPCountVector
train2 = pull_training(DATA_PATH.joinpath("train_mlp.csv"))

def MLPCountVector_result(review):
    ''' 
    This is the tricky part. The vectorizer for the new sample needs to be trained on
    the same data that was originally used to build the model.

    For this reason, I have pulled the train['tokenized'] values out as a csv, that way
    if for some reason something happens to the train data (ie opening the notebook in a new 
    computer) the whole model doesnt need to be run again. 
    '''

    x_train = train2['tokenized'].values.tolist()

    # Fit the TfidfVectorizer to the training data
    vectorizer = CountVectorizer()
    x_train_str = [' '.join(text) for text in x_train]
    vectorizer.fit_transform(x_train_str)

    review = review.replace('[^\w\s]', '')
    tokenized = nltk.word_tokenize(review)

    without_stopwords = []
    for item in tokenized:
        if item not in stop_words:
            without_stopwords.append(item)

    # Vectorize the training data
    vectorizer = CountVectorizer()
    x_train_str = [' '.join(text) for text in x_train]
    vectorizer.fit_transform(x_train_str)

    # Convert sample sentence to vector
    sentence = ' '.join(without_stopwords)  # join words in list
    review_vec = vectorizer.transform([sentence])

    # Convert sparse matrix to CSR format
    x_sample_vec = csr_matrix(review_vec)

    result = MLPCountVector.predict(x_sample_vec)
    return result.astype(str)


# 5: TF-IDF SVC
def MultinomialNBTFIDF_result(review):
    tf_idf_vector = tf_idf_vectoriser.transform([review])
    result_multiNBtfidf = MultinomialNBTFIDF.predict(
        tf_idf_vector.reshape(1, -1))
    return result_multiNBtfidf


def SVCwithTFIDF_result(review):
    tf_idf_vector = tf_idf_vectoriser.transform([review])
    result_svctfidf = SVCwithTFIDF.predict(
        tf_idf_vector.reshape(1, -1))
    return result_svctfidf
