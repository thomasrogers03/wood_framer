from . import app


def main(debug_gui: bool):
    app.App(debug_gui).run()
