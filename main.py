from src.config._container import Application
from bootstrap import bootstrap


def main():
    app = Application()
    bootstrap(app)


if __name__ == "__main__":
    main()
