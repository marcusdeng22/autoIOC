# import html
from bs4 import BeautifulSoup
import subprocess
import re
import sys
from collections import OrderedDict
from difflib import SequenceMatcher

if len(sys.argv) != 3:
	print("usage: python3.6 textcleaner.py <file> <page for table of contents>")
	exit()

FILE = sys.argv[1]

pdf2text_proc = subprocess.Popen("which pdf2txt.py", shell=True, stdout=subprocess.PIPE)

pdf2text = pdf2text_proc.communicate()[0].strip().decode("utf-8")
print("location of pdf2txt:", pdf2text)

page_no = int(sys.argv[2]) + 1#10#3
LOAD = False	#debugging purposes

minFontSize = 9	#in px
headerSearch = 5
footerSearch = 5
marginAllowed = 0.95	#margin allowed between header and footer match; this is really just used if page # is part of the footer
pageAllowed = 3	#number of pages that may fail to match header and footer before we consider the current match to not be a footer

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
	fontSize = re.compile("(font-size:)([0-9]+)(px)")

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
				#check if font is big enough
				styleFont = fontSize.search(style)
				if styleFont is not None and len(styleFont.groups()) == 3 and float(styleFont.group(2)) < minFontSize:
					# print("dropping because of font")
					# print(s)
					# add = False
					# break
					continue
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
	# break

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
		if lastKey == newKeyList[0]:	#equivalent styles
			finalText[-1][lastKey] += " " + i[newKeyList[0]]
			#add remaining
			for k in newKeyList:
				if k == newKeyList[0]:
					continue
				finalText.append({k: i[k]})
		#elif same font size? take font-family of longer string
		else:	#add new sections
			for k in i:
				finalText.append({k: i[k]})
			continue

	pageText.append(finalText)

	if page_no > 10:
		break

print("````````````````````````````````````")
print(pageText)
print()
print()
#remove headers and footers by comparng across pages
#footers first
footerList = []	#list of dicts, where each key in the dict is style+footer, and value is [count, footer, [pages]]
for i in range(1, footerSearch + 1):
	footerCount = {}
	for n, p in enumerate(pageText):
		try:
			footer = str(list(p[-i].values())[0])
			#handle very short strings, so is probably pg #: assumming page # < 1000
			if len(footer) <= 3:
				# print("short")
				footerKey = "short"
			else:
				footerKey = str(p[-i])
			if footerKey not in footerCount:
				#try comparing if key is close to an existing key
				keyList = footerCount.keys()
				if len(keyList) == 0:	#nothing in dict so far
					footerCount[footerKey] = [1, footer, [n]]
				else:
					added = False
					seqM = SequenceMatcher(a=footerKey)
					for k in keyList:
						if k == "short":
							continue
						seqM.set_seq2(k)
						if seqM.quick_ratio() > marginAllowed:
							footerCount[k][0] += 1
							footerCount[k][2].append(n)
							added = True
							break
					if not added:
						#otherwise we need to just accept that it is probably not a footer
						footerCount[footerKey] = [1, footer, [n]]
			else:
				footerCount[footerKey][0] += 1
				footerCount[footerKey][2].append(n)
		except:
			print("error")
			continue
	print(len(footerCount))
	if len(footerCount) > pageAllowed:
		break	#unlikely anything past this point is a footer
	footerList.append(footerCount)
# print(footerList)
#now remove the footers
for f in footerList:
	# print(f)
	# print()
	#take the footer that occurs the most often
	count = 0
	maxFooter = None
	for k, v in f.items():
		if v[0] > count:
			count = v[0]
			maxFooter = v
			maxKey = k
	print(maxFooter)
	print()
	for p in maxFooter[2]:
		del pageText[p][-1]
print()
for p in pageText:
	print(p)
	print()

#merge text across sections here
