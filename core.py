import json
import requests
from ftplib import FTP
import os.path


class Article:
    """A data class for storing information about a single Article"""

    def __init__(self, title=None, image=None, text=None):
        self.title = title
        self.cover_image = image
        self.content = text

    def __str__(self):
        return f"Article titled {self.title} cover status {bool(self.cover_image)}"

    def __repr__(self):
        return f"Article titled {self.title} cover status {bool(self.cover_image)}"

    def to_dict(self):
        return {"title": self.title, "image": self.cover_image, "text": self.content}


class Issue:
    """A data class for storing information about a single Issue"""

    def __init__(self, date, nr, pub):
        self.index = None
        self.year = date
        self.number = nr
        self.pub = pub
        self.articles = dict()

    def __str__(self):
        return f'Issue {self.number} {self.year}/{self.year + 1} Index: {self.index} Published: {self.pub}'

    def __repr__(self):
        return f'Issue {self.number} {self.year}/{self.year + 1} Index: {self.index} Published: {self.pub}'

    def to_dict(self):
        return {'date': self.year, 'nr': self.number, 'pub': self.pub}

    def populate_articles(self):
        r = requests.get(f"http://lo2.opole.pl/gazetka/test/assets/articles/{self.index}.json")
        data = json.loads(r.content)
        r.close()
        for k in data:
            self.articles[k] = Article(**data[k])


class Gazetka:

    def __init__(self):
        self._ftp = None
        self.issues = dict()
        if not os.path.isfile('tokens.txt'):
            raise NotConfiguredError

    def _start_session(self):
        try:
            self._ftp = FTP('www.lo2.opole.pl')
            with open('tokens.txt', 'r') as f:
                tokens = f.read()
                tokens = tokens.split('\n')
                self._ftp.login(tokens[0], tokens[1])
        except Exception as e:
            print(e)

    def _end_session(self):
        if self._ftp:
            self._ftp.quit()
            self._ftp = None

    def get_issues(self, with_articles=False):
        r = requests.get("http://lo2.opole.pl/gazetka/test/assets/issues.json")
        data = json.loads(r.content)
        r.close()
        for a in data:
            i = Issue(**data[a])
            i.index = a
            if with_articles:
                i.populate_articles()
            self.issues[a] = i

    def issues_to_dict(self):
        r = {}
        for k in self.issues:
            r[k] = self.issues[k].to_dict()
        return r

    def articles_to_dict(self, nr):
        nr = str(nr)
        r = {}
        for k in self.issues[nr].articles:
            r[k] = self.issues[nr].articles[k].to_dict()
        return r

    def _upload_helper(self, data, path, name):
        with open("tmp.json", 'w') as f:
            json.dump(data, f)
        self._start_session()
        self._ftp.cwd(path)
        with open("tmp.json", 'rb') as f:
            self._ftp.storbinary(f'STOR {name}.json', f)
        self._end_session()
        os.remove("tmp.json")

    def upload_issues(self):
        if self.issues == dict():
            print("No changes detected")
            return
        self._upload_helper(self.issues_to_dict(), "test/assets", 'issues')

    def upload_articles(self, nr):
        nr = str(nr)
        if nr not in self.issues or self.issues[nr].articles == dict():
            print("No changes detected")
            return
        self._upload_helper(self.articles_to_dict(nr), "test/assets/articles", nr)


class NotConfiguredError(Exception):
    def __init__(self):
        super().__init__("Missing tokens.txt")
