## Take a user defined set of files currently in Enjin mark-up and translate them to a pipe
## delimited text file. Enjin mark-up is to be replaced with standard HTML and single quote (')
## characters are to be replaced with HTML escape sequence.
##
## File formatting rules are as follows:
## [rule] tag denotes the end of an entry.
## The first line in an entry to contain the [/color] tag is the title.

def htmlParse( str ):
	outString = str.replace("[color=red]", "")
	outString = outString.replace("[/color]", "")
	outString = outString.replace("[b]", "")
	outString = outString.replace("[/b]", "")
	outString = outString.replace("[table]", "<table>")
	outString = outString.replace("[/table]", "</table>")
	outString = outString.replace("[tr]", "<tr>")
	outString = outString.replace("[td]", "<td>")
	outString = outString.replace("[/tr]", "</tr>")
	outString = outString.replace("[/td]", "</td>")
	outString = outString.replace("'", "&#39;")
	return outString

fileDict = {
	"DS1.txt" : "DX",
	"KS1.txt" : "KN",
	"MS1.txt" : "OP",
	"PS1.txt" : "PR",
	"SS1.txt" : "ST",
	"TS1.txt" : "TH",
	}

with open('SkillFile.txt', 'w') as outFileObj:

	for fileName, catString in fileDict.items():
		## fileName: name of the input file. Defined by user.
		## catString: String to be appended to the output.
		catString = "S|" + catString + "|0|0|0|0|0|''|''|0|''|''|''|''"

		with open(fileName) as fileObj:
			line = fileObj.readline()
			outputLine = '' # String to write to file.
			titleFound = False
			while line != '':
				currentLine = line.rstrip()
				if currentLine == '[rule]':
					### End of data section. Append fixed data and output.
					outputLine += '|' + catString + '|' + '\n'
					outFileObj.write(outputLine)
					titleFound = False
					outputLine = ''

				else :
					isTitle = False # flag denoting whether the title of this section has been found.

					if currentLine == '':
						outputLine += '<p>'

					if '[/color]' in currentLine and not titleFound:
						## Meets criteria for title section. Set appropriate flags.
						isTitle = True
						titleFound = True

					outputLine += htmlParse(currentLine) ## Apply the sepecified data cleaning

					if isTitle:
						## Separator tag between title and other content.
						outputLine += '|'


				line = fileObj.readline()
		fileObj.closed
outFileObj.closed
