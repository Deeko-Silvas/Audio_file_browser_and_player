from MainWindow import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import sys

import pygame
import mutagen.mp3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import eyed3
from sqlite3 import connect
from datetime import timedelta
import csv
from functools import reduce
from re import sub
from threading import Timer
import os
from pydub import AudioSegment
from pydub.utils import mediainfo
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import subprocess
import wave

rating_list = ["0", "1", "2", "3", "4", "5"]
rating_list_filter = ["Any", "1", "2", "3", "4", "5"]
rating_dict = {"1":"1", "64":"2", "128":"3", "196":"4", "256":"5"}

keys = ["Any", "1A", "1B", "2A", "2B", "3A", "3B", "4A", "4B", "5A", "5B", "6A", "6B", "7A", "7B", "8A", "8B", "9A", "9B", "10A", "10B", "11A", "11B", "12A", "12B"]
energy = ["Any", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
plus_minus_energy = ["-2", "Same < -2", "-1", "Same < -1", "Same", "Same > +1", "+1", "Same > +2", "+2"]
plus_minus_energy_dict = {"-2":-2, "Same < -2":-2, "-1":-1, "Same < -1":-1, "Same":0, "Same > +1":1, "+1":1, "Same > +2":2, "+2":2}
mix_type = ["Any", "Harmonic", "Energy Boost", "Energy Drop"]
plus_minus_bpm = ["Any", "+-0%", "+-1%", "+-2%", "+-3%", "+-4%", "+-5%", "+-6%"]
plus_minus_bpm_dict = {"+-0%":0, "+-1%":1, "+-2%":2, "+-3%":3, "+-4%":4, "+-5%":5, "+-6%":6}
plus_minus_year = ["Any", "+-0", "+-1", "+-2", "+-3", "+-4", "+-5", "+-6"]
plus_minus_year_dict = {"+-0":0, "+-1":1, "+-2":2, "+-3":3, "+-4":4, "+-5":5, "+-6":6}



rating_list = ["0", "1", "2", "3", "4", "5"]
rating_list_filter = ["Any", "1", "2", "3", "4", "5"]
rating_dict = {"1":"1", "64":"2", "128":"3", "196":"4", "256":"5"}

keys = ["Any", "1A", "1B", "2A", "2B", "3A", "3B", "4A", "4B", "5A", "5B", "6A", "6B", "7A", "7B", "8A", "8B", "9A", "9B", "10A", "10B", "11A", "11B", "12A", "12B"]
energy = ["Any", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
plus_minus_energy = ["-2", "Same < -2", "-1", "Same < -1", "Same", "Same > +1", "+1", "Same > +2", "+2"]
plus_minus_energy_dict = {"-2":-2, "Same < -2":-2, "-1":-1, "Same < -1":-1, "Same":0, "Same > +1":1, "+1":1, "Same > +2":2, "+2":2}
mix_type = ["Any", "Harmonic", "Energy Boost", "Energy Drop"]
plus_minus_bpm = ["Any", "+-0%", "+-1%", "+-2%", "+-3%", "+-4%", "+-5%", "+-6%"]
plus_minus_bpm_dict = {"+-0%":0, "+-1%":1, "+-2%":2, "+-3%":3, "+-4%":4, "+-5%":5, "+-6%":6}
plus_minus_year = ["Any", "+-0", "+-1", "+-2", "+-3", "+-4", "+-5", "+-6"]
plus_minus_year_dict = {"+-0":0, "+-1":1, "+-2":2, "+-3":3, "+-4":4, "+-5":5, "+-6":6}

loaded_rowid = 0
loaded_track_length = 0.0
current_position = 0
t = None
db = os.path.join("DB",
                  "Music.db")
genres_file = os.path.join("DB",
                           "genres.csv")
playlists_file = os.path.join("DB",
                              "playlists.csv")
#start_folder = os.path.join("D:",
#                            "Music",
#                            "Unmixed Tunes")


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Triggers

        # Table Columns
        self.collectionTable.hideColumn(0)
        self.collectionTable.hideColumn(1)
        self.collectionTable.hideColumn(12)
        self.collectionTable.hideColumn(13)
        self.collectionTable.setColumnWidth(2, 230)
        self.collectionTable.setColumnWidth(3, 200)
        self.collectionTable.setColumnWidth(4, 200)
        self.collectionTable.setColumnWidth(5, 150)
        self.collectionTable.setColumnWidth(6, 40)
        self.collectionTable.setColumnWidth(7, 40)
        self.collectionTable.setColumnWidth(8, 100)
        self.collectionTable.setColumnWidth(9, 50)
        self.collectionTable.setColumnWidth(10, 40)
        self.collectionTable.setColumnWidth(11, 60)

        # File menu
        self.actionAdd_File.triggered.connect(self.addFile)
        self.actionAdd_Folder.triggered.connect(self.addFolder)
        self.actionExit.triggered.connect(self.close)

        # add options to combos
        self.yearPlusMinusComboFilter.addItems(plus_minus_year)
        self.keyComboFilter.addItems(keys)
        self.mixTypeComboFilter.addItems(mix_type)
        self.ratingPlusMinusComboFilter.addItems(rating_list_filter)
        self.bpmPlusMinusComboFilter_2.addItems(plus_minus_bpm)
        self.energyComboFilter.addItems(energy)
        self.energyComboFilter.setCurrentIndex(0)
        self.energyPlusMinusComboFilter.addItems(plus_minus_energy)
        self.energyPlusMinusComboFilter.setCurrentIndex(4)

        # filter boxes changed
        self.searchInput.textChanged.connect(self.filterResults)
        self.artistInputFilter.textChanged.connect(self.filterResults)
        self.albumNameInputFilter.textChanged.connect(self.filterResults)
        self.genreInputFilter.textChanged.connect(self.filterResults)
        self.yearInputFilter.textChanged.connect(self.filterResults)
        self.yearPlusMinusComboFilter.currentIndexChanged.connect(self.filterResults)
        self.keyComboFilter.currentIndexChanged.connect(self.filterResults)
        self.mixTypeComboFilter.currentIndexChanged.connect(self.filterResults)
        self.ratingPlusMinusComboFilter.currentIndexChanged.connect(self.filterResults)
        self.bpmInputFilter.textChanged.connect(self.filterResults)
        self.bpmPlusMinusComboFilter_2.currentIndexChanged.connect(self.filterResults)
        self.energyComboFilter.currentIndexChanged.connect(self.filterResults)
        self.energyPlusMinusComboFilter.currentIndexChanged.connect(self.filterResults)

        # Tags boxes updated

        self.artistInput.installEventFilter(self)
        self.trackNameInput.installEventFilter(self)
        self.albumNameInput.installEventFilter(self)
        self.yearInput.installEventFilter(self)
        self.genreCombo.view().pressed.connect(self.updateGenre)
        self.bpmInput.installEventFilter(self)
        self.keyInput.installEventFilter(self)
        self.energyInput.installEventFilter(self)


        # Tree Widget clicks
        self.treeWidget.itemClicked.connect(self.treeClicked)

        # Button clicks
        self.filterOn.setChecked(True)
        self.filterOn.stateChanged.connect(self.filterResults)
        self.filterOn.stateChanged.connect(self.hideFilter)

        self.resetButton.clicked.connect(self.reset)

        self.addPlaylist.clicked.connect(self.createPlaylist)
        self.DeletePlaylist.clicked.connect(self.removePlaylist)

        self.playButton.clicked.connect(self.playButtonClicked)
        self.stopButton.clicked.connect(self.stop)
        self.pauseButton.clicked.connect(self.pauseButtonState)

        self.muteButton.clicked.connect(self.muteButtonState)

        self.skipButton.clicked.connect(self.skip30)
        self.backButton.clicked.connect(self.back30)

        # Sliders
        self.volumeSlider.valueChanged[int].connect(self.changeVolume)
        self.trackPositionSlider.installEventFilter(self)

        # table widget
        self.collectionTable.verticalHeader().sectionClicked.connect(self.onHeaderClicked)
        self.collectionTable.cellDoubleClicked.connect(self.onHeaderClicked)
        # self.collectionTable.setVerticalHeaderItem(3, self.setPlayImage())


        self.collectionTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.collectionTable.customContextMenuRequested.connect(self.selectMenu)

        self.collectionTable.viewport().installEventFilter(self)

        self.treeWidget.setCurrentItem(self.treeWidget.topLevelItem(0))

        self.trackPositionSlider.setStyleSheet("""QSlider {
                                                border-image: url(white.png);
                                                background-repeat: no-repeat}

                                                QSlider::groove:horizontal {
                                                border: 0px solid;
                                                height: 0x;
                                                margin: 0px}

                                                QSlider::handle:horizontal {
                                                background-color: black;
                                                border: 1px solid;
                                                height: 91px;
                                                width: 1px;
                                                margin: -45px 0px}""")


        # To here

    def closeEvent(self, event):
        result = QtWidgets.QMessageBox.question(self,
                                                "Confirm Exit...",
                                                "Are you sure you want to exit ?",
                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            self.stop()
            event.accept()
            sys.exit()

        else:
            event.ignore()

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseButtonPress and event.buttons() == QtCore.Qt.RightButton):

            item = self.collectionTable.itemAt(event.pos())
            if item is not None:
                row = item.row()
                self.menu = QtWidgets.QMenu(self)
        elif event.type() == QtCore.QEvent.FocusOut and source.objectName() != "trackPositionSlider":
            self.updateFromInput(source.objectName())
        elif event.type() == QtCore.QEvent.MouseButtonRelease and source.objectName() == "trackPositionSlider":
            position = QtWidgets.QStyle.sliderValueFromPosition(self.trackPositionSlider.minimum(), self.trackPositionSlider.maximum(), event.x(), self.trackPositionSlider.width())
            self.seek(position)
        return super(MainWindow, self).eventFilter(source, event)

    def updateGenre(self):
        self.genreCombo.currentIndexChanged.connect(lambda: self.updateFromInput("genreCombo"))

    def updateFromInput(self, object_name):
        total_rows = self.collectionTable.rowCount()
        for row in range(total_rows):
            table_rowid = self.collectionTable.item(row, 0).text()
            if table_rowid == loaded_rowid:
                matched_rowid = row

        if object_name == "artistInput":
            self.collectionTable.setItem(matched_rowid, 3, QtWidgets.QTableWidgetItem(str(self.artistInput.text())))
        elif object_name == "trackNameInput":
            self.collectionTable.setItem(matched_rowid, 2, QtWidgets.QTableWidgetItem(str(self.trackNameInput.text())))
        elif object_name == "albumNameInput":
            self.collectionTable.setItem(matched_rowid, 4, QtWidgets.QTableWidgetItem(str(self.albumNameInput.text())))
        elif object_name == "yearInput":
            self.collectionTable.setItem(matched_rowid, 10, QtWidgets.QTableWidgetItem(str(self.yearInput.text())))
        elif object_name == "genreCombo":
            self.genresCombo = QtWidgets.QComboBox()
            self.genresCombo.addItems(self.getGenres())
            self.collectionTable.setCellWidget(matched_rowid, 5, self.genresCombo)
            self.genresCombo.setCurrentText(self.genreCombo.currentText())
        elif object_name == "bpmInput":
            self.collectionTable.setItem(matched_rowid, 7, QtWidgets.QTableWidgetItem(str(self.bpmInput.text())))
        elif object_name == "keyInput":
            self.collectionTable.setItem(matched_rowid, 6, QtWidgets.QTableWidgetItem(str(self.keyInput.text())))
        elif object_name == "energyInput":
            self.collectionTable.setItem(matched_rowid, 8, QtWidgets.QTableWidgetItem(str(self.energyInput.text())))

        self.updateDB(matched_rowid)

    def selectMenu(self, pos):
        playlists = self.getPlaylists()
        playlist_menu = self.menu.addMenu("Add To Playlist")
        current_playlist_menu = self.menu.addMenu("Remove From Playlist")
        delete = self.menu.addAction("Delete")
        play = self.menu.addAction("Play")
        row = self.collectionTable.itemAt(pos).row()
        current_playlists = self.collectionTable.item(row, 13).text()
        for playlist in playlists:
            playlist_menu.addAction(playlist)
        current_playlists_list = current_playlists.split(", ")
        for current_playlist in current_playlists_list:
            current_playlist_menu.addAction((current_playlist))

        action = self.menu.exec_(self.collectionTable.mapToGlobal(pos))
        try:
            parent = action.parentWidget().title()
        except AttributeError:
            return
        if parent == "Add To Playlist":
            self.addToPlaylist(row, action)
        elif parent == "Remove From Playlist":
            self.removeFromPlaylist(row, action)
        elif action.text() == "Play":
            self.onHeaderClicked(row)
        elif action.text() == "Delete":
            self.deleteItem(row)

    def addToPlaylist(self, row, playlist):
        current_playlists = self.collectionTable.item(row, 13).text()
        if current_playlists != "":
            playlist_lists = current_playlists.split(", ")
            if playlist.text() in playlist_lists:
                self.messageBox("Already In Playlist!", "This track is already in this playlist")
            else:
                playlist_lists.append(playlist.text())
        else:
            playlist_lists = []
            playlist_lists.append(playlist.text())

        playlist_lists_string = str(playlist_lists)
        playlist_string = playlist_lists_string[1:-1].replace("'", "")
        self.collectionTable.setItem(row, 13, QtWidgets.QTableWidgetItem(playlist_string))
        self.updateDB(row)

    def removeFromPlaylist(self, row, playlist):
        current_playlists = self.collectionTable.item(row, 13).text()
        current_playlists_list = current_playlists.split(", ")
        current_playlists_list.remove(playlist.text())
        current_playlists_list_string = str(current_playlists_list)
        current_playlists_string = current_playlists_list_string[1:-1].replace("'", "")
        self.collectionTable.setItem(row, 13, QtWidgets.QTableWidgetItem(current_playlists_string))
        self.updateDB(row)
        self.filterResults()

    def deleteItem(self, row):
        rowid = self.collectionTable.item(row, 0).text()

        conn = connect(db)
        cursor_object = conn.cursor()

        cursor_object.execute("DELETE FROM catalogue WHERE _rowid_=?", (rowid,))
        self.collectionTable.removeRow(row)
        conn.commit()

        conn.close()



    def onHeaderClicked(self, logicalIndex):

        rowid = self.collectionTable.item(logicalIndex, 0).text()
        waveform = self.collectionTable.cellWidget(logicalIndex, 1)
        title = self.collectionTable.item(logicalIndex, 2).text()
        artist = self.collectionTable.item(logicalIndex, 3).text()
        album = self.collectionTable.item(logicalIndex, 4).text()
        genre = self.collectionTable.cellWidget(logicalIndex, 5).currentText()
        key = self.collectionTable.item(logicalIndex, 6).text()
        bpm = self.collectionTable.item(logicalIndex, 7).text()
        energy = self.collectionTable.item(logicalIndex, 8).text()
        rating = self.collectionTable.cellWidget(logicalIndex, 9).currentText()
        year = self.collectionTable.item(logicalIndex, 10).text()
        length = self.collectionTable.item(logicalIndex, 11).text()
        file = self.collectionTable.item(logicalIndex, 12).text()

        self.loadID3(rowid, title, artist, album, genre, key, bpm, energy, rating, year, length, file)
        self.loadFile(file)
        self.trackPositionSlider.setSliderPosition(0)

        self.play()
        self.loadWaveform(file, rowid)

    def populateCollection(self):
        genres_list = self.getGenres()
        conn = connect(db)
        cursor_object = conn.cursor()

        cursor_object.execute("SELECT rowid, * FROM catalogue")

        rows = cursor_object.fetchall()
        #print(rows)

        for track_details in rows:
            self.addToCollection(track_details, genres_list, True)

        conn.close()

        #self.collectionTable.itemChanged.connect(self.itemChanged)

    def itemChanged(self, item):
        combo = self.sender()

        if item == "combo":
            row = combo.property('row')
        else:
            row = item.row()

        self.updateDB(row)

    def addFile(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(None, "Open", "",
                                                          "MP3 (*.mp3)")
        if len(file_name[0]) > 0:
            self.addFiles(file_name[0])

    def addFolder(self):
        folder_name = QtWidgets.QFileDialog.getExistingDirectory(None, "Open", "")
        path = folder_name
        if path != "":
            for current_folder, subfolders, file_names in os.walk(path):
                for file_name in file_names:
                    if file_name.lower().endswith(".mp3"):
                        self.addFiles(os.path.join(current_folder, file_name))

    def addFiles(self, file_name):

        track_details = self.getID3(file_name)
        if track_details != False:

            track_details.append(file_name)
            track_details.append("")

            self.addNewGenre(track_details[4])
            self.addToCollection(track_details, self.getGenres())

    def addToCollection(self, track_details, genres_list, startup=False):

        row = self.collectionTable.rowCount()
        self.collectionTable.insertRow(row)
        headerItem = QtWidgets.QTableWidgetItem("")
        headerItem.setIcon(QtGui.QIcon(QtGui.QPixmap(os.path.join("images", "play.jpg"))))
        self.collectionTable.setVerticalHeaderItem(row, headerItem)

        self.collectionTable.setRowHeight(row, 5)

        # creates genres & ratings combos
        self.genresCombo = QtWidgets.QComboBox()
        self.genresCombo.addItems(genres_list)
        self.ratingCombo = QtWidgets.QComboBox()
        self.ratingCombo.addItems(rating_list)

        if startup == False:
            rowid = str(self.writeDB(track_details))
            rowid_string = sub('[,()]', '', str(rowid))
            self.collectionTable.setItem(row, 0, QtWidgets.QTableWidgetItem(rowid_string))
            col = 1
        else:
            col = 0


        for detail in track_details:
            print(detail)
            if col == 5:
                self.collectionTable.setCellWidget(row, col, self.genresCombo)
                self.genresCombo.setCurrentText(detail)
                self.genresCombo.setProperty('row', row)
                self.genresCombo.currentIndexChanged.connect(lambda: self.itemChanged("combo"))
            if col == 9:
                self.collectionTable.setCellWidget(row, col, self.ratingCombo)
                self.ratingCombo.setCurrentText(str(detail))
                self.ratingCombo.setProperty('row', row)
                self.ratingCombo.currentIndexChanged.connect(lambda: self.itemChanged("combo"))
            else:
                if detail == None:
                    detail = ""
                self.collectionTable.setItem(row, col, QtWidgets.QTableWidgetItem(str(detail)))
            col += 1

        return [self.genreCombo, self.ratingCombo]

    def writeDB(self, track_details):
        conn = connect(db)
        cursor_object = conn.cursor()

        cursor_object.execute("INSERT INTO catalogue VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                              (track_details))
        a = cursor_object.execute('SELECT last_insert_rowid() FROM catalogue')
        rowid = a.fetchone()


        conn.commit()
        conn.close()

        return rowid

    def updateDB(self, row):
        track_details = []
        row_id = self.collectionTable.item(row, 0).text()
        for col in range(2, 14):
            if col == 5 or col == 9:
                try:
                    item_text = str(self.collectionTable.cellWidget(row, col).currentText())
                except AttributeError:
                    return
            else:
                #pass
                item_text = str(self.collectionTable.item(row, col).text())
            track_details.append(item_text)


        conn = connect(db)
        cursor_object = conn.cursor()

        cursor_object.execute(
            "UPDATE catalogue SET Title = (?), Artist = (?), Album = (?), Genre = (?), Song_Key = (?), BPM = (?), Energy = (?), Rating = (?), Song_Year = (?), Song_Length = (?), Location = (?), Playlists = (?) WHERE _rowid_ = (?)",
            (track_details[0], track_details[1], track_details[2], track_details[3], track_details[4], track_details[5],
             track_details[6], track_details[7], track_details[8], track_details[9], track_details[10],
             track_details[11], row_id))
        conn.commit()
        conn.close()

    def hideFilter(self):
        if self.filterOn.isChecked():
            self.filterBox.show()
        else:
            self.filterBox.hide()

    def reset(self):
        self.artistInputFilter.setText("")
        self.albumNameInputFilter.setText("")
        self.genreInputFilter.setText("")
        self.yearInputFilter.setText("")
        self.yearPlusMinusComboFilter.setCurrentText("Any")
        self.keyComboFilter.setCurrentText("Any")
        self.mixTypeComboFilter.setCurrentText("Any")
        self.ratingPlusMinusComboFilter.setCurrentText("Any")
        self.bpmInputFilter.setText("")
        self.bpmPlusMinusComboFilter_2.setCurrentText("Any")
        self.energyComboFilter.setCurrentText("Any")
        self.energyPlusMinusComboFilter.setCurrentText("Same")

    def filterResults(self):

        tree = self.treeWidget.currentItem()

        list_of_lists = []
        search_index_list = []
        genre_tree_index_list = []
        playlist_tree_index_list = []

        # unhide all rows
        table_rows = self.collectionTable.rowCount()
        for row in range(table_rows):
            self.collectionTable.showRow(row)

        if tree.text(0) != "Collection" and tree.text(0) != "Genres" and tree.text(0) != "Playlists":
            tree_parent = tree.parent()
            child = tree.text(0)

            if tree_parent.text(0) == "Genres":
                for row_index in range(table_rows):
                    genre_item = self.collectionTable.cellWidget(row_index, 5).currentText()
                    if child.lower() == genre_item.lower():
                        genre_index = self.collectionTable.item(row_index, 0).text()
                        genre_tree_index_list.append(genre_index)

                if len(genre_tree_index_list) == 0:
                    genre_tree_index_list.append("0")

                list_of_lists.append(genre_tree_index_list)

            if tree_parent.text(0) == "Playlists":
                for row_index in range(table_rows):
                    playlist_item = self.collectionTable.item(row_index, 13).text()
                    playlist_item_list = playlist_item.split(", ")
                    if child in playlist_item_list:
                        playlist_index = self.collectionTable.item(row_index, 0).text()
                        playlist_tree_index_list.append(playlist_index)

                if len(playlist_tree_index_list) == 0:
                    playlist_tree_index_list.append("0")

                list_of_lists.append(playlist_tree_index_list)


        search = self.searchInput.text()

        if search != "":
            for row_index in range(table_rows):
                title_item = self.collectionTable.item(row_index, 3).text()
                artist_item = self.collectionTable.item(row_index, 4).text()
                if search.lower() in title_item.lower() or search.lower() in artist_item.lower():
                    search_index = self.collectionTable.item(row_index, 0).text()
                    search_index_list.append(search_index)
                list_of_lists.append(search_index_list)

        if self.filterOn.isChecked():
            artist_index_list = []
            title_index_list = []
            genre_index_list = []
            year_index_list = []
            rating_index_list = []
            bpm_index_list = []
            key_index_list = []
            energy_index_list = []

            artist = self.artistInputFilter.text()
            title = self.albumNameInputFilter.text()
            genre = self.genreInputFilter.text()
            year = self.yearInputFilter.text()
            year_plus = self.yearPlusMinusComboFilter.currentText()
            key = self.keyComboFilter.currentText()
            mix_type = self.mixTypeComboFilter.currentText()
            rating = self.ratingPlusMinusComboFilter.currentText()
            bpm = self.bpmInputFilter.text()
            bpm_plus = self.bpmPlusMinusComboFilter_2.currentText()
            energy = self.energyComboFilter.currentText()
            energy_plus = self.energyPlusMinusComboFilter.currentText()

            table_rows = self.collectionTable.rowCount()

            if title != "":
                title_index_list = self.filterContain(title, table_rows, 2)
                list_of_lists.append(title_index_list)

            if artist != "":
                artist_index_list = self.filterContain(artist, table_rows, 3)
                list_of_lists.append(artist_index_list)

            if genre != "":
                genre_index_list = self.filterContain(genre, table_rows, 5)
                list_of_lists.append(genre_index_list)

            if year != "" and year_plus != "Any":
                year_range = plus_minus_year_dict[year_plus]
                try:
                    year_index_list = self.filterPlusMinus(int(year), year_range, table_rows, 10)
                    list_of_lists.append(year_index_list)
                except ValueError:
                    self.messageBox("Error", "Please enter a valid year")

            if rating != "Any":
                rating_index_list = self.filterGreaterThan(int(rating), table_rows, 9)
                list_of_lists.append(rating_index_list)

            if bpm != "" and bpm_plus != "Any":
                bpm_range = plus_minus_bpm_dict[bpm_plus]
                try:
                    bpm_index_list = self.filterPlusMinus(int(bpm), bpm_range, table_rows, 7)
                    list_of_lists.append(bpm_index_list)
                except ValueError:
                    self.messageBox("Error", "Please enter a valid BPM")

            if key != "Any" and mix_type != "Any":
                key_index_list = self.keyFilter(key, mix_type, table_rows, 6)
                list_of_lists.append(key_index_list)

            if energy != "Any":
                energy_range = plus_minus_energy_dict[energy_plus]
                energy_index_list = self.filterEnergy(int(energy), energy_range, table_rows, 8, energy_plus)
                list_of_lists.append(energy_index_list)

        try:
            result = reduce(set.intersection, map(set, filter(len, list_of_lists)))
        except TypeError:
            return

        for row_index in range(table_rows):
            rowid = self.collectionTable.item(row_index, 0).text()
            if rowid not in result:
                self.collectionTable.hideRow(row_index)

    def filterContain(self, input, table_rows, col):
        filter_in_list = []
        for row_index in range(table_rows):
            item = self.collectionTable.item(row_index, col)
            if input.lower() in item.text().lower():
                index = self.collectionTable.item(row_index, 0).text()
                filter_in_list.append(index)

        if len(filter_in_list) == 0:
            filter_in_list.append("0")

        return filter_in_list

    def filterPlusMinus(self, input, plus, table_rows, col):
        filter_in_list = []
        for row_index in range(table_rows):
            item = self.collectionTable.item(row_index, col).text()
            try:
                if int(item) <= (input + plus) and int(item) >= (input - plus):
                    index = self.collectionTable.item(row_index, 0).text()
                    filter_in_list.append(index)
            except ValueError:
                continue

        if len(filter_in_list) == 0:
            filter_in_list.append("0")

        return filter_in_list

    def filterGreaterThan(self, input, table_rows, col):
        filter_in_list = []
        for row_index in range(table_rows):
            item = self.collectionTable.cellWidget(row_index, col)
            if int(item.currentText()) >= input:
                index = self.collectionTable.item(row_index, 0).text()
                filter_in_list.append(index)

        if len(filter_in_list) == 0:
            filter_in_list.append("0")

        return filter_in_list

    def keyFilter(self, input, type, table_rows, col):
        filter_in_list = []
        key_list = []

        num = int(input[:-1])
        letter = input[-1:]

        if type == "Harmonic":
            if num == 12:
                key1 = "1" + letter
            else:
                key1 = str(num + 1) + letter
            if num == 1:
                key2 = "12" + letter
            else:
                key2 = str(num - 1) + letter
            if letter == "A":
                key3 = str(num) + "B"
            else:
                key3 = str(num) + "A"

            key_list = [input, key1, key2, key3]
        elif type == "Energy Boost":
            new_num = num + 2
            if new_num > 12:
                new_num -= 12
            key_list = [(str(new_num) + letter)]
        elif type == "Energy Drop":
            new_num = num - 2
            if new_num < 1:
                new_num += 12;
            key_list = [(str(new_num) + letter)]

        for row_index in range(table_rows):
            item = self.collectionTable.item(row_index, col)
            if item.text() in key_list:
                index = self.collectionTable.item(row_index, 0).text()
                filter_in_list.append(index)

        if len(filter_in_list) == 0:
            filter_in_list.append("0")

        return filter_in_list

    def filterEnergy(self, input, plus, table_rows, col, energy_plus):
        filter_in_list = []
        for row_index in range(table_rows):
            item = self.collectionTable.item(row_index, col).text()[-1:]
            try:
                if item != "":
                    if "Same" in energy_plus and "+" in energy_plus:
                        if int(item) >= input and int(item) <= input + plus:
                            index = self.collectionTable.item(row_index, 0).text()
                            filter_in_list.append(index)
                    elif "Same" in energy_plus and "-" in energy_plus:
                        if int(item) <= input and int(item) >= input + plus:
                            index = self.collectionTable.item(row_index, 0).text()
                            filter_in_list.append(index)
                    else:
                        if int(item) == input + plus:
                            index = self.collectionTable.item(row_index, 0).text()
                            filter_in_list.append(index)
            except ValueError:
                pass

        if len(filter_in_list) == 0:
            filter_in_list.append("0")

        return filter_in_list

    def treeClicked(self):
        self.filterResults()

    def populatePlaylists(self):
        genres_item = self.treeWidget.findItems("Genres", QtCore.Qt.MatchExactly, 0)[0]
        genres_list = self.getGenres()
        for genre in genres_list:
            new_genre_item = QtWidgets.QTreeWidgetItem()
            new_genre_item.setText(0, genre)
            genres_item.addChild(new_genre_item)

        playlist_item = self.treeWidget.findItems("Playlists", QtCore.Qt.MatchExactly, 0)[0]
        playlist_list = self.getPlaylists()
        for playlist in playlist_list:
            new_playlist_item = QtWidgets.QTreeWidgetItem()
            new_playlist_item.setText(0, playlist)
            playlist_item.addChild(new_playlist_item)

    def playButtonClicked(self):
        try:
            if pygame.mixer.music.get_busy():
                if self.pauseButton.isChecked():
                    self.pauseButton.setChecked(False)
                    pygame.mixer.music.unpause()
                else:
                    pass
            else:
                self.play()
        except pygame.error:
            pass

    def play(self, position=0):
        try:
            pygame.mixer.music.rewind()
            pygame.mixer.music.play(start=position)
            self.startPlayheadIncrement()
        except pygame.error:
            pass

        global current_position
        current_position = position


    def stop(self):
        try:
            pygame.mixer.music.stop()
            self.trackPositionSlider.setSliderPosition(0)
            self.startPlayheadIncrement(stop=True)
        except pygame.error:
            pass

    def sliderInc(self):
        track_length_seconds = self.get_sec(loaded_track_length)
        return track_length_seconds / 1000

    def setPlayHead(self, position):
        slider_increment = self.sliderInc()

        value = position / slider_increment
        self.trackPositionSlider.setSliderPosition(value)

    def startPlayheadIncrement(self, stop=False):
        track_length_seconds = self.get_sec(loaded_track_length)
        increment = track_length_seconds / 1000
        global t
        try:
            t.cancel()
        except AttributeError:
            pass
        if not stop:
            t = Timer(0.5, self.startPlayheadIncrement)
            t.start()

            self.incrementPlayhead()

    def incrementPlayhead(self):
        position = pygame.mixer.music.get_pos()
        new_position = (position + (current_position * 1000)) / 1000
        self.setPlayHead(new_position)

    def pauseButtonState(self):
        if self.pauseButton.isChecked():
            try:
                pygame.mixer.music.pause()
            except pygame.error:
                pass
        else:
            try:
                pygame.mixer.music.unpause()
            except pygame.error:
                pass

    def muteButtonState(self):
        if self.muteButton.isChecked():
            try:
                pygame.mixer.music.set_volume(0)
            except pygame.error:
                pass
        else:
            try:
                vol = self.volumeSlider.value()
                pygame.mixer.music.set_volume(vol / 100)
            except pygame.error:
                pass

    def changeVolume(self, value):
        if value == 0:
            try:
                self.muteButton.setChecked(True)
                self.muteButtonState()
            except pygame.error:
                pass
        else:
            try:
                pygame.mixer.music.set_volume(value / 100)
                self.muteButton.setChecked(False)
            except pygame.error:
                pass

    def getPosition(self):
        position = pygame.mixer.music.get_pos()
        return current_position + position

    def skip30(self):
        try:
            global current_position
            position = self.getPosition()
            new_position = (position + 30000 + (current_position * 1000)) / 1000
            self.play(int(new_position))
            current_position = new_position

            self.setPlayHead(new_position)
        except pygame.error:
            pass

    def back30(self):
        try:
            global current_position
            position = pygame.mixer.music.get_pos()
            if position + (current_position * 1000) <= 30000:
                self.play()
                self.setPlayHead(0)
            else:
                new_position = ((current_position * 1000) + position - 30000) / 1000
                self.play(int(new_position))
                self.setPlayHead(int(new_position))
        except pygame.error:
            pass

    def seek(self, value):
        track_length_seconds = self.get_sec(loaded_track_length)
        try:
            slider_increment = track_length_seconds /  1000
            track_position = value * slider_increment
            self.trackPositionSlider.setSliderPosition(value)
            self.play(track_position)
        except TypeError:
            pass


    def get_sec(self, time_str):
        try:
            m, s = time_str.split(':')
            return int(m) * 60 + int(s)
        except AttributeError:
            pass

    def getGenres(self):
        with open(genres_file, "r") as genres:
            reader = csv.reader(genres)
            for row in reader:
                genres_list = row

        return genres_list

    def addNewGenre(self, genre):
        genres_list = self.getGenres()

        if genre not in genres_list:
            genres_list.append(genre)
            with open(genres_file, "w", newline="") as add_genre:
                writer = csv.writer(add_genre)

                writer.writerow(genres_list)

    def getPlaylists(self):
        with open(playlists_file, "r") as playlists:
            reader = csv.reader(playlists)
            for row in reader:
                playlists_list = row

        return playlists_list

    def newPlaylist(self, playlist_name):
        playlist_list = self.getPlaylists()
        playlist_list.append(playlist_name)
        self.writePlaylist(playlist_list)

    def deletePlaylist(self, playlist_name):
        playlist_list = self.getPlaylists()
        playlist_list.remove(playlist_name)
        self.writePlaylist(playlist_list)

    def writePlaylist(self, playlist_list):
        with open(playlists_file, "w", newline="") as add_playlist:
            writer = csv.writer(add_playlist)
            writer.writerow(playlist_list)

    def createPlaylist(self):
        playlist_list = self.getPlaylists()

        playlist_name, ok = QtWidgets.QInputDialog.getText(QtWidgets.QInputDialog(), "New Playlist",
                                                           "Please enter new playlist name:")
        if ok:
            if playlist_name in playlist_list:
                self.messageBox("Already Exists", "Playlist already exists")
            else:
                self.newPlaylist(playlist_name)
                playlist_item = self.treeWidget.findItems("Playlists", QtCore.Qt.MatchExactly, 0)[0]
                new_playlist_item = QtWidgets.QTreeWidgetItem()
                new_playlist_item.setText(0, playlist_name)
                playlist_item.addChild(new_playlist_item)

    def removePlaylist(self):
        item = self.treeWidget.currentItem()
        parent = item.parent()
        if parent == None or parent.text(0) != "Playlists":
            self.messageBox("Error", "Please select a valid playlist")
        else:
            message = f"Are you sure you want to delete {item.text(0)}?"
            if self.yesNo("Are you sure", message):
                self.deletePlaylist(item.text(0))
                parent.removeChild(item)
                row_count = self.collectionTable.rowCount()
                for row in range(row_count):
                    playlists = self.collectionTable.item(row, 13).text()
                    playlists_list = playlists.split(", ")
                    if item.text(0) in playlists_list:
                        playlists_list.remove(item.text(0))
                        playlists_list_string = str(playlists_list)
                        playlists_string = playlists_list_string[1:-1].replace("'", "")
                        self.collectionTable.setItem(row, 13, QtWidgets.QTableWidgetItem())
                        self.updateDB(row)
                self.filterResults()
            else:
                return

    def messageBox(self, title, message):
        self.app = QtWidgets.QMessageBox()
        self.app.setWindowTitle(title)
        self.app.setText(message)
        self.app.setIcon(QtWidgets.QMessageBox.Warning)
        self.app.exec()

    def yesNo(self, title, message):
        self.app = QtWidgets.QMessageBox.question(self, title, message, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if self.app == QtWidgets.QMessageBox.Yes:
            return True
        else:
            return False

    def getID3(self, file):
        # eyed3
        audiofile = eyed3.load(file)

        try:
            artist = audiofile.tag.artist
        except AttributeError:
            return False
        try:
            title = audiofile.tag.title
        except AttributeError:
            return False

        album = audiofile.tag.album
        bpm = audiofile.tag.bpm
        try:
            energy = audiofile.tag.comments[0].text
        except IndexError:
            energy = ""

        waveform = ""

        # mutagen
        audio = ID3(file)

        try:
            year = str(audio["TDRC"].text[0])
        except KeyError:
            year = ""
        try:
            key = audio["TKEY"].text[0]
        except KeyError:
            key = ""
        try:
            genre = audio["TCON"].text[0]
        except KeyError:
            genre = ""

        try:
            length_sec = MP3(file).info.length
        except mutagen.mp3.HeaderNotFoundError:
            return False
        length_list = str(timedelta(seconds=length_sec)).split(".")
        length = length_list[0].replace("0:", "", 1)
        popm = mutagen.File(file).tags.getall("POPM")
        if len(popm) == 0:
            rating = 0
        else:
            popm_string = str(popm[0])
            popm_left_strip = popm_string.replace("POPM(email='Windows Media Player 9 Series', rating=", "")
            popm_right_strip = popm_left_strip.replace(")", "")
            rating = rating_dict[popm_right_strip]

        iD3List = [waveform, title, artist, album, genre, key, bpm, energy, rating, year, length]
        return iD3List

    def loadID3(self, rowid, title, artist, album, genre, key, bpm, energy, rating, year, length, file):

        try:
            audio = ID3(file)
        except mutagen.MutagenError:
            self.messageBox("Error", "File Not Found")
            return
        try:
            art = audio["APIC:"].data
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(art)
            pixmap_resized = pixmap.scaled(191, 191, QtCore.Qt.KeepAspectRatio)
            art = pixmap_resized
            self.albumArtLabel.setPixmap(art)
            self.albumArtLabel.setGeometry(70, 515, 191, 191)
        except KeyError:
            self.albumArtLabel.clear()

        self.addNewGenre(genre)

        global loaded_rowid
        loaded_rowid = rowid
        global loaded_track_length
        loaded_track_length = length

        genreList = self.getGenres()
        self.genreCombo.addItems(genreList)

        # import ID3 tags to GUI
        self.trackNameInput.setText(title)
        self.artistInput.setText(artist)
        self.albumNameInput.setText(album)
        self.genreCombo.setCurrentText(genre)
        self.keyInput.setText(key)
        self.bpmInput.setText(str(bpm))
        self.energyInput.setText(energy)
        self.yearInput.setText(str(year))


    def loadWaveform(self, file, rowid):
        self.trackPositionSlider.setStyleSheet("""QSlider {
                                                border-image: url(icons8-responsive-100.png);
                                                background-repeat: no-repeat}

                                                QSlider::groove:horizontal {
                                                border: 0px solid;
                                                height: 0x;
                                                margin: 0px}

                                                QSlider::handle:horizontal {
                                                background-color: black;
                                                border: 1px solid;
                                                height: 91px;
                                                width: 1px;
                                                margin: -45px 0px}""")
        self.getWaveform(rowid, file)

    def getWaveform(self, rowid, file):


        conn = connect(db)
        cursor_object = conn.cursor()

        cursor_object.execute("SELECT rowid, * FROM catalogue WHERE _rowid_=?", (rowid,))

        row = cursor_object.fetchone()
        if row[1] != None and row[1] != "":
            with open("waveform.jpg", "wb") as fh:
                fh.write(row[1])
            image_jpg = Image.open(r"waveform.jpg")
            image_jpg.save(r"waveform.png")
        else:
            success = self.createWaveform(file)
            if success:
                with open("waveform.png", "rb") as file:
                    blobData = file.read()
                cursor_object.execute("UPDATE catalogue SET Waveform = (?) WHERE _rowid_ = (?)", (blobData, rowid,))
                conn.commit()
        self.trackPositionSlider.setStyleSheet("""QSlider {
                                                border-image: url(waveform.png);
                                                background-repeat: no-repeat}

                                                QSlider::groove:horizontal {
                                                border: 0px solid;
                                                height: 0x;
                                                margin: 0px}

                                                QSlider::handle:horizontal {
                                                background-color: black;
                                                border: 1px solid;
                                                height: 91px;
                                                width: 1px;
                                                margin: -45px 0px}""")

        conn.close()

    def createWaveform(self, file):

        subprocess.call(["ffmpeg", "-i", file, "output.wav"])

        wf = wave.open("output.wav", 'rb')

        duration = self.get_sec(loaded_track_length)
        fs = wf.getframerate()
        bytes_per_sample = wf.getsampwidth()
        bits_per_sample = bytes_per_sample * 8
        dtype = 'int{0}'.format(bits_per_sample)

        channels = wf.getnchannels()

        audio = np.fromstring(wf.readframes(int(duration * fs * bytes_per_sample / channels)), dtype=dtype)
        audio.shape = (int(audio.shape[0] / int(channels)), int(channels))

        times = np.arange(audio.shape[0]) / float(fs)

        plt.figure(figsize=(11.572917, 0.947917))
        plt.plot(times, audio[:, 1])
        plt.xlim(0, duration)
        plt.ylim(-36000, 36000)

        plt.axis("off")
        plt.savefig("waveform.png", bbox_inches="tight", pad_inches=0)

        wf.close()

        os.remove("Output.wav")

    def getGeomerty(self):
        x = self.trackPositionSlider.x()
        y = self.trackPositionSlider.y()
        width = self.trackPositionSlider.width()
        height = self.trackPositionSlider.height()


        return [x, y, width, height]

    def loadFile(self, file):

        try:
            audio_info = mutagen.File(file).info
        except mutagen.MutagenError:
            return
        sample_rate = audio_info.sample_rate
        pygame.mixer.pre_init(sample_rate, -16, 2, 512)
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volumeSlider.value() / 100)
        pygame.mixer.music.load(file)



app = QtWidgets.QApplication([])
app.setStyle('Fusion')
window = MainWindow()
window.show()
window.populateCollection()
window.populatePlaylists()

sys.exit(app.exec_())


