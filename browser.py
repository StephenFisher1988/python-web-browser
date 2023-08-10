import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set the window title and (optionally) an icon for the browser window
        self.setWindowTitle("MyBrowser")
        self.setWindowIcon(QIcon('path_to_icon.png'))  # Replace 'path_to_icon.png' with your actual path
        
        # Initialize a tabbed interface for browsing
        self.tabs = QTabWidget()
        
        # Enable advanced tab features
        self.tabs.setDocumentMode(True)
        
        # Connect tab events to their respective functions
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)

        # Set the tabs as the central widget of the window
        self.setCentralWidget(self.tabs)

        # Create a status bar (optional, can be used to show loading status, etc.)
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Create a navigation toolbar for URL entry, back/forward buttons, etc.
        navtb = QToolBar("Navigation")
        self.addToolBar(navtb)
        
        # Add a URL input bar to the navigation toolbar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)  # Connect the URL bar's enter/return event
        navtb.addWidget(self.url_bar)

        # Create and add a "New Tab" button to the navigation toolbar
        new_tab_action = QAction(QIcon('path_to_icon.png'), "New Tab", self)  # Replace 'path_to_icon.png' with your actual path
        new_tab_action.triggered.connect(self.add_new_tab)
        navtb.addAction(new_tab_action)
        
        # Add a '+' tab that allows users to open new tabs
        self.tabs.addTab(QWidget(), "+")
        self.add_new_tab(QUrl('http://www.startpage.com'), 'Homepage')  # Open a default start page

    def add_new_tab(self, qurl=None, label="Blank"):
        """Open a new browser tab. Load a default page if no URL is provided."""
        if qurl is None:
            qurl = QUrl('http://www.startpage.com')
    
        browser = QWebEngineView()
        browser.setUrl(qurl)
        
        # Insert this tab right before the '+' tab
        i = self.tabs.insertTab(self.tabs.count() - 1, browser, label)
        self.tabs.setCurrentIndex(i)
        
        # Connect browser signals to update the UI accordingly
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()))

    def tab_open_doubleclick(self, i):
        """Open a new tab on double-click on the tab bar."""
        if i == -1:
            return
        if self.tabs.tabText(i) != "+":
            self.add_new_tab()

    def current_tab_changed(self, i):
        """Handles the tab change event."""
        # If '+' is clicked, open a new tab
        if self.tabs.tabText(i) == "+" and i == self.tabs.count() - 1:
            self.add_new_tab()
            self.tabs.setCurrentIndex(self.tabs.count() - 2)  # Switch to the new tab
            return

        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        """Close the current tab."""
        if self.tabs.tabText(i) == "+":
            return
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def update_title(self, browser):
        """Update the window title based on the browser's current page title."""
        title = browser.page().title()
        self.setWindowTitle("% s - MyBrowser" % title)

    def update_urlbar(self, q, browser=None):
        """Update the URL bar to the current page's URL."""
        if not hasattr(self, 'url_bar') or browser != self.tabs.currentWidget():
            return
        self.url_bar.setText(q.toString())
        self.url_bar.setCursorPosition(0)

    def navigate_to_url(self):
        """Navigate to the URL specified in the URL bar."""
        if not hasattr(self, 'url_bar'):
            return
        q = QUrl(self.url_bar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.tabs.currentWidget().setUrl(q)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName("MyBrowser")
    window = Browser()
    sys.exit(app.exec_())
