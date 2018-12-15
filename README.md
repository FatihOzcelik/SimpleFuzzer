# SimpleFuzzer
This is a simple mutation based file format fuzzer written in python 2.7. It runs on Ubuntu Linux and it uses GNU Debugger (GDB) to monitor, detect and log faults.

Usage:
```
$ python SimpleFuzzer ['Target App'] ['Arguments Before File Name'] ['Input File Name'] ['Arguments After File Name']
