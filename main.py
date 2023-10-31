import sys
from pathlib import Path

import pandas as pd
import xlsxwriter as xls
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from UliPlot.XLSX import auto_adjust_xlsx_column_width
import threading

from style_gray import QDialogsheetstyle


class MainWindow(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel Sheet Generator")
        self.setMinimumSize(350, 280)

        self.widgets()
        self.layouts()
        QDialogsheetstyle(self)
        self.show()

    def widgets(self):
        self.sort_column_name = QLineEdit()
        self.sort_column_name.setPlaceholderText("Enter Name of Column")
        self.sort_column_name.setFont(QFont("Times", 12))

        self.saved_file_name = QLineEdit()
        self.saved_file_name.setPlaceholderText("Enter New File Name")
        self.saved_file_name.setFont(QFont("Times", 12))

        self.select_button = QPushButton("Select File")
        self.select_button.clicked.connect(self.getFileInfo)
        self.select_button.setFont(QFont("Times", 10))
        self.select_button.setFixedHeight(25)

        self.generate_button = QPushButton("Generate File with Sheets")
        self.generate_button.clicked.connect(self.thread_1)
        self.generate_button.setFont(QFont("Times", 10))
        self.generate_button.setFixedHeight(25)

        self.file_name = QLabel("Selected File Name: ")
        self.file_name.setFont(QFont("Times", 12))

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar.setStyleSheet("""QProgressBar::chunk {
                                        background-color: steelblue;
                                        }""")
        self.progress_bar.setFont(QFont("Times", 12))
        self.progress_bar.setFixedHeight(30)

    def layouts(self):
        self.main_layout = QHBoxLayout()
        self.button_layout = QVBoxLayout()

        self.button_layout.addWidget(self.sort_column_name)
        self.button_layout.addWidget(self.saved_file_name)
        self.button_layout.addWidget(self.select_button)
        self.button_layout.addWidget(self.file_name)
        self.button_layout.addWidget(QLabel(""))
        self.button_layout.addWidget(self.progress_bar)
        self.button_layout.addWidget(self.generate_button)

        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)

    def getFileInfo(self):
        """ Select file and get all data like path/filename """

        try:
            self.dialog = QFileDialog.getOpenFileName(self, "", "", "(*.xlsx;*.xls;*.csv)")
            (self.directory, self.fileType) = self.dialog

            # get file name only
            self.file_name_ = Path(self.directory).name

            # get file dir only
            self.file_dir_ = Path(self.directory).parents[0]
            self.file_name.setText(f"Selected File Name:\n'{self.file_name_}'")

        except:
            self.file_name.setText(f"File doesn't exist:\n'{self.file_name_}'")
            self.file_name.setStyleSheet("""QLabel { color: red; }""")

    def start_palletes_count(self):
        """This function uses "pandas" to sort main file table and generates palettes lists by palette number column
         in main file and convert it to .csv .xlsx files. In saved Excel file function will expand cells to fit input
         to view full text, counts items in palette, aligns text to center, adds table border and styles Header items."""

        column_name = f"{self.sort_column_name.text()}"

        try:
            data = pd.read_excel(f"{self.directory}")

            data_table = pd.DataFrame(data)

            grouped = data_table.groupby(data_table[f'{column_name}'])

            list_pallet = [a for a in data_table[f'{column_name}']]

            # get highest palette number
            max_number = len(list_pallet)

            # generate .xlsx file to dir where .csv is
            with (pd.ExcelWriter(f"{self.file_dir_}\{self.saved_file_name.text()}.xlsx",
                                 engine='xlsxwriter') as writer):

                if self.saved_file_name.text() == "":
                    msg = QMessageBox()
                    msg.setWindowTitle("ERROR...")
                    msg.setText("Enter new file name.")
                    msg.setIcon(QMessageBox.Information)

                    x = msg.exec_()

                else:
                    for index, item in enumerate(list_pallet, 1):
                        # group dataframe table - sort it by palette number, loop all palettes and create
                        # different tables for different pallet
                        data_tables = grouped.get_group(item)

                        # index reset to start index number from 1 (not 0 like default) after every loop
                        data_tables.index = range(1, len(data_tables) + 1)

                        print(data_tables)

                        # Save to .csv file
                        # data_tables.to_csv(f"palete", index=False)

                        # Save to .xlsx
                        data_tables.style.set_properties(**{'text-align': 'center'}
                                                         ).to_excel(writer,
                                                                    sheet_name=f'{item}',
                                                                    index=True,
                                                                    index_label="Nr.")

                        # fit to cell
                        auto_adjust_xlsx_column_width(data_tables, writer,
                                                      sheet_name=f'{item}',
                                                      margin=3)

                        # create workbook
                        workbook = writer.book
                        worksheet = writer.sheets[f'{item}']

                        # add border on cells
                        border_format = workbook.add_format({'border': True,
                                                             'align': 'center',
                                                             'valign': 'vcenter'})

                        # add style to headers
                        header_format = workbook.add_format({'font_name': 'Arial',
                                                             'font_size': 10,
                                                             'bold': True,
                                                             'bg_color': 'yellow'})

                        # "xl_range(0, 0, len(data_tables), len(data_tables.columns)"
                        # first int "0" and second "0" is start point first cell,
                        # third int is how much rows your need to apply
                        # and last one is for how many columns to apply
                        worksheet.conditional_format(xls.utility.xl_range(
                            0, 0, len(data_tables), len(data_tables.columns)),
                            {'type': 'no_errors',
                             'format': border_format})

                        worksheet.conditional_format(xls.utility.xl_range(
                            0, 0, 0, len(data_tables.columns)),
                            {'type': 'no_errors',
                             'format': header_format})

                        progress_val = int((index / max_number) * 100)
                        self.progress_bar.setValue(progress_val)

                        if 1 <= progress_val < 100:
                            self.generate_button.setEnabled(False)
                        else:
                            self.generate_button.setEnabled(True)

        except:
            self.file_name.setText(f"Column doesn't exist: '{column_name}'\nPlease enter valid column name")
            self.file_name.setStyleSheet("""QLabel { color: red; }""")

    def thread_1(self):
        self.thread = threading.Thread(target=self.start_palletes_count)
        self.thread.start()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
