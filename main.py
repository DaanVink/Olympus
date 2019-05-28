#TODO: Set up a consistent naming scheme for files, classes and functions
#TODO: find a way to minimize new object creation when calling updateTree()
#TODO: clean up functions and group related code using whitespace
#TODO: comments
#TODO: add detail view for categories with "Rename category", "Delete", etc

from PyQt5 import QtGui, QtWidgets, QtCore, uic
import sys, json, sqlite3

from GUI import contentViews, typeEditor
import settingsHandler

db = sqlite3.connect("data/mainStore.sqlite")

settingsHolder = settingsHandler.Settings(db)
settingsHolder.load()

app = QtWidgets.QApplication(sys.argv)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        uic.loadUi("GUI/main.ui", self)

        self.db = db
        self.cursor = self.db.cursor()

        self.data = {}
        for category in settingsHolder.settings["categories"]:
            query = f"SELECT name, content, type, id FROM data WHERE category == '{category}'"
            self.cursor.execute(query)
            self.data[str(category)] = self.cursor.fetchall()

        self.categoryFilter.addItem("")
        for item in settingsHolder.settings["categories"]:
            self.categoryFilter.addItem(item)
        self.categoryFilter.activated.connect(self.catFilterFunc)

        self.typeFilter.addItem("")
        for item in settingsHolder.settings["types"]:
            self.typeFilter.addItem(item)
        self.typeFilter.activated.connect(self.typeFilterFunc)

        self.searchBox.textChanged.connect(self.onSearchChange)
        self.filter = {"category": "", "type": "", "search": ""}

        self.treeView.setColumnWidth(0, 150)
        self.treeView.setAlternatingRowColors(False)
        self.treeView.expandAll()
        self.treeView.doubleClicked.connect(self.onDoubleClick)
        self.updateTree()

        self.menu = self.menuBar()
        self.addNew = QtWidgets.QAction("New", self)
        self.addNew.triggered.connect(self.addContent)
        self.menu.addAction(self.addNew)

        self.editTypes = QtWidgets.QAction("Types", self)
        self.editTypes.triggered.connect(self.editTypesFunc)
        self.menu.addAction(self.editTypes)

        self.tmp = QtWidgets.QAction("Debug", self)
        self.tmp.triggered.connect(self.tmpFunc)
        self.menu.addAction(self.tmp)

        self.setWindowTitle("Project Olympus")
        self.show()

    def updateTree(self):

        addition = ""
        if self.filter["category"] is not "":
            filteredCategories = [ self.filter["category"] ]
        else:
            filteredCategories = settingsHolder.settings["categories"]
        
        filterType = self.filter["type"] if self.filter["type"] is not "" else ""
        if filterType is not "":
            addition += f" AND type = '{filterType}'"
        if self.filter["search"] is not "":
            search = self.filter["search"]
            addition += f" AND (name LIKE '%{ search }%' or content LIKE '%{ search }%')"

        self.data = {}
        for category in filteredCategories:
            query = f"SELECT name, content, type, id FROM data WHERE category = '{category}'" + addition
            self.cursor.execute(query)
            self.data[str(category)] = self.cursor.fetchall()

        self.model = QtGui.QStandardItemModel()
        self.model.setColumnCount(4)
        self.model.setHorizontalHeaderLabels(["Title", "Notes", "Type", "ID"])

        self.rootNode = self.model.invisibleRootItem()

        self.branches = []
        for x in range(0, len(filteredCategories)):
            category = filteredCategories[x]
            self.branches.append(QtGui.QStandardItem(str(category)))
            for node in range(0, len(self.data[str(category)])):
                currentData = self.data[str(category)][node]
                color = QtGui.QColor(settingsHolder.settings["typeColors"][currentData[2]])
                obj0 = QtGui.QStandardItem(str(currentData[0]))
                obj0.setForeground(color)
                obj1 = QtGui.QStandardItem(str(currentData[1]))
                obj1.setForeground(color)
                obj2 = QtGui.QStandardItem(str(currentData[2]))
                obj2.setForeground(color)
                obj3 = QtGui.QStandardItem(str(currentData[3]))
                obj3.setForeground(color)
                self.branches[x].appendRow([obj0,
                                            obj1,
                                            obj2,
                                            obj3
                                            ])
        
        for branch in self.branches:
            self.rootNode.appendRow( [branch] )
        
        self.treeView.setModel(self.model)
        self.treeView.expandAll()
    
    def addContent(self):
        self.new = contentViews.AddContent(settingsHolder)
        self.new.buttonApply.clicked.connect(self.retrieveNewContent)
    
    def retrieveNewContent(self):
        d = self.new.obj
        try:
            self.cursor.execute("INSERT INTO data(name, content, category, type) VALUES(?,?,?,?)", [d["title"], d["notes"], d["category"], d["type"]])
            self.db.commit()
            self.updateTree()
        except sqlite3.IntegrityError as e:
            print("Not a unique ID")
            print(e)
    
    def catFilterFunc(self, index):
        self.filter["category"] = self.categoryFilter.itemText(index)
        self.updateTree()

    def typeFilterFunc(self, index):
        self.filter["type"] = self.typeFilter.itemText(index)
        self.updateTree()
    
    def onSearchChange(self):
        search = self.searchBox.text()
        self.filter["search"] = search
        self.updateTree()

    def onDoubleClick(self, index):
        id = self.treeView.selectedIndexes()[3].data()
        if id is None:
            pass
        else:
            self.detail = contentViews.ViewContent(settingsHolder, id, self.db, self.cursor)
        self.updateTree()
    
    def editTypesFunc(self):
        self.new = typeEditor.Editor(self.db, self.cursor, settingsHolder.settings["types"])
        self.new.exec() # wait for the dialog to return
        settingsHolder.load()
        self.updateTree()
    
    def tmpFunc(self):
        pass

main = MainWindow(db)
app.exec()
