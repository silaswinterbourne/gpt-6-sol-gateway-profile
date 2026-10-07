import pathlib,re,sys
def validate(path):
 s=pathlib.Path(path).read_text()
 for field in ('schema:','model:','base_url:','endpoint:','docs:'): assert field in s,field
 assert 'https://' in s
 return True
if __name__=='__main__': validate(sys.argv[1]); print('valid')
