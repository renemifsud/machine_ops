#!/usr/bin/python3
import os
import math


size_kb = 13000000  # 2GB
filename = "13gbfile"
if __name__ == "__main__":
    chunksize = 1024
    chunks = math.ceil(size_kb / chunksize)
    with open(filename, "wb") as fh:
        for iter in range(chunks):
            numrand = os.urandom(int(size_kb * 1024 / chunks))
            fh.write(numrand)
        numrand = os.urandom(int(size_kb * 1024 % chunks))
        fh.write(numrand)



# Before
# import os

# GBS = 13
# GB = 1024 * 1024 * 1024  # 2GB

# if __name__ == "__main__":
#     for i, j in enumerate(range(GBS)):
#         GB = 1024 * 1024 * 1024
#         with open("large_file_" + str(i), "wb+") as fout:
#             fout.write(os.urandom(GB))
