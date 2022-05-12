from src.gui.window import MainWindow
from dotenv import load_dotenv


def main():
    load_dotenv()
    window = MainWindow()
    window.launch()


if __name__ == '__main__':
    main()
