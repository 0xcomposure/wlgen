import os
import re
import sys
import json
import signal
import argparse
import validators
from datetime import date
from argparse import RawTextHelpFormatter

days = []
lang = []
users = []
months = []
seasons = []
keywords = []
languages = []
subdomains = []

target = ''
minyear = 1970
complete = False
filename = 'wordlist.txt'
currentyear = date.today().year + 1 
urlre = re.compile(r"https?://(www\.)?")
resourcespath = os.path.dirname(os.path.abspath(__file__)) + '/resources/'

with open(resourcespath + 'languages.json') as languagesjson:
    languages = json.load(languagesjson)

parser = argparse.ArgumentParser(description='Wordlist Generator.')
parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.add_argument('--target',
                    '-T',
                    help = "Enter the name of the target. \n"
                         + "Example: -T targetcorp or -T https://targetcorp.com/\n",
                    required = True,
                    nargs = 1,
                    type = str)

parser.add_argument('--output',
                    '-O',
                    help = "Output file. \n"
                         + "Example: -O /path/to/output.txt\n",
                    nargs = 1,
                    type = str)

parser.add_argument('--complete',
                    '-C',
                    help = 'Add more causistry.\n',
                    action = 'store_true')

parser.add_argument('--keywords',
                    '-K',
                    help = 'List of keywords to add, separated by comma and no space between each keyword.'
                         + 'Example: -K example,keyword,test,word\n',
                    nargs = 1,
                    type = str)

parser.add_argument('--lang',
                    '-L',
                    help = 'Language of the target.\n'
                         + 'English:eng, Spanish:spa, Vietnamese:vie, Portuguese: por, Catalan: cat, Galician: glg\n'
                         + 'To add more than one separate each by comma and no space between each one.\n'
                         + 'Example: -L eng,spa\n',
                    required = True,
                    nargs = 1,
                    type = str)

parser.add_argument('--users',
                    '-U',
                    help = 'List of users, the domain will be deleted automatically if the list contains email addresses\n',
                    nargs = 1,
                    type = str)

args = parser.parse_args()

if args.keywords is not None:
    try:
        keywords = str(args.keywords[0]).split(',')
    except Exception as e:
        print('The keywords must be separated by comma and no space between each keyword.')
        exit(str(e))

if args.target is not None:
    if validators.url(str(args.target[0])):
        target = urlre.sub('', str(args.target[0])).strip().strip('/')
    else:    
        target = str(args.target[0])

    if target.count('.') > 1:
        domstrings = str(target).split('.')
        subdomains.extend(domstrings[:len(domstrings) - 2])
        del domstrings[:len(domstrings) - 2]
        target = domstrings[0]
        for sd in subdomains:
            keywords.append(sd)
    target = str(target.split('.')[0])
    print('Target: ' + target + '\n')
else:
    exit('It requires the target')

if args.output is not None:
    filename = args.output[0]
    print('Output file: ' + filename + '\n')

if args.complete is True:
    complete = True

if args.lang is not None:
    try:
        langs = []
        langs = str(args.lang[0]).split(',')
        for l in langs:
            if l in languages['languages']:
                lang.append(str(l))
            else:
                raise Exception('The language code is not valid.')
        print('Languages for the target: ' + ','.join(lang) + '\n')
    except Exception as e:
        exit(str(e))

else:
    exit('It requires the language for the target')

if args.users is not None:
    try:
        usersfile = open(str(args.users[0]), 'r')
        for user in usersfile:
            user = user.rstrip('\n')
            usernomail = re.search(r'([\w\d\.]+)@[\w\d\.]+', user)
            if usernomail and user.count('@') == 1:
                users.append(usernomail.group(1).replace('.', '').replace(' ', ''))
                users.append(usernomail.group(1).replace(' ', ''))
            else:
                users.append(user)
        usersfile.close()
    except Exception as e:
        print('The file could not be read')
        exit(str(e))

file = open(filename, 'w+')


def exit(msg):
    parser.print_help(sys.stderr)
    print(msg, file=sys.stderr)


def sigint_handler(signal, frame):
    print ('Task interrupted...')
    sys.exit(0)
signal.signal(signal.SIGINT, sigint_handler)



def writetofile(v, n = 0):
    if n:  
        file.write(v + str(n) + '\n')
        file.write(v[0].upper() + v[1:] + str(n) + '\n')
        file.write(v.upper() + str(n) + '\n')
        if complete:
            file.write(v + '@' + '\n')
            file.write(str(n) + v + '\n')
            file.write(str(n) + v.upper() + '\n')
            file.write(str(n) + v[0].upper() + v[1:] + '\n')
            file.write(v + '@' + str(n) + '\n')
            file.write(v.upper() + '@' + str(n) + '\n')
            file.write(v[0].upper() + v[:1] + '@' + str(n) + '\n')
            file.write(str(n) + '@' + v + '\n')
            file.write(str(n) + '@' + v.upper() + '\n')
            file.write(str(n) + '@' + v[0].upper() + v[1:] + '\n')
    else:
        file.write(v + '\n')
        file.write(v[0].upper() + v[1:] + '\n')
        file.write(v.upper() + '\n')
        

def getjson(data, typedata, language=''):
    return data[typedata]['languages'][language]

with open(resourcespath + 'days.json') as days_json:
    data = json.load(days_json)
    for l in lang:
        days.extend(getjson(data, 'days', l))
with open(resourcespath + 'months.json') as months_json:
    data = json.load(months_json)
    for l in lang:
        months.extend(getjson(data, 'months', l))

with open(resourcespath + 'seasons.json') as seasons_json:
    data = json.load(seasons_json)
    for l in lang:
        seasons.extend(getjson(data, 'seasons', l))

for d in days:
    writetofile(d)
    for dn in range(1, 31):
        writetofile(d, dn)

if complete:
    minyear = 1

for m in months:
    writetofile(m)
    for mn in range(minyear, currentyear):
        writetofile(m, mn)

for s in seasons:
    writetofile(s)
    for sn in range(minyear, currentyear):
        writetofile(s, sn)

writetofile(target)
for tn in range(minyear, currentyear):
    writetofile(target, tn)

if len(users):
    cleanusers = [i for n, i in enumerate(users) if i not in users[:n]]
    for u in cleanusers:
        writetofile(str(u))
        for un in range(minyear, currentyear):
            writetofile(u, un)

if len(keywords):
    cleankeys = [i for n, i in enumerate(keywords) if i not in keywords[:n]]
    for k in cleankeys:
        writetofile(str(k))
        for kn in range(minyear, currentyear):
            writetofile(k, kn)
print('Wordlist saved in: ' + filename)
file.close()
