libeditor
=========

`libeditor` is a library built around PyQt to quickly create
editor-like programs. 

Main Features
-------------

- QWebView for displaying document contents (HTML)
- Multi-document support with tabs
- Easy to create toolbars and menus
- Actions with built-in support for shorcuts, undo/redo and greying out


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
