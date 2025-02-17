import pickle
from ..utils.BuilderProcessor import TextProcessorBuilder

with open('/home/hwadmin/HareWareAssistant/app/ml_models/model_arc.pkl', 'rb') as f:
    clf, vectorizer = pickle.load(f)


def arc_predict(prompt):
    text_processor = TextProcessorBuilder().set_stem(False).set_remove_stopwords(False).build()
    texto_processado = text_processor.process(prompt)
    nova_entrada = vectorizer.transform([texto_processado]).toarray()
    predicao = clf.predict(nova_entrada)

    return predicao
