import nltk
import string
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer
from nltk.tokenize import word_tokenize

nltk.download('all')


class TextProcessor:
    def __init__(self, remove_stopwords, lowercase, remove_punctuation, stem):
        self._remove_stopwords = remove_stopwords
        self._lowercase = lowercase
        self._remove_punctuation = remove_punctuation
        self._stem = stem
        self._stopwords = set(stopwords.words('portuguese'))
        self._stemmer = RSLPStemmer()

    def process(self, text: str) -> str:
        if self._lowercase:
            text = self.lowercase(text)
        if self._remove_punctuation:
            text = self.remove_punctuation(text)
        if self._remove_stopwords:
            text = self.remove_stopwords(text)
        if self._stem:
            text = self.stem(text)
        return text

    def lowercase(self, text: str) -> str:
        return text.lower()

    def remove_punctuation(self, text: str) -> str:
        return text.translate(str.maketrans('', '', string.punctuation))

    def remove_stopwords(self, text: str) -> str:
        words = word_tokenize(text)
        filtered_words = [word for word in words if word.lower() not in self._stopwords]
        return ' '.join(filtered_words)

    def stem(self, text: str) -> str:
        text = [self._stemmer.stem(word) for word in text]
        return ' '.join(text)
