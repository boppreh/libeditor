from PyQt4 import QtCore, QtGui, QtWebKit
import re

class Document(QtWebKit.QWebView):
    """
    Document with HTML display.
    """
    untitled_count = 0

    def __init__(self, title=None, contents=''):
        QtWebKit.QWebView.__init__(self)
        self.setHtml(contents)

        if title is None:
            Document.untitled_count += 1
            title = 'Untitled Document ' + str(self.untitled_count)

        self.title = title
        self.undo_stack = QtGui.QUndoStack()

    def refresh(self):
        pass


class Action(QtGui.QAction):
    """
    Class for Actions that can be displayed on toolbars and menus and triggered
    by shortcut.
    """
    def __init__(self, function, label=None, shortcut=None, is_available=None):
        if label is None:
            fname = function.__name__
            words = re.sub('([A-Z])', r' \1', fname).replace('_', ' ')
            label = words.strip().title()
        self.function = function
        self.is_available = is_available or (lambda doc: True)

        QtGui.QAction.__init__(self, label, None)
        self.triggered.connect(self.execute)

        if shortcut is not None:
            self.setShortcut(shortcut)

    def execute(self):
        document = self.parent().currentDocument()
        result = self.function(document)
        if isinstance(result, QtGui.QUndoCommand):
            document.undo_stack.push(result)
        self.parent().refresh()

    def refresh(self):
        """
        Updates the availability of this action.
        """
        doc = self.parent().currentDocument()
        self.setEnabled(bool(self.is_available(doc)))


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
        self.parent().refresh()

    def _close_tab(self, tab):
        self.removeTab(tab)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self._close_tab(self.tabBar().tabAt(event.pos()))

        QtGui.QTabWidget.mouseReleaseEvent(self, event)

    def addTab(self, widget, title):
        self._update_tab(QtGui.QTabWidget.addTab(self, widget, title))

    def title(self):
        return self.tabText(self.currentIndex())


class MainWindow(QtGui.QMainWindow):
    """
    Class for a multi-document window, if automatic handling of actions and
    tabs.
    """
    def __init__(self, title):
        self.app = QtGui.QApplication([__file__])

        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle(title)
        self.setCentralWidget(Tabbed())

        self.base_title = title
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
        menu = self.menuBar().addMenu(menu_name)
        self._addActions(menu, actions)
        return menu

    def addToolbar(self, toolbar_name, actions):
        """
        Creates a new toolbar with a list of actions.
        """
        toolbar = self.addToolBar(toolbar_name)
        toolbar.setObjectName(toolbar_name)
        self._addActions(toolbar, actions)
        return toolbar

    def _addActions(self, bar, actions):
        """
        Adds a list of actions to a (menu|tool)bar.
        """
        for action in actions:
            if action is None:
                bar.addSeparator()
                continue

            bar.addAction(action)
            self.actions.add(action)
            action.setParent(self)

    def addDocument(self, document):
        """
        Opens a new document in a new tab, displaying the given text as HTML.
        """
        self.centralWidget().addTab(document, document.title)
        self.refresh()

    def newDocument(self):
        """
        Opens a new empty document in a new tab.
        """
        return self.addDocument(Document())

    def currentDocument(self):
        """
        Returns the currently focused HTML widget.
        """
        return self.centralWidget().currentWidget()

    def refresh(self):
        """
        Updates the title and action availability.
        """
        if self.currentDocument():
            self.currentDocument().refresh()
            title = '{} - {}'.format(self.centralWidget().title(),
                                     self.base_title)
            self.setWindowTitle(title)
        else:
            self.setWindowTitle(self.base_title)

        for action in self.actions:
            action.refresh()

    def loadState(self):
        settings = QtCore.QSettings(self.base_title, '')
        self.restoreGeometry(settings.value('geometry').toByteArray())
        self.restoreState(settings.value('state').toByteArray())

    def closeEvent(self, event):
        settings = QtCore.QSettings(self.base_title, '')
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('state', self.saveState())
        QtGui.QMainWindow.closeEvent(self, event)

    def run(self):
        self.loadState()
        self.show()
        self.refresh()
        exit(self.app.exec_())



if __name__ == '__main__':
    import sys, os
    main_window = MainWindow('Structured Editor')

    class ClearCommand(QtGui.QUndoCommand):
        def __init__(self, doc):
            QtGui.QUndoCommand.__init__(self)
            self.doc = doc
            self.old_text = doc.page().mainFrame().toHtml()

        def redo(self):
            self.doc.setHtml('')

        def undo(self):
            self.doc.setHtml(self.old_text)

    class InsertCommand(QtGui.QUndoCommand):
        def __init__(self, doc):
            QtGui.QUndoCommand.__init__(self)
            self.doc = doc
            self.old_text = doc.page().mainFrame().toHtml()

        def redo(self):
            self.doc.setHtml(self.old_text + '\nNew line.')

        def undo(self):
            self.doc.setHtml(self.old_text)

    clear_action = Action(ClearCommand, is_available=lambda d: d)
    insert_action = Action(InsertCommand, is_available=lambda d: d)
    main_window.addToolbar('Toolbar 1', [clear_action, insert_action])

    for path in sys.argv[1:]:
        main_window.addDocument(Document(open(path).read(),
                                         os.path.basename(path)))

    main_window.run()
