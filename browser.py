import sys
import os
import importlib
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
MODULES_PATH = os.path.join(script_dir, "modules")

class CustomTabBar(QTabBar):
    def wheelEvent(self, event): pass
    def tabSizeHint(self, index):
        size = super().tabSizeHint(index)
        size.setWidth(min(size.width(), 150))
        return size

    def paintEvent(self, event):
        painter = QStylePainter(self)
        option = QStyleOptionTab()
        for index in range(self.count()):
            self.initStyleOption(option, index)
            option.text = self.tabText(index)
            painter.drawControl(QStyle.CE_TabBarTabShape, option)
            painter.drawControl(QStyle.CE_TabBarTabLabel, option)

class CustomComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.placeholder = "≡"
        self.addItem(self.placeholder)
        self.currentIndexChanged.connect(self.on_item_selected)

    def showPopup(self):
        if self.currentText() == self.placeholder:
            self.setCurrentIndex(-1)
        super().showPopup()

    def hidePopup(self):
        if self.currentIndex() == -1:
            self.setCurrentIndex(self.findText(self.placeholder))
        super().hidePopup()

    def on_item_selected(self, index):
        if index != 0:
            self.setCurrentIndex(0)

class CustomTabBarWithDropdown(CustomTabBar):
    def __init__(self):
        super().__init__()
        self.comboBox = CustomComboBox(self)
        self.comboBox.move(self.width() - self.comboBox.width(), 0)
    def resizeEvent(self, event):
        self.comboBox.move(self.width() - self.comboBox.width(), 0)

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MyBrowser")
        self.setWindowIcon(QIcon('path_to_icon.png'))
        self.setupUI()
        self.modules = self.load_modules_into_dropdown()
        self.showMaximized()

    def setupUI(self):
        self.tabs = QTabWidget(self)
        self.tabs.setTabBar(CustomTabBarWithDropdown())
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        navtb = QToolBar("Navigation")
        self.url_bar = QLineEdit(self)
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.url_bar)
        new_tab_action = QAction(QIcon('path_to_icon.png'), "New Tab", self)
        new_tab_action.triggered.connect(self.add_new_tab)
        navtb.addAction(new_tab_action)
        self.tabs.addTab(QWidget(), "+")
        layout = QVBoxLayout()
        layout.addWidget(navtb)        
        layout.addWidget(self.tabs)
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.add_new_tab(QUrl('http://www.startpage.com'), 'Homepage')

    def add_new_tab(self, qurl=None, label="Blank"):
        if qurl is None: qurl = QUrl('http://www.startpage.com')
        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.insertTab(self.tabs.count() - 1, browser, label)
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.tabs.setTabText(i, browser.page().title()[:15] + "..."))

    def tab_open_doubleclick(self, i):
        if i != -1 and self.tabs.tabText(i) == "+": self.add_new_tab()

    def current_tab_changed(self, i):
        if self.tabs.tabText(i) == "+" and i == self.tabs.count() - 1:
            self.add_new_tab()
            self.tabs.setCurrentIndex(self.tabs.count() - 2)

    def close_current_tab(self, i):
        if self.tabs.tabText(i) != "+" and self.tabs.count() > 2: self.tabs.removeTab(i)

    def update_urlbar(self, q, browser=None):
        if hasattr(self, 'url_bar') and browser == self.tabs.currentWidget():
            self.url_bar.setText(q.toString())

    def navigate_to_url(self):
        q = QUrl(self.url_bar.text())
        if not q.scheme(): q.setScheme("http")
        self.tabs.currentWidget().setUrl(q)

    def load_modules_into_dropdown(self):
        modules = {}
        for module_file in [f[:-3] for f in os.listdir(MODULES_PATH) if f.endswith('.py') and not f.startswith('__init__')]:
            module = importlib.import_module(f"modules.{module_file}")
            if hasattr(module, "get_module_name"):
                self.tabs.tabBar().comboBox.addItem(module.get_module_name())
                modules[module.get_module_name()] = module
        self.tabs.tabBar().comboBox.activated[str].connect(self.execute_selected_module)
        return modules

    def execute_selected_module(self, module_name):
        module = self.modules.get(module_name)
        if module and hasattr(module, "execute_module_function"): module.execute_module_function()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setApplicationName("MyBrowser")
    window = Browser()
    sys.exit(app.exec_())
