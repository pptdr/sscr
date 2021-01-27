import os
os.chdir(os.path.dirname(__file__))
#    cwd = os.getcwd()
cwd = os.path.realpath(__file__)
print(cwd)
filepath = cwd + '/city.txt'
