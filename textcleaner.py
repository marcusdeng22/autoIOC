# import html
from bs4 import BeautifulSoup
import subprocess
import re
import sys
from collections import OrderedDict
from difflib import SequenceMatcher


def clean(FILE, page_no, print_to_stdout=True):
	original_page_no = page_no  # Because it changes throughout the rest of the program
	pdf2text_proc = subprocess.Popen("which pdf2txt.py", shell=True, stdout=subprocess.PIPE)

	pdf2text = pdf2text_proc.communicate()[0].strip().decode("utf-8")
	# print("location of pdf2txt:", pdf2text)

	LOAD = False	#debugging purposes

	minFontSize = 9	#in px
	headerSearch = 5
	footerSearch = 5
	marginAllowed = 0.95	#margin allowed between header and footer match; this is really just used if page # is part of the footer
	minLength = 20	#number of characters that must match at the start of a sentence in order to be considered equivalent (for header)
	pageAllowed = 3	#number of pages that may fail to match header and footer before we consider the current match to not be a footer

	pageText = []

	pageTop = re.compile("^[pP]age [0-9]+$")
	pageBot = re.compile("^[pP]age:")
	nonText = re.compile("^[^\w]+$")
	fontSize = re.compile("(font-size:)([0-9]+)(px)")
	while True:
		if not LOAD:
			command = " ".join(['python3.6', pdf2text, '-p', str(page_no), '-t', 'html', FILE])
			# print(command)
			#print()
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
		if len(textStruct) == 1:
			break
		text = []

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

		# if page_no > 10:	#debugging
		# 	break

	# print("````````````````````````````````````")
	# print(pageText)
	# print()
	# print()
	#remove headers and footers by comparng across pages
	def removeBorder(loc):
		if loc not in ["footer", "header"]:
			return []
		#footers first
		footerList = []	#list of dicts, where each key in the dict is style+footer, and value is [count, footer, [pages], directMatch]
		for i in range(1, footerSearch + 1):
			footerCount = {}
			if loc == "footer":
				i = -i
			else:
				i -= 1
			for n, p in enumerate(pageText):
				try:
					footer = str(list(p[i].values())[0])
					#handle very short strings, so is probably pg #: assumming page # < 1000
					if len(footer) <= 3:
						# print("short")
						footerKey = "short"
					else:
						footerKey = str(p[i])
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
								# if len(footerCount[k][1]) >= minLength and len(footer) >= minLength and footerCount[k][1][:minLength+1] == footer[:minLength+1]:
								# 	print("same head")
								# 	footerCount[""]
								seqM.set_seq2(k)
								# print(seqM.quick_ratio())
								if seqM.quick_ratio() > marginAllowed:
									footerCount[k][0] += 1
									footerCount[k][2].append(n)
									added = True
									break

							#try to match the start if header
							if not added and loc == "header":
								# print("trying match:", footer)
								seqM.set_seq1(footer)
								for k in keyList:
									storedFooter = footerCount[k][1]
									# print("comparing to:", storedFooter)
									seqM.set_seq2(storedFooter)
									matchInfo = seqM.get_matching_blocks()[0]
									# print(matchInfo)
									if matchInfo.a == 0 and matchInfo.b == 0 and matchInfo.size >= minLength:
										# print("matched!")
										longFooter = footer if len(footer) > len(storedFooter) else storedFooter
										newFooter = longFooter[:matchInfo.size]
										# print(newFooter)
										footerCount[newFooter] = [
											footerCount[k][0] + 1,
											newFooter,
											footerCount[k][2] + [n],
											True
										]
										added = True
										break
								if added and k != newFooter:
									# print("removing old:", k)
									del footerCount[k]

							if not added:
								#otherwise we need to just accept that it is probably not a footer
								footerCount[footerKey] = [1, footer, [n]]
					else:
						footerCount[footerKey][0] += 1
						footerCount[footerKey][2].append(n)
				except:
					print("error")
					continue
			# print("----------------------------------")
			# print(len(footerCount))
			# print(footerCount)
			# print()
			if len(footerCount) > pageAllowed:
				break	#unlikely anything past this point is a footer
			footerList.append(footerCount)
		return footerList
	#remove footers first
	# print("\nRemoving footers")
	footerList = removeBorder("footer")
	#now remove the footers
	for f in footerList:
		#take the footer that occurs the most often
		count = 0
		maxFooter = None
		for k, v in f.items():
			if v[0] > count:
				count = v[0]
				maxFooter = v
		# print(maxFooter)
		# print()
		for p in maxFooter[2]:
			del pageText[p][-1]

	# print("Removing headers")
	#now do headers
	headerList = removeBorder("header")
	currentFirst = 0
	for f in headerList:
		#take the header that occurs the most often
		count = 0
		maxHeader = None
		for k, v in f.items():
			if v[0] > count:
				count = v[0]
				maxHeader = v
		# print(maxHeader)
		# print()
		modified = False
		for p in maxHeader[2]:
			if len(maxHeader) == 3:
				del pageText[p][currentFirst]
			elif len(maxHeader) == 4:	#need to look at the first string and remove the header
				for k in pageText[p][currentFirst]:
					#should only be 1
					if pageText[p][currentFirst][k] != maxHeader[1]:
						pageText[p][currentFirst][k] = pageText[p][currentFirst][k][len(maxHeader[1]):].strip()
				modified = True
		if modified:
			currentFirst += 1

	# print("--------------------------------------------")
	# for p in pageText:
	# 	print(p)
	# 	print()

	#parse table of contents
	toc = []
	#remove styles
	for t in pageText[0]:
		for k, s in t.items():
			toc.append(s)
	contents = {}	#key is section title, value is page #
	#text may be in one style, or section and number are different styles
	inlineMatch = re.compile("(.*?)\s?(?P<spacing>[^a-zA-Z0-9])(?P=spacing)+\s?([0-9]+)")
	#(.*?)\s?([^a-zA-Z0-9])\2+\s?([0-9]+)
	numMatch = re.compile("^([0-9]+)$")
	trailer = ""
	for l in range(len(toc)):
		r = inlineMatch.search(toc[l])
		if r == None and numMatch.match(toc[l]) == None:
			#need to lookahead to next section for page number
			o = l+1
			if o < len(toc):
				num = numMatch.match(toc[o])
				if not num == None:
					contents[toc[l]] = int(toc[o])
					continue
				else:
					#this probably is some random text and can be dropped
					continue
		elif r != None:
			trailer += toc[l]
			offset = 0
			r = inlineMatch.search(trailer)
			while r != None:	#add contents until trailer is unmatched
				offset = r.end()
				contents[r.group(1).strip()] = int(r.group(3))
				trailer = trailer[offset:]
				r = inlineMatch.search(trailer)
		elif numMatch.match(toc[l]) != None:	#we found a page number, so add to previous trailer
			contents[trailer] = int(numMatch.match(toc[l]).group(1))
		else:
			continue

	# print("------------------")
	# print("Contents:", *contents, sep='\n\t')


	#merge text across pages here
	fullText = []	#each entry will be a section from the table of contents, where each entry is [title, text, subtitle, text, ...]
	curSection = []
	curStyle = None
	for num, p in enumerate(pageText[1:]):	#page
		for t in p:	#text, list of dicts
			for style, text in t.items():	#text; dict, should only be 1
				#assumes section title/subtitle are of different styles than normal text
				seqM = SequenceMatcher(a=text.lower())
				newSection = False
				for title, pageRef in contents.items():
					seqM.set_seq2(title.lower())
					if seqM.quick_ratio() > marginAllowed and abs(num + original_page_no - pageRef) <= 2:	#approximately close to actual page
						if len(curSection) > 0:
							fullText.append(curSection)
						curSection = [text]
						curStyle = None
						newSection = True
						break
				if not newSection:
					if style == curStyle:
						curSection[-1] += " " + text
					else:
						curSection.append(text)
						curStyle = style
	fullText.append(curSection)

	#print("-----------------------")

	# out_file = FILE.split('.')  # in case the file has many . in the name
	# out_file[-2] = out_file[-2] + "_parsed-sections"
	# out_file[-1] = 'txt'
	# out_file = '.'.join(out_file)
	# print("Outputting to:", out_file, '\n')
	# with open(out_file, 'w') as f:
	if print_to_stdout:
		for section in fullText:
			for s in section:
				print(s)
				print()
			print("++++++++++++++++")
	else:
		return fullText


if __name__ == "__main__":
	if len(sys.argv) != 3:
		print("usage: python3.6 textcleaner.py <file> <page for table of contents>")
		print("table of contents is assumed to be 1 page only")
		exit()
	
	FILE = sys.argv[1]
	page_no = int(sys.argv[2])#10#3
	clean(FILE, page_no)
