import pandas as pd
import sys
import re
import spacy
from spacy.tokens import DocBin
from spacy.util import filter_spans

nlp = spacy.blank('en')

def find_substrings(sentence, words, doc_bin):

	if (type(words) == str):
		wordslst = words.split("\n")
		wordidx = 0
	else:
		#print(sentence, type(words))
		exit()
	
	ents = []
	doc = nlp.make_doc(sentence)
	
	while wordidx < len(wordslst):
		word = wordslst[wordidx]
		label = word.find("[") - 1
		substring = word[:label]
		freq = wordslst.count(word)

		if freq > 1:
			count = 0
			for i in re.finditer(substring, sentence):
				count+= 1
				span = doc.char_span(i.start(), i.end(), label=word[label+2:-1], alignment_mode="contract")
				
				if span is not None:
					ents.append(span)
				else:
    					print(f"Warning: Failed to create span for '{substring}' at position {i.start()}–{i.end()}")
				
				#ents.append(span)
				#print(f"{word[:label]}: {i.start()}, {i.end()},{word[label:]}")
			if (freq > count):
				print(f"{substring} only occurs {count} time(s)") 
			wordslst = [i for i in wordslst if i != word]
	
		else:
			start = sentence.find(substring)
			end = len(substring)+start
			
			if start == -1:
				print(f"Substring {word[:label]} not in sentence")
			else:
				span = doc.char_span(start, end, label=word[label+2:-1], alignment_mode="contract")
				if span is not None:
					ents.append(span)
				else:
					print(f"Warning: Failed to create span for '{substring}' at position {start}-{end}")
			wordidx += 1
	
	filtered_ents = filter_spans(ents)
	doc.ents = filtered_ents
	doc_bin.add(doc)
	return doc

def printDoc(db):
	docs = list(db.get_docs(nlp.vocab))
	
	print([doc.to_json() for doc in docs])
	
if __name__ == "__main__":
	df = pd.read_csv(sys.argv[1])

	doc_bin = DocBin()
	df['locations'] = df.apply(lambda row: find_substrings(row['sentence'][3:], row['words'], doc_bin), axis=1)

	#printDoc(doc_bin)
	
	doc_bin.to_disk(sys.argv[2])
