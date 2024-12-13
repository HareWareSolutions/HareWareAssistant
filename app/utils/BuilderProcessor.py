
from app.utils.TemplateProcessor import TextProcessor


class TextProcessorBuilder:
    def __init__(self):
        self._remove_stopwords = True
        self._lowercase = True
        self._remove_punctuation = True
        self._stem = True

    def set_remove_stopwords(self, remove_stopwords: bool):
        self._remove_stopwords = remove_stopwords
        return self

    def set_lowercase(self, lowercase: bool):
        self._lowercase = lowercase
        return self

    def set_remove_punctuation(self, remove_punctuation: bool):
        self._remove_punctuation = remove_punctuation
        return self

    def set_stem(self, stem: bool):
        self._stem = stem
        return self

    def build(self):
        return TextProcessor(self._remove_stopwords, self._lowercase, self._remove_punctuation, self._stem)
