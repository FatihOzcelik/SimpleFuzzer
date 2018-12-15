# Author: Fatih Ozcelik
# Developed as a part of my BSc project.

import sys
import os
import random
import time
import subprocess
import threading
import time

originalFile = ""
targetApp = ""

try:
	targetApp = sys.argv[1]
	argumentsBeforeFile = sys.argv[2]
	originalFile = sys.argv[3]
	argumentsAfterFile = sys.argv[4]

except IndexError:
	print("Usage: python SimpleFuzzer ['Target App'] ['Arguments Before File'] ['Input file name'] ['Arguments After File']")
	exit()

#Load the input file
def load_file(file):
	#Open the file with the 'rb' mode, meaning read binary mode
	#The with-statement: "file is properly closed after its suite finishes, even if an exception is raised"
	with open(file, "rb") as f:
		readFile = bytearray(f.read())
		return readFile

def save_file(fileName, fileData):
	try:
		with open(fileName, "wb") as f:
			f.write(str(fileData))
	except IOError:
		print("Error! Make sure to create a folder named 'test_samples'. All the mutated test samples will reside in this folder.")
		exit()

#Mutate the loaded data
def mutateRandom(fileDataByteArr):
	#Bitflip - XOR
	#to have a random number of loops from 1 to the length of the fileDataByteArr / 4
	randomLoop = random.randint(1, int(len(fileDataByteArr)/4))
	
	for i in range(0, randomLoop):
		#Which bit to be mutated.
		#(To avoid editing meta-description of the file format (file-header), it will start at 25% in the file)
		randomByteIndex = random.randint(int(len(fileDataByteArr)/4), len(fileDataByteArr)-1) 
		
		#The random byte value to be applied in mutation (range must be in 0,256 (bytearray))
		randomByteValue = random.randint(0, 255) 
		
		#Takes the bytevalue at index randomByteIndex from fileDataByteArr and XOR it with randomByteValue
		fileDataByteArr[randomByteIndex] = fileDataByteArr[randomByteIndex] ^ randomByteValue
	
	return fileDataByteArr

def launch_target_app_with_mutated_file(mutatedFileName):
	#macOS approach:
	#os.system(targetApp + " " + mutatedFileName)
	#time.sleep(2)
	#os.system("killall " + "gedit")

	proc = subprocess.Popen(["gdb", "--batch", "-ex", "run", "-ex", "where", "--args",
	  targetApp, argumentsBeforeFile, mutatedFileName, argumentsAfterFile],
	  stdout=subprocess.PIPE)
	
	#Sometimes, it can be necessary to remove the argumentsBeforeFile argument - if so, use the commented
	#three lines belowinstead of the above three lines
	#proc = subprocess.Popen(["gdb", "--batch", "-ex", "run", "-ex", "where", "--args",
	#  targetApp, mutatedFileName, argumentsAfterFile],
	#  stdout=subprocess.PIPE)

	timer = threading.Timer(1, proc.terminate)
	try:
		timer.start()
		stdoutput, stderr = proc.communicate()
	finally:
		timer.cancel()
	print("stdout: " + stdoutput)
	#When a crash happens, gdb will e.g. output "Program received signal SIGSEGV, Segmentation fault".
	#Therefore if "Program received signal" is in output, then we know there is a crash.
	if "Program received signal" in stdoutput:
		print("RETURNED OUTPUT")
		return stdoutput
	else:
		print("RETURNED (nothing interesting)")
		return None

runNumber = 0
crashFileNumber = 0
fileNumber = 0

readFile = load_file(originalFile)

while True:
	print("Run " + str(runNumber))
	runNumber += 1

	mutatedFile = mutateRandom(readFile)

	extension = os.path.splitext(originalFile)[1]
	mutatedFileName = "test_samples/mutated_file" + str(fileNumber) + extension
	
	#Save file test-sample (this saves all mutated files)
	save_file(mutatedFileName, mutatedFile) 
	fileNumber += 1

	#Launch the target app with the mutated file and see if it fails (if so, save crash-sample)
	crashSampleName = "crash_sample" + str(fileNumber) + extension
	crashOutputName = "crash_output" + str(fileNumber) + ".txt"
	stdoutput = launch_target_app_with_mutated_file(mutatedFileName)
	if stdoutput is not None:
		print("Program crashed!")
		#save the mutated file which caused crash
		save_file(crashSampleName, mutatedFile)
		#also save the crash-output
		save_file(crashOutputName, stdoutput)
		print(stdoutput)

	crashFileNumber += 1