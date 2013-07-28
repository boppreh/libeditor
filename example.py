from random import choice
from string import ascii_letters

# These are the imports that matter.
from libeditor import MainWindow, Command, Action, Document

# Commands define instances of actions, and can be undone and redone.
class InsertRandomCommand(Command):
    # It's important to receive the constructor args and repass them to the
    # superclass. We are expecting a reference to the document here, which
    # will be saved in `self.doc`.
    def __init__(self, *args):
        super(InsertRandomCommand, self).__init__(*args)
        self.char = choice(ascii_letters)

    def redo(self):
        self.doc.contents += self.char

    def undo(self):
        self.doc.contents = self.doc.contents[:-1]

class RemoveCommand(Command):
    # We don't need to set anything in the constructor, so we use the default
    # one from the superclass.
    def redo(self):
        old_text = self.doc.contents
        self.char = old_text[-1]
        self.doc.contents = old_text[:-1]

    def undo(self):
        self.doc.contents += self.char

class ReverseCommand(Command):
    def redo(self):
        self.old_text = self.doc.contents
        self.doc.contents = ''.join(reversed(self.old_text))

    def undo(self):
        self.doc.contents = self.old_text


def main():
    # Only the MainWindow needs to be created. The rest of the application is
    # setup automatically.
    main_window = MainWindow('Example Application')

    # Helper function that opens a new document with a help message.
    def open_help(doc):
        message = 'Click on the toolbars and try Ctrl+Z and Ctrl+Shift+Z.'
        main_window.addDocument(Document(message, 'Help'))

    # Defines an Action with name and associated function.
    help_ = Action(open_help, 'Help')

    # Similar to the help function, but using a simple lambda to shave off the
    # first argument.
    new = Action(lambda d: main_window.newDocument(), 'New')
    open_ = Action(lambda d: main_window.openDocument(), 'Open')
    quit = Action(lambda d: exit(), 'Quit')

    # Actions that create Commands. `is_available` evaluates if the action
    # should be enabled or not at a given time.
    random = Action(InsertRandomCommand, label='Insert Random',
                    is_available=lambda d: d)
    remove = Action(RemoveCommand, label='Remove',
                    is_available=lambda d: d and len(d.contents) >= 1)
    reverse = Action(ReverseCommand, label='Reverse',
                     is_available=lambda d: d and len(d.contents) >= 2)

    # Creates a new toolbar with the three Actions created above.
    main_window.addToolbar('Toolbar', [random, reverse, remove])
    # Same with the help action.
    main_window.addToolbar('Help Toolbar', [help_])
    # Adding a menu is exactly like adding a toolbar.
    main_window.addMenu('File', [new, open_, None, quit])

    # Creates a new empty document with a given title.
    main_window.addDocument(Document('', 'My Empty Document'))

    # Shows the main window and starts the event loop.
    main_window.run()

if __name__ == '__main__':
    main()
