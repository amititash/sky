import os

'''
def files(path):  
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

with open('start.sh', 'a') as filehandle:
    for file in files("tmp_config/"):
        filehandle.write("python3 c2.py tmp_config/"+file+" "+file+" &\n")
'''

import multiprocessing, glob

def process(file):
    command = "python3 c2.py "+file+" "+file+" &"
    print("crawling...",command)
    os.system(command)

p = multiprocessing.Pool()
for f in glob.glob("./tmp_config/*.json"):
    # launch a process for each file (ish).
    # The result will be approximately one process per CPU core available.
    p.apply_async(process, [f]) 

p.close()
p.join() # Wait for all child processes to close.
