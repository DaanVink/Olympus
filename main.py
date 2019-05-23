#TODO: Set up a consistent naming scheme for files, classes and functions

from PyQt5 import QtGui, QtWidgets, QtCore, uic
import sys
import json
import sqlite3

db = sqlite3.connect("data/mainStore.sqlite")

from GUI import newContent, detailContent
import settingsHandler

settingsHolder = settingsHandler.Settings()

app = QtWidgets.QApplication(sys.argv)

class Item():
    def __init__(self, title, content, category, type):
        self.title = title
        self.content = content
        self.category = category
        self.type = type
        
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.cursor = self.db.cursor()

        uic.loadUi("GUI/main.ui", self)

        self.buttonNew.clicked.connect(self.addContent)

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

        self.updateTree()

        self.treeView.doubleClicked.connect(self.onDoubleClick)

    def updateTree(self):

        if self.filter["category"] is not "":
            filteredCategories = [ self.filter["category"] ]
            print("test")
        else:
            filteredCategories = settingsHolder.settings["categories"]
        
        filterType = self.filter["type"] if self.filter["type"] is not "" else ""

        self.data = {}
        for category in filteredCategories:
            query = f"SELECT name, content, type, id FROM data WHERE category = '{category}'"
            if filterType is not "":
                query += f" AND type = '{filterType}'"
            if self.filter["search"] is not "":
                search = self.filter["search"]
                query += f" AND (name LIKE '%{ search }%' or content LIKE '%{ search }%')"
            print(query)
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
                self.branches[x].appendRow([QtGui.QStandardItem(str(currentData[0])),
                                            QtGui.QStandardItem(str(currentData[1])),
                                            QtGui.QStandardItem(str(currentData[2])),
                                            QtGui.QStandardItem(str(currentData[3]))
                ])
        
        for branch in self.branches:
            self.rootNode.appendRow( [branch, None] )
        
        self.treeView.setModel(self.model)
        self.treeView.setColumnWidth(0, 150)

        self.treeView.setAlternatingRowColors(False)
        self.treeView.expandAll()
    
    def addContent(self):
        self.new = newContent.LinkDialog(settingsHolder)
        self.new.buttonApply.clicked.connect(self.retrieveNewContent)
        self.new.exec()
    
    def retrieveNewContent(self):
        print(self.new.obj)
        d = self.new.obj
        try:
            self.cursor.execute("INSERT INTO data(name, content, category, type) VALUES(?,?,?,?)", [d["title"], d["notes"], d["category"], d["type"]])
            self.db.commit()
            self.updateTree()
        except sqlite3.IntegrityError:
            print("Not a unique ID")
    
    def onDoubleClick(self, index):
        id = self.treeView.selectedIndexes()[3].data()
        if id is None:
            pass
        else:
            self.detail = detailContent.LinkDialog(settingsHolder, id, self.db, self.cursor)
            self.detail.exec()
        self.updateTree()
    
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

main = MainWindow(db)
main.show()
app.exec()