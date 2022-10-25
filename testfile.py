import psutil
f = open('file.test', 'w')
p = psutil.Process()
p.open_files()
print(p)
#[popenfile(path='/Users/username/file.test', fd=3)]