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

        self.updateTree(None)

        self.treeView.doubleClicked.connect(self.onDoubleClick)

    def updateTree(self, filter):

        for category in settingsHolder.settings["categories"]:
            query = f"SELECT name, content, type, id FROM data WHERE category == '{category}'"
            self.cursor.execute(query)
            self.data[str(category)] = self.cursor.fetchall()

        self.model = QtGui.QStandardItemModel()
        self.model.setColumnCount(4)
        self.model.setHorizontalHeaderLabels(["Title", "Notes", "Type", "ID"])
        self.rootNode = self.model.invisibleRootItem()

        self.branches = []
        for x in range(0, len(settingsHolder.settings["categories"])):
            category = settingsHolder.settings["categories"][x]
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
            self.updateTree(None)
        except sqlite3.IntegrityError:
            print("Not a unique ID")
    
    def onDoubleClick(self, index):
        id = self.treeView.selectedIndexes()[3].data()

        self.new = detailContent.LinkDialog(settingsHolder, id, self.db, self.cursor)
        self.new.exec()
        self.updateTree(None)

main = MainWindow(db)
main.show()
app.exec()