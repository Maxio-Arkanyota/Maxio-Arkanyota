#!/usr/bin/python3
from tqdm import tqdm
import datetime
import sys
from git import Repo
import requests
from time import sleep
from discord import Webhook, RequestsWebhookAdapter

print(f"date -> {datetime.datetime.now()}", file=sys.stderr)
PATH_OF_GIT_REPO = r'.git'  # make sure .git folder is properly configured
today = datetime.datetime.now()
today = int(today.strftime('%j'))
webhook = Webhook.from_url("https://discord.com/api/webhooks/930571408906526770/oLoTyvGTZNfENJes0PDhOP7J-VBw2CKvJEcip8fEoEfhmzRcgIyRRQmBRNMDOKr2Bk5Z" ,adapter=RequestsWebhookAdapter())
webhook.send(f"Salut on commence a push 😊")

f = open("./ori.push.py", "r").read()
first = f[:today]
open("./ori.push.py", "w").write(f[today:])

print(f"day -> {today} -> '{first.encode('unicode_escape').decode()}'")
webhook.send(f"start commit : day -> {today} -> `{first.encode('unicode_escape').decode()}`")

def git_push(commit, chr):
    print(commit)
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
    git_push(f"day : {today}, commit : {str(ind + 1).zfill(len(str(today)))}/{today} -> `{i.encode('unicode_escape').decode()}`", i)
    if ind != len(first) - 1:
        for _ in tqdm(range(30)):
	        sleep(1)
