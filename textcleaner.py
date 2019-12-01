# import html
from bs4 import BeautifulSoup
import subprocess
import re
import sys
from collections import OrderedDict

if len(sys.argv) != 2:
	print("usage: python3.6 textcleaner.py <file>")#" <page for table of contents>")
	exit()

FILE = sys.argv[1]

pdf2text_proc = subprocess.Popen("which pdf2txt.py", shell=True, stdout=subprocess.PIPE)

pdf2text = pdf2text_proc.communicate()[0].strip().decode("utf-8")
print("location of pdf2txt:", pdf2text)

page_no = 1#10#3
LOAD = False	#debugging purposes
pageText = []
while True:
	if not LOAD:
		command = " ".join(['python3.6', pdf2text, '-p', str(page_no), '-t', 'html', FILE])
		print(command)
		print()
		output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).communicate()[0].decode("utf-8")

		if len(output) == 0:
			break
		else:
			page_no += 1

		with open("test.html", "w") as f:
			f.write(output)
	else:
		output = ""
		with open("test.html", "r") as f:
			for l in f:
				output += l

	parser = BeautifulSoup(output, "html.parser")

	textStruct = parser.body.find_all("div")
	text = []

	pageTop = re.compile("^[pP]age [0-9]+$")
	pageBot = re.compile("^[pP]age:")
	nonText = re.compile("^[^\w]+$")

	for c in textStruct:	#div level
		# print(c)
		# print("-----------------------------------------")
		#check if no inner tags
		if (len(c.contents) == 0):
			continue
		toAdd = OrderedDict()
		add = True
		for d in c:	#span level
			if not hasattr(d, "stripped_strings"):	#no data
				add = False
				break
			for s in d.stripped_strings:
				#check if page regex matches
				if pageTop.match(s) or pageBot.match(s):
					add = False
					break
				#check if non text
				if nonText.match(s):
					continue
				#now we have text; check style
				style = d["style"]
				if style in toAdd:
					if len(toAdd) == 1:	#only one style so far
						toAdd[style] += " " + s
					elif list(toAdd.keys()).index(style) == len(toAdd) - 1:	#style is same as prev
						toAdd[style] += " " + s
					else:	#some weird formatting, so merge previous indices
						keyList = list(toAdd.keys())
						i = keyList.index(style)
						for a in range(i + 1, len(toAdd)):
							toAdd[style] += " " + toAdd[keyList[a]]
							toAdd.pop(keyList[a])
						toAdd[style] += " " + s
				else:
					toAdd[style] = s
			if not add:
				break
		if not add:
			continue
		if len(toAdd) > 0:
			text.append(toAdd)
	# 	print(toAdd)
	# 	print()
	# print("++++++++++++++++++++++++++++++++++++++++++++++++++")

	#now merge sections
	#if we want a new line, add it here
	finalText = []
	for i in text:
		if len(finalText) == 0:
			for k in i:
				finalText.append({k: i[k]})
			continue

		#compare current text section to previous text: if same text style then merge
		lastKey = list(finalText[-1].keys())[0]
		newKeyList = list(i.keys())
		if lastKey == newKeyList[0]:
			finalText[-1][lastKey] += " " + i[newKeyList[0]]
			#add remaining
			for k in newKeyList:
				if k == newKeyList[0]:
					continue
				finalText.append({k: i[k]})
		else:	#add new sections
			for k in i:
				finalText.append({k: i[k]})
			continue

	pageText.append(finalText)
	'''
	for c in textStruct:
		print(c)
		print("------------------------------------")
		toAdd = OrderedDict()
		add = True
		print(len(c.contents))
		for d in c.contents:
			print(d, "\n", type(d))
			# if pageTop.match()
		print('++++++++++++++++++++++++++++++++++++')
		print()

	def depth(soup):
	    if hasattr(soup, "contents") and soup.contents:
	        return max([depth(child) for child in soup.contents]) + 1
	    else:
	        return 0

	maxDepth = 0
	maxStruct = None
	for c in textStruct:
		d = depth(c)
		if d > maxDepth:
			maxDepth = d
			maxStruct = c
	print("max depth:", maxDepth)
	# print(maxStruct)
	#trying to merge br tags
	for s in maxStruct:
		print(s)
		print()
	print("++++++++++++++++++++++++==")
	for s in maxStruct:
		print(s["style"])
		for ss in s.stripped_strings:
			print(ss)
			print()
		print("----")
	'''


	# # print(textStruct)
	# for c in textStruct:
	# 	# if type(c) == Tag:
	# 		# if no contents
	# 		print(type(c))
	# 		# print(len(c.children))
	# 		# print(c.children)
	# 		# if is a page #
	# 		print(c)
	# 		print()
	#
	# print(type(textStruct))

	break
print("````````````````````````````````````")
print(pageText)
#remove headers and footers by comparng across pages
#merge text across sections here
