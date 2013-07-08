libeditor
=========

`libeditor` is an architecture for building document editors. It strives to
automatically provide functionality that a user might expect of such programs,
such as undo/redo, interface customization, hotkey support and persistent
configuration.


Features
---------

- QWebView for displaying document contents (HTML)
- Multi-document support with tabs
- Easy to create toolbars and menus
- Actions with built-in support for shorcuts, undo/redo and greying out


Architecture
------------

The architecture is based on four concepts:

- `Document` is the class that contains the data to be edited. It is a `QWidget`
  object (by default `QWebView`), and it has a title, an `undo_stack` and a
  `refresh()` method.

- `Action` encapsulates a possible user action, such as opening a new document
  or inserting something in the current one. It has a `label` and `shortcut`, 
  allowing it to be placed in menus or toolbars, where its availability (greyed
  out or not) is defined by the parameter `is_available(doc)`. Its main
  `function(doc)` may execute the action directly or return a `Command` to do
  so.

- `Command` is an action executed upon a specific document. The user must
  extend the class and override its `redo()` and `undo()` methods.

- `MainWindow` contains zero or more `Document`s displayed in tabs, toolbars
  and menus containing `Action`s and supports opening new documents, redoing
  and undoing commands out of the box.


Detailed behavior
-----------------

- Tabs
  - Tabs can be reordered by dragging
  - The currently focused tab has a close button (like Firefox)
  - Ctrl+W closes the current tab
  - Middle click closes the clicked tab
  - Tab bar is hidden when there's only one document
  - Automatically focus on newly opened tabs
  
- Main Window
  - Empty documents can be created with Ctrl+N
  - Unnamed documents are labeled "Untitled Document x"
  - Easy to add new toolbars and menus with their actions
  - Title displays the current document name
  - "App" object is created automatically
  - Window size, position and toolbars are saved and loaded automatically
  
- Actions
  - Can contain a label
  - Support for redo and undo functions
  - Receives an availability function and refreshes automatically
  - Can have shortcuts
  - Ctrl+Z and Ctrl+Shift+Z automatically undo and redo the last actions
  - Undo stack is kept in a per-document basis
  - Actions without undo are considered global
  - 'None' actions are rendered as separators in toolbars and menus

- Document
  - Has a title, filepath and filetype
  - Contains its own undo stack
  - Keeps track of which executed commands were saved (clean) or not
  - Asks for confirmation when closing with unsaved changes
  - Save and save-as work as expected


Future features
---------------

- Implement open/save/saveas, going through a user supplied function
- Support toolbars with variable number of actions
- Enable default menus (File, Edit)
- Macro support? Technically the undo_stack already has it
- Status bar?
- Auto updater?
- Reset geomtry/state?
