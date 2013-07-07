libeditor
=========

`libeditor` is a library built around PyQt to quickly create
editor-like programs. 

Main Features
-------------

- QWebView for displaying the contents (HTML)
- Multi-document support with tabs
- Easy to create toolbars and menus
- Actions have built-in support for shorcuts and undo/redo


Detailed Features
----------------

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
  - Documents can be opened by giving only the HTML and a label
  - Current QWebView widget can be accessed for easy modifications
  - Easy to add new toolbars and menus with their actions
  - Title displays the current document name
  - "App" object is created automatically
  - Window size, position and toolbars are saved and loaded automatically
  
- Actions
  - Support for label, redo and undo functions
  - Ctrl+Z and Ctrl+Shift+Z automatically undo and redo the last actions
  - Undo stack is kept in a per-document basis
  - Actions can have shortcuts
  - Empty actions are rendered as separators
  - Actions without undo are considered global
  - Availability defined by user-supplied function and automatically refreshed
