from argparse import Namespace

from hike.hike import Hike

app = Hike(Namespace(theme="textual-mono", navigation=False, command=["README.md"]))
if __name__ == "__main__":
    app.run()
