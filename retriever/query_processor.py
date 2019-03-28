import sqlite3
import numpy as np
import pyinotify
import code
from drqa import retriever
from drqa import pipeline
from drqa.retriever import utils

database_path = './rough/DrQA/data/wikipedia/'
conn = sqlite3.connect(database_path+'docs.db')
cursor = conn.cursor()
print("setting up DrQA")
DrQA = pipeline.DrQA(
	cuda=True,
	fixed_candidates=None,
	reader_model=None,
	ranker_config={'options': {'tfidf_path': '/docs-tfidf-ngram=2-hash=16777216-tokenizer=simple.npz'}},
	db_config={'options': {'db_path': database_path + 'docs.db'}},
	tokenizer=None)
#ranker = retriever.get_class('tfidf')(tfidf_path='/docs-tfidf-ngram=2-hash=16777216-tokenizer=simple.npz')
print('ranker loaded')

def get_docs(query, k=1):
	doc_id, doc_score = ranker.closest_docs(query, k)
	for i in range(len(doc_score)):
		print(str(doc_id[i])+' '+ str(doc_score))
	return doc_id

def trim_docs(doc_list, query):
	paras = []
	for doc in doc_list:
		paras.extend((doc[0]).split('\n'))

	return paras

def process_query():
	while True:
		print(">>>>", end=' ')
		query= input()
		if query=='exit':
			break
		doc_ids = get_docs(query, 1)
		doc_list = []
		for doc_id in doc_ids:
			cursor.execute('SELECT text FROM documents WHERE id="'+str(doc_id)+'"')
			doc_list.append(cursor.fetchone())
			#print(doc_list)
			print('main\n')

		paras = trim_docs(doc_list, query)
		paras = [para for para in paras if para.strip() != '']
		#closest_para = get_closest_para(paras, query)
		#print(closest_para)
		query_vec = ranker.text2spvec(query)
		#query_vec = query_vec.toarray()[0]
		para_matrix = []
		for para in paras:
			para_vec = ranker.text2spvec(para)
			#para_vec = para_vec.toarray()[0]
			res = para_vec.multiply( query_vec)
			if len(res.data)>0:
				para_matrix.append((np.sum(res.data)))
			else:
				para_matrix.append(0)
		print("final printing")
		index = np.argsort(np.array(para_matrix))[-1]
		print(index)
		print('printing closest_para')
		print(paras[index])

def get_closest_para(question, candidates=None, top_n=1, n_docs=5):
	
	predictions = DrQA.process(question, candidates, top_n, n_docs, return_context=True)
	print('\nContexts:')
	for p in predictions:
	    text = p['context']['text']
	    start = p['context']['start']
	    end = p['context']['end']
	    output = (text[:start] +
	              text[start: end] +
	              text[end:])
	    print('[ Doc = %s ]' % p['doc_id'])
	    print(output + '\n')

	return output


if __name__ == '__main__':
	#process_query
	#while True:
	#	print(">>>>", end=' ')
	#	query= input()
	#	if query=='exit':
	#		break
	#	get_closest_para(query)
	wm = pyinotify.WatchManager()

	mask =pyinotify.IN_CREATE  # watched events

	class EventHandler(pyinotify.ProcessEvent):
	    def process_IN_CREATE(self, event):
	        print ("Creating:", event.pathname)
	        with open(event.pathname, 'r') as queryfile:
	        	query = queryfile.readline()
	        with open(event.pathname, 'w') as queryfile:
	        	queryfile.write(get_closest_para(query))

	print("startingloop")
	handler = EventHandler()
	notifier = pyinotify.Notifier(wm, handler)
	wdd = wm.add_watch('questions', mask, rec=True)
	notifier.loop()