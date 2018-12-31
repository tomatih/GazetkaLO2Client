from core import Gazetka


def main():
    g = Gazetka()
    g.get_issues(True)
    print(g.issues)
    for k in g.issues:
        print(g.issues[k].articles)


if __name__ == '__main__':
    main()
