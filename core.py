import json
import requests
from ftplib import FTP
import os.path

class Article():
    pass

class Issue():
    
    def __init__(self, index, year, number, pub):
        self.index = index
        self.year = year
        self.number = number
        self.pub = pub

    def __str__(self):
        return f'Issue {self.number} {self.year}/{self.year+1}, Index: {self.index} ,Published: {self.pub}'

    def __repr__(self):
        return f'Issue {self.number} {self.year}/{self.year+1}, Index: {self.index} ,Published: {self.pub}'

    def to_json(self):
        return [self.index,{'date': self.year, 'nr': self.number, 'pub': self.pub}]

class Gazetka():

    def __init__(self):
        self.issues=[]
        self.ftp=None
        if not os.path.isfile('tokens.txt'):
            raise NotConfiguredError

    def start_session(self):
        try:
            self.ftp = FTP('www.lo2.opole.pl')
            with open('tokens.txt','r') as f:
                tokens = f.read()
                tokens = tokens.split('\n')
                self.ftp.login(tokens[0],tokens[1])
        except Exception as e:
            print(e) 

    def stop_session(self):
        if self.ftp:
            self.ftp.quit()
            self.ftp=None

    def get_issues(self):
        r = requests.get("http://lo2.opole.pl/gazetka/test/assets/issues.json")
        data = json.loads(r.content)
        for a in data:
            self.issues.append(Issue(a,data[a]['date'],data[a]['nr'],data[a]['pub']))

    def issues_to_json(self):
        ret={}
        for a in self.issues:
            b=a.to_json()
            ret[b[0]] = b[1]
        return json.dumps(ret)

    def upload_issues(self):
        self.start_session()
        self.stop_session()

class NotConfiguredError(Exception):
    def __init__(self):
        super().__init__("Missing tokens.txt")