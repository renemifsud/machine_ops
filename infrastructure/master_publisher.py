#!/usr/bin/env python
from publisher import Publisher 
import threading, sys


if __name__ == "__main__":
    cnt = 0
    queue = []
    for num in range(int(sys.argv[1])):
        cnt += 1
        try:
            thread = Publisher(f"Message {cnt}", sys.argv[2])
            thread.start()
            queue.append(thread)
        except Exception as er:
            print (er)
            
    
    