from PyQt4 import QtCore, QtGui, QtWebKit
import re, os

class Document(QtWebKit.QWebView):
    """
    Document with HTML display.
    """
    untitled_count = 0

    def __init__(self, contents='', path=None):
        QtWebKit.QWebView.__init__(self)
        self.contents = contents
        self.undo_stack = QtGui.QUndoStack()
        self.filetype = '*.*'

        self.path = path
        if path is not None:
            self.title = os.path.basename(path)
            self.filetype = '*' + os.path.splitext(self.path)[1]
        else:
            Document.untitled_count += 1
            self.title = 'Untitled Document ' + str(self.untitled_count)        
            self.filetype = '*.*'

    def refresh(self):
        """
        Updates the document after a command has been executed.
        """
        self.setHtml(self.contents)

    def save(self):
        """
        Saves the document content to the original file, or opens a file dialog
        if there was no original file. Marks the document as clean and allows
        the tab to be closed without confirmation.
        """
        if not self.filepath:
            return self.save_as()

        if self.filepath:
            with open(self.filepath, 'w') as f:
                f.write(str(self.contents))

            self.undo_stack.setClean()
            return True
        else:
            return False

    def save_as(self):
        """
        Saves the document content to the original file, or opens the file
        dialog is none is given.
        """
        self.filepath = str(QtGui.QFileDialog.getSaveFileName(self, 'Save as',
                                                              self.title,
                                                              filter=self.filetype))
        return self.save()

    def _confirm_unsaved_changes(self):
        message = 'Do you want to save changes to {}?'.format(self.title)
        buttons = QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard | QtGui.QMessageBox.Cancel
        result = QtGui.QMessageBox.warning(self, 'Close confirmation', message, buttons=buttons)

        if result == QtGui.QMessageBox.Save:
            return self.save()
        elif result == QtGui.QMessageBox.Discard:
            return True
        elif result == QtGui.QMessageBox.Cancel:
            return False

    def close(self):
        """
        Attempts to close the document, possibly asking the user for
        confirmation. Should return whether the document could be closed or
        not.
        """
        return self.undo_stack.isClean() or self._confirm_unsaved_changes()


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


class Command(QtGui.QUndoCommand):
    """
    Class for actions performed that can be undone and redone.
    """
    def __init__(self, doc):
        QtGui.QUndoCommand.__init__(self)
        self.doc = doc

    def redo(self):
        raise NotImplemented()

    def undo(self):
        raise NotImplemented()


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
        if self.widget(tab).close():
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
    def __init__(self, title, document_class=Document):
        """
        Creates a new Main Window with a given title to edit documents of type
        `document_class` that extends libeditor.Document.
        """
        self.app = QtGui.QApplication([__file__])
        self.document_class = document_class

        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle(title)
        self.setCentralWidget(Tabbed())

        self.base_title = title
        self.actions = set()

        QtGui.QShortcut('Ctrl+Z', self, self.undo)
        QtGui.QShortcut('Ctrl+Shift+Z', self, self.redo)

    def undo(self):
        self.currentDocument().undo_stack.undo()
        self.refresh()

    def redo(self):
        self.currentDocument().undo_stack.redo()
        self.refresh()

    def addFileMenu(self):
        """
        Adds a standard "File" menu with New, Open, Save, Save as and Quit
        actions.
        """
        actions = [
            Action(lambda d: self.newDocument(), '&New', 'Ctrl+N'),
            Action(lambda d: self.openDocument(), '&Open...', 'Ctrl+O'),
            None,
            Action(lambda d: d.save(), '&Save', 'Ctrl+S', lambda d: d),
            Action(lambda d: d.save_as(), 'Save &as...', 'Ctrl+Alt+S', lambda d: d),
            None,
            Action(lambda d: exit(), '&Quit', 'Ctrl+Q'),
        ]
        self.addMenu('&File', actions)

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

    def openDocument(self):
        """
        Prompts the user to select a file location to open in a new document.
        """
        path = str(QtGui.QFileDialog.getOpenFileName(self, filter='*.*'))
        if path is not None:
            document = self.document_class(open(path).read(), path)
            self.addDocument(document)

    def newDocument(self):
        """
        Opens a new empty document in a new tab.
        """
        return self.addDocument(self.document_class())

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
        geometry, state = settings.value('geometry'), settings.value('state')
        if geometry:
            self.restoreGeometry(geometry)
        if state:
            self.restoreState(state)

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
    import example
    example.main()
