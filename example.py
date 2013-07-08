from libeditor import MainWindow, Command, Action, Document
import sys, os
from random import choice
from string import ascii_letters

class RemoveCommand(Command):
    def redo(self):
        old_text = self.doc.text() 
        self.char = old_text[-1]
        self.doc.setHtml(old_text[:-1])

    def undo(self):
        self.doc.setHtml(self.doc.text() + self.char)

class ReverseCommand(Command):
    def redo(self):
        self.old_text = self.doc.text()
        self.doc.setHtml(''.join(reversed(self.old_text)))

    def undo(self):
        self.doc.setHtml(self.old_text)

class InsertRandomCommand(Command):
    def __init__(self, *args):
        super(InsertRandomCommand, self).__init__(*args)
        self.char = choice(ascii_letters)

    def redo(self):
        self.doc.setHtml(self.doc.text() + self.char)

    def undo(self):
        self.doc.setHtml(self.doc.text()[:-1])


def main():
    main_window = MainWindow('Example Application')

    def open_help(doc):
        message = 'Click on the toolbars and try Ctrl+Z and Ctrl+Shift+Z.'
        main_window.addDocument(Document('Help', message))
    main_window.addToolbar('Help Toolbar', [Action(open_help, 'Help')])

    random_action = Action(InsertRandomCommand, label='Insert Random',
                           is_available=lambda d: d)
    remove_action = Action(RemoveCommand, label='Remove',
                           is_available=lambda d: d and len(d.text()) >= 1)
    reverse_action = Action(ReverseCommand, label='Reverse',
                            is_available=lambda d: d and len(d.text()) >= 2)

    actions = [random_action, reverse_action, remove_action]
    main_window.addToolbar('Toolbar', actions)
    main_window.addDocument(Document('My Empty Document', ''))
    main_window.run()

if __name__ == '__main__':
    main()
