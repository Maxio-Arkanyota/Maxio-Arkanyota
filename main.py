
from tqdm import tqdm
import datetime
from git import Repo
import requests
from time import sleep
from discord import Webhook, RequestsWebhookAdapter

PATH_OF_GIT_REPO = r'.git'  # make sure .git folder is properly configured
today = datetime.datetime.now()
today = int(today.strftime('%j'))
webhook = Webhook.from_url("https://discord.com/api/webhooks/926423307421638666/0Gjv7qcTRvtEO8SQaDTt_ZZp0W2OV7AvI709h4TcEB-ECtIP8SPKG92nvTu3huOpwlmf" ,adapter=RequestsWebhookAdapter())

"""
f = open("./ori.push.py", "r").read()
first = f[:today]
open("./ori.push.py", "w").write(f[today:])
"""

first = "m: set f"
print(f"day -> {today} -> '{first}'")
def git_push(commit, chr):
    print(f"radom commit {chr}")
    open("./messy_pypi/__init__.py", "a").write(chr)
    try:
        repo = Repo(PATH_OF_GIT_REPO)
        repo.git.add(update=True)
        repo.index.commit(commit)
        origin = repo.remote(name='origin')
        origin.push()
        webhook.send(commit)
    except:
        webhook.send("@Admin error bande de troll")

for ind,i in enumerate(first):
    git_push(f"day : {today}, commit : {ind + 2}/{today} -> '{i}'", i)
    if ind != len(first) - 1:
        for _ in tqdm(range(60)):
	        sleep(1)
