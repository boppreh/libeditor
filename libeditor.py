from PyQt4 import QtCore, QtGui, QtWebKit


class Action(QtGui.QAction):
    """
    Class for Actions that can be displayed on toolbars and menus, triggered
    by hotkey and undone/redone.
    """
    def __init__(self, label, redo, undo=None, hotkey=None, is_available=None):
        QtGui.QAction.__init__(self, label, None)
        self.redo = redo
        self.undo = undo
        self.hotkey = hotkey
        self.finished_setup = False
        self.is_available = is_available or (lambda: True)

    def setup(self, parent):
        if self.finished_setup:
            return
        self.finished_setup = True

        if self.undo:
            def execute():
                parent.currentDocument().undo_stack.push(self.command())
        else:
            execute = self.redo

        self.triggered.connect(execute)
        if self.hotkey:
            QtGui.QShortcut(self.hotkey, parent, execute)

    def command(self):
        command = QtGui.QUndoCommand(self.text(), None)
        command.redo = self.redo
        command.undo = self.undo
        return command 


class Tabbed(QtGui.QTabWidget):
    """
    Tabbed interface with focus on usability:
    - tabs can be moved
    - the currently focused tab has a close button
    - Ctrl+W closes the current tab
    - the user can middle-click on a tab to close it
    - the tab bar is hidden when there's only one tab
    - when a tab is open, change to it
    """
    def __init__(self, *args, **kargs):
        QtGui.QTabWidget.__init__(self, *args, **kargs)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.currentChanged.connect(self._update_tab)
        self.tabCloseRequested.connect(self._close_tab)
        QtGui.QShortcut('Ctrl+W', self,
                        lambda: self._close_tab(self.currentIndex()))

    def _update_tab(self, new_tab=None):
        self.setCurrentIndex(new_tab)
        for i in range(self.count()):
            button = self.tabBar().tabButton(i, QtGui.QTabBar.RightSide)
            if button:
                button.setVisible(i == new_tab)

        self.tabBar().setVisible(self.count() > 1)

    def _close_tab(self, tab):
        self.removeTab(tab)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self._close_tab(self.tabBar().tabAt(event.pos()))

        QtGui.QTabWidget.mouseReleaseEvent(self, event)

    def addTab(self, widget, title):
        self._update_tab(QtGui.QTabWidget.addTab(self, widget, title))


class MainWindow(QtGui.QMainWindow):
    """
    Class for a multi-document window, if automatic handling of actions and
    tabs.
    """
    def __init__(self, title):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle(title)
        self.setCentralWidget(Tabbed())

        self.untitled_count = 0
        self.actions = set()

        QtGui.QShortcut('Ctrl+N', self, self.newDocument)
        QtGui.QShortcut('Ctrl+Z', self,
                        lambda: self.currentDocument().undo_stack.undo())
        QtGui.QShortcut('Ctrl+Shift+Z', self,
                        lambda: self.currentDocument().undo_stack.redo())

    def addMenu(self, menu_name, actions):
        """
        Creates a new menu with a list of actions.
        """
        self._addActions(self.menuBar().addMenu(menu_name), actions)

    def addToolbar(self, toolbar_name, actions):
        """
        Creates a new toolbar with a list of actions.
        """
        self._addActions(self.addToolBar(toolbar_name), actions)

    def _addActions(self, bar, actions):
        """
        Adds a list of actions to a (menu|tool)bar.
        """
        for action in actions:
            if action is None:
                bar.addSeparator()
                continue

            self.actions.add(action)
            bar.addAction(action)
            action.setup(self)

    def addDocument(self, text, label=None):
        """
        Opens a new document in a new tab, displaying the given text as HTML.
        """
        if label is None:
            self.untitled_count += 1
            label = 'Untitled Document ' + str(self.untitled_count)

        contents = QtWebKit.QWebView()
        contents.setHtml(text)
        contents.undo_stack = QtGui.QUndoStack()
        self.centralWidget().addTab(contents, label)
        return contents

    def newDocument(self):
        """
        Opens a new empty document in a new tab.
        """
        return self.addDocument('', None)

    def currentDocument(self):
        """
        Returns the currently focused HTML widget.
        """
        return self.centralWidget().currentWidget()

    def refresh(self):
        for action in self.actions:
            action.setEnabled(action.is_available())


if __name__ == '__main__':
    import sys, os
    app = QtGui.QApplication([__file__])
    main_window = MainWindow('Structured Editor')

    def p(s):
        def print_():
            print(s)
        return print_ 

    actions = [
               Action('A1', p('did a1'), hotkey='1'),
               None,
               Action('A2', p('did a2'), p('undid a2'), hotkey='2'),
               Action('A3', p('did a3'), p('undid a3'), hotkey='3'),
               Action('A4', p('did a4'), p('undid a4'), hotkey='4'),
               Action('A5', p('did a5'), p('undid a5'), hotkey='5'),
               None,
               Action('Disable', main_window.refresh),
              ]

    main_window.addToolbar('Toolbar 1', actions)

    for path in sys.argv[1:]:
        main_window.add(open(path).read(), os.path.basename(path))

    main_window.show()
    exit(app.exec_())
