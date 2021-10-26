from panda3d import core

core.load_prc_file_data("", "direct-gui-edit #t")

from wood_framer.main import main

if __name__ == "__main__":
    main(True)
