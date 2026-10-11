import flet as ft
import config
from ui import UI

def main():
    ui = UI()
    ft.app(target=ui.start if config.first_time else ui.main)

if __name__ == "__main__":
    main()