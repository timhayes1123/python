## @author: Tim Hayes
## @date: 7/23/19
## Take a user defined set of files currently in Enjin mark-up and build SQL Insert statements
## from the data contained within. This script is to generate a file of Insert statements only
## NOT to execute them. Source data is considered as trusted and integers will be where integers
## are expected.
##
## The data is currently in Enjin mark-up format. In some fields, the mark-up is to be stripped
## out entirely. In other fields it is to be replaced with corresponding HTML tags.
##
## File formatting rules are as follows:
## [rule] tag denotes the end of an entry.
## The first line in an entry to contain the [/color] tag is the title.

## Simple object to contain the text data.

import re

class DataObject:
	"""Contains the data being translated"""

	def __init__ (self, textPref):
		self.textPrefix = textPref
		self.title = ""
		self.descr = ""
		self.rank = "0"
		self.requirementTech = ""
		self.requirementOther = ""
		self.constraint = "NA"
		self.reviewed = "0"
		self.range = ""
		self.duration = ""
		self.avail = ""
		self.status = ""

def cleanUp(str):
	return str.replace("<table></table>", "")

def htmlClear( str ):
	### Strip all mark-up tags from the input parameter. Mark-up tags are in the form [tag]...[/tag]
	outString = re.sub("\[(.*?)\]", "", str) # Remove all text between the square brackets.
	outString = re.sub("\[", "", outString) # Remove the square brackets themselves.
	outString = re.sub("\]", "", outString)

	return outString

def htmlParse( str ):
	## Replace all square brackets with angle brackets.
	outString = re.sub("\[", "<", str)
	outString = re.sub("\]", ">", outString)

	## Remove the disallowed tags altogether.
	outString = outString.replace("<color=red>", "")
	outString = outString.replace("</color>", "")
	outString = outString.replace("<b>", "")
	outString = outString.replace("</b>", "")

	outString = outString.replace("'", "&#39;")
	return outString

## Mapping of filenames to input fields `type` and `attr`.

fileDict = {
	"DS3.txt" : "'S'|'DX'",
	"KS3.txt" : "'S'|'KO'",
	"MS3.txt" : "'S'|'OP'",
	"PS3.txt" : "'S'|'PR'",
	"SS3.txt" : "'S'|'ST'",
	"TS3.txt" : "'S'|'TC'",
	"SA3.txt" : "'F'|'SA'",
	"CS3.txt" : "'F'|'CS'",
	"C3.txt" : "'F'|'C'",
	"S3.txt" : "'F'|'S'",
	"CA3.txt" : "'F'|'CA'",
	"A3.txt" : "'F'|'A'",
	"SAL.txt" : "'F'|'SAL'",
	"CAS.txt" : "'F'|'CAS'",
	}

## Mapping of data section names to the DataObject property name.
fieldHeadingsDict = {
	'Rank Required:' : 'rank',
	'Technical Requirements:' : 'requirementTech',
	'Other Requirements:' : 'requirementOther',
	'Constraints:' : 'constraint',
	'Reviewed:' : 'reviewed',
	'Date Range:' : 'range',
	'Duration:' : 'duration',
	'Time Available:' : 'avail',
	'Status:' : 'status',
	}

with open('generated_insert.sql', 'w') as outFileObj:

	for fileName, catString in fileDict.items():
		## fileName is the name of the file to be opened.
		## catString is data to be appended. Correspond to the `spec`, `adv`, `specreq`, `advreq` fields in the database.
		catString += "|0|0|0|0|";
		with open(fileName) as fileObj:
			line = fileObj.readline()

			titleFound = False
			thisObj = DataObject(catString)
			while line != '':
				currentLine = line.rstrip()
				### End of the object in source text is denoted by [rule]
				if currentLine == '[rule]':
					### Denotes the end of the section. Data object should be fully populated. Generate and output INSERT statement.
					insertStmt = "INSERT INTO `skill` (`name`, `descr`, `type`, `attr`, `spec`, `adv`, `specreq`, `advreq`, `rank`, `prereq`, `constraint`, `reviewed`, `range`, `duration`, `availtime`, `status`) VALUES ("
					insertStmt += "'" + thisObj.title + "', "
					insertStmt += "'" + cleanUp(thisObj.descr) + "', "
					tokenList = thisObj.textPrefix.split("|")
					tokenCounter = 1
					for token in tokenList:
						## Expect exactly 6 fields to be populated through this method.
						print ("tokenCounter = " + str(tokenCounter) + "\ntoken = " + token + "\n")

						if tokenCounter <= 6:
							insertStmt += token + ","
							tokenCounter += 1

					insertStmt += thisObj.rank + ", "

					if 'None' == thisObj.requirementTech:
						thisObj.requirementTech = ""
					if 'None' == thisObj.requirementOther:
						thisObj.requirementOther = ""


					if '' == thisObj.requirementTech and '' == thisObj.requirementOther:
						## If both values contain the empty string, insert the value "None"
						insertStmt += "'None', "
					elif '' != thisObj.requirementTech and '' != thisObj.requirementOther:
						## If neither value is empty, insert both values separated by a comma and a space.
						insertStmt += "'" + thisObj.requirementTech + ", " + thisObj.requirementOther + "', "
					else:
						## If one or the other is empty, concatenate both values with a space separator and strip the end space.
						tempLine = thisObj.requirementTech + ' ' + thisObj.requirementOther
						tempLine = tempLine.strip()
						insertStmt += "'" + tempLine + "', "

					insertStmt += "'" + thisObj.constraint + "', "
					insertStmt += thisObj.reviewed + ", "
					insertStmt += "'" + thisObj.range + "', "
					insertStmt += "'" + thisObj.duration + "', "
					insertStmt += "'" + thisObj.avail + "', "
					insertStmt += "'" + thisObj.status + "');" + '\n'

					# print(outputLine, end='')
					outFileObj.write(insertStmt)
					titleFound = False
					thisObj = DataObject(catString)
					# print('if')
				else :
					isTitle = False

					if '[color=red]' in currentLine and not titleFound:
						## First occurence of [color=red] in the section denotes that this line is the data title.
						isTitle = True
						titleFound = True
						thisObj.title = htmlParse(currentLine)
					elif any(field in currentLine for field in list(fieldHeadingsDict.keys())):
						## Check to see if the text contains any of the keys of fieldHeadingsDict.
						## If so, then parse and assign to the appropriate data field.
						clearText = htmlClear(currentLine)
						colonPos = clearText.find(':')
						###Should always be true.
						if colonPos >= 0:
							## Everything before the colon corresponds to the key.
							## Everything after the colon is the data.
							## The value field in fieldHeadingsDict corresponds to the property name of the data object.
							keyVal = clearText[:colonPos + 1]
							varValue = htmlParse(clearText[colonPos + 1:])
							varName = fieldHeadingsDict[keyVal]

							## Convert Yes/No text field to integer boolean.
							if 'reviewed' == varName:
								if varValue == "No":
									varValue = "0"
								else:
									varValue = "1"
							setattr(thisObj, varName, varValue)
					else :
						## If none of the above conditions apply, then the current line contains the record description
						thisObj.descr += htmlParse(currentLine)


				line = fileObj.readline()
		fileObj.closed

	# outFileObj.write(outputLine)
outFileObj.closed
