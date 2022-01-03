from main_demineur import demineur
from main_terminalFunctions import clear
from main_countlignes import count_number_of_lines_in_file, count_number_of_lines_in_folder
import os

helpmenu = """
--help: Affiche ceci\n
--gui: Affiche une interface graphique avec GTK3
--cli: En ligne de commande
--tli: Affiche une interface en ligne de commande

"""


def launch():
    print("---")
    print("1: demineur terminal")
    print("2: conter le nombre de lignes")
    print("3: graphical demineur")
    print("4: terminal snake")
    print("---")
    menu = input("Menu: ")
    # TODO match
    if menu == "1":
        clear()
        demineur()
    if menu == "2":
        print("---")
        print("1: file")
        print("2: folder")
        print("---")
        menu = input("Menu : ")
        if menu == "1":
            print(count_number_of_lines_in_file(input("Nom de fichier: ")))
        if menu == "2":
            print("---")
            print("1: match")
            print("2: all match at racine")
            print("---")
            menu = input("Menu : ")
            if menu == "1":
                count_number_of_lines_in_folder(input("folder"), input("match"))
            elif menu == "2":
                print("DOSSIER " + str(os.getcwd()) + "/../")
                print("All Ext\t", count_number_of_lines_in_folder("../", "(.py$|.md$|.png$|.txt$|LICENCE|.json$)"),
                      "\t Pour être plus précis: (.py$|.md$|.png$|.txt$|LICENCE|.json$)")
                print("py$ md$\t", count_number_of_lines_in_folder("../", "(.py$|.md$)"))
                print("py$\t", count_number_of_lines_in_folder("../", ".py$"))
    if menu == "3":
        import main_minesweeper
        import os
        os.chdir("./resources")
        main_minesweeper.Main.start()
    if menu == "4":
        import main_terminalsnake
        debug = False
        main_terminalsnake.main()


def clilaunch():
    """
    # TODO, Apps a faire: 
    autoreadme, compressint, countligne, ?duplicateFile, keyboardGenerator, minesweeper, readmereader, getbyteskey, tetris
    """
    from main_terminalGetKey import getKey
    global current_menu  # 0 = Normal, 1=CountLine,
    current_menu = 0  # 0 = Normal, 1=CountLine,
    Apps_to_launch = [
        {
            '0': ('demineur', lambda: demineur()),
            '1': ('menu count ligne', lambda: change_current_menu(1))
        },
        {
            '0': ('print ok', lambda: print("ok")),
            '1': ('print okj2', lambda: print('ojk2'))
        }
    ]
    while True:
        # TODO Afficher les aides
        key = getKey(debug=True)
        if key in Apps_to_launch[current_menu]:
            clear()
            Apps_to_launch[current_menu][key][1]()
        else:
            print("Commande Inconnue")
        print(current_menu)


def change_current_menu(x):
    global current_menu
    current_menu = x


def guilaunch():
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk

    def on_activate(app):
        win = Gtk.ApplicationWindow(application=app)
        btn = Gtk.Button(label="Hello, World!")
        btn.connect('clicked', lambda x: win.close())
        win.add(btn)
        win.show_all()

    app = Gtk.Application(application_id='org.gtk.Example')
    app.connect('activate', on_activate)
    app.run(None)


if __name__ == "__main__":
    import sys

    args = sys.argv
    if "--help" in args:
        print(helpmenu)
    elif "--gui" in args:
        guilaunch()
    elif "--cli" in args:
        clilaunch()
    else:
        launch()
