import os
from subprocess import Popen
try:
	os.chdir(os.path.abspath(os.path.dirname(__file__)))
except:
	pass
EXIT_SUCCESS = 0
EXIT_FAILURE = 1
EOF = (-1)


def getTxt(filePath:str, index:int = 0) -> str: # get .txt content
	coding = ("utf-8", "gbk", "utf-16") # codings
	if 0 <= index < len(coding): # in the range
		try:
			with open(filePath, "r", encoding = coding[index]) as f:
				content = f.read()
			return content[1:] if content.startswith("\ufeff") else content # if utf-8 with BOM, remove BOM
		except (UnicodeError, UnicodeDecodeError):
			return getTxt(filePath, index + 1) # recursion
		except:
			return None
	else:
		return None # out of range

def handleFolder(fd:str) -> bool:
	folder = str(fd)
	if not folder:
		return True
	elif os.path.exists(folder):
		return os.path.isdir(folder)
	else:
		try:
			os.makedirs(folder)
			return True
		except:
			return False

def generateProtocolTxt(pythonFilePath:str) -> bool:
	if isinstance(pythonFilePath, str):
		if os.path.splitext(pythonFilePath)[1].lower() == ".py":
			content, folderPath, fileName = getTxt(pythonFilePath), pythonFilePath[:-3], os.path.split(pythonFilePath)[1][:-3] + ".tex"
			if content is None:
				print("Failed to read \"{0}\". ".format(pythonFilePath))
				return False
			elif handleFolder(folderPath):
				try:
					with open(os.path.join(folderPath, fileName), "w", encoding = "utf-8") as f:
						f.write("\\documentclass[a4paper]{article}\n\\setlength{\\parindent}{0pt}\n\\usepackage{amsmath,amssymb}\n\n\\begin{document}\n\n\\section{Protocol}\n\n")
						classFlag, functionFlag, protocolFlag, doubleSeparatorSwitch = False, False, False, True
						for line in content.splitlines():
							if line.startswith("class Protocol"):
								classFlag = True
							elif classFlag and line.startswith("\tdef ") and "#" in line:
								f.write("\\subsection{" + line[line.index("#") + 1:].strip() + "}\n\n")
								functionFlag = True
							elif classFlag and functionFlag and "\t\t# Protocol #" == line:
								protocolFlag = True
							elif classFlag and functionFlag and protocolFlag and line.count("#") == 1 and "#" in line:
								prompt = line[line.index("#") + 1:].strip()
								if "$" == prompt:
									doubleSeparatorSwitch = not doubleSeparatorSwitch # invert the double separator switch
								elif prompt.startswith("$") and not prompt.endswith("$"):
									doubleSeparatorSwitch = False # disable the double separator switch
								elif not prompt.startswith("$") and prompt.endswith("$"):
									doubleSeparatorSwitch = True # enable the double separator switch
								f.write(prompt + ("\n\n" if doubleSeparatorSwitch else "\n"))
							elif line.strip() and not line.startswith("\t") and not line.lstrip().startswith("#"):
								classFlag, functionFlag, protocolFlag, doubleSeparatorSwitch = False, False, False, True # reset
							if functionFlag and protocolFlag and line.startswith("\t\treturn "):
								functionFlag, protocolFlag = False, False
						f.write("\\end{document}")
					print("The TEX generation for \"{0}\" succeeded. ".format(pythonFilePath))
					process = Popen(["pdflatex", fileName], cwd = folderPath, shell = True)
					if process.wait() == EXIT_SUCCESS:
						print("The TEX compilation for \"{0}\" succeeded. ".format(pythonFilePath))
						return True
					else:
						print("The TEX compilation for \"{0}\" failed. ".format(pythonFilePath))
						return False
				except BaseException as e:
					print("The TEX generation for \"{0}\" failed since {1}. ".format(pythonFilePath, e))
					return False
			else:
				print("The TEX generation for \"{0}\" failed since the parent folder was not created successfully. ".format(pythonFilePath))
				return False
		else:
			print("The passed file \"{0}\" is not a Python file. ".format(pythonFilePath))
			return False
	else:
		print("The passed parameter should be a string. ")
		return False

def main() -> int:
	bRet = True
	for pythonFilePath in ("ProtocolAnonymousME.py", "ProtocolHIBME.py", "ProtocolIBMETR.py"):
		bRet = generateProtocolTxt(pythonFilePath) and bRet
	iRet = EXIT_SUCCESS if bRet else EXIT_FAILURE
	print("Please press the enter key to exit ({0}). ".format(iRet))
	input()
	return iRet



if "__main__" == __name__:
	exit(main())