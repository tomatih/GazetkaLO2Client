from core import *


def main():
    g = Gazetka()
    g.get_issues()
    print(g.issues)

if __name__ == '__main__':
    main()