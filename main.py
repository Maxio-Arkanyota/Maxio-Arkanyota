
import datetime
from git import Repo
import requests
from time import sleep
from discord import Webhook, RequestsWebhookAdapter

PATH_OF_GIT_REPO = r'.git'  # make sure .git folder is properly configured
today = datetime.datetime.now()
today = today.strftime('%j')
print(f"today -> {today}")
today = 1
webhook = Webhook.from_url("https://discord.com/api/webhooks/926421181870006303/X98DdFguI7lkpQKUhrkp5tjx-uYfP1P5e_5doL8AWhbdPvXcfmOLiboqsWSeMAO3Cf8f" ,adapter=RequestsWebhookAdapter())
file = open("./ori.push.py", "r+")
f = file.read()
file.write(f[today:])
file.close()
first = f[:today]
def git_push(commit, chr):
	open("./messy_pypi/__init__.py", "a").write(chr)
	try:
	    repo = Repo(PATH_OF_GIT_REPO)
	    repo.git.add(update=True)
	    repo.index.commit(commit)
	    origin = repo.remote(name='origin')
	    origin.push()
	except:
	    webhook.send("@Admin error bande de troll")

for i in first:
	git_push(f"radom commit {i}", i)
	sleep(3*60)