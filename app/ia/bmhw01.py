import math


class ScoreBM25():
    def __init__(self, termo_consulta=None, total_documentos=None, total_documento_termo=None,
                 total_termos_documento=None, total_tokens_documento=None, tf=None, idf=None):
        self.k1 = 1.5
        self.b = 0.75
        self.k3 = 1000
        self.termo_consulta = termo_consulta
        self.total_documentos = total_documentos
        self.total_documento_termo = total_documento_termo
        self.total_termos_documento = total_termos_documento
        self.total_tokens_documento = total_tokens_documento
        self.tf = tf
        self.idf = idf

    def inverse_term_frequency(self):
        return math.log((self.total_documentos - self.total_documento_termo + 0.5) / (self.total_documento_termo + 0.5) + 1.0)

    def term_frequency(self):
        avgdl = self.total_tokens_documento / self.total_documentos
        return (self.total_termos_documento * (self.k1 + 1)) / (self.total_termos_documento + self.k1 * (1 - self.b + self.b * (self.total_tokens_documento / avgdl)))

    def score(self):
        return self.idf * self.term_frequency() * (self.k3 + 1) / (self.term_frequency() + self.k3)
