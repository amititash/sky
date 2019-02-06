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

import multiprocessing, glob, re, time

def process(file):
    pattern = re.search('tmp_config/(.+?).config.json', file)
    if pattern:
        configname = pattern.group(1)
        print("configname is ", configname)
    command = "python3 c2.py "+file+" "+configname
    print("crawling...",command)
    os.system(command)

def multer(maxsize=15):
    
    p = multiprocessing.Pool()
    for f in glob.glob("tmp_config/*.json"):
        # launch a process for each file (ish).
        # The result will be approximately one process per CPU core available.
        p.apply_async(process, [f]) 
        while p._taskqueue.qsize() > maxsize:
            print("************SLEEPING************")
            time.sleep(100)
            print("*******WAKING UP***************")
        
        
        
    p.close()
    p.join() # Wait for all child processes to close.


if __name__ == "__main__":  
    multer()
    
