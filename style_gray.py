def QDialogsheetstyle(self):
    self.setStyleSheet("""QDialog{
                            background-color:lightgray;
                            }

                            QGroupBox{
                            background-color: lightgrey;
                            border: 1px solid black;
                            margin-top: 10px;
                            padding: 10px;;
                            }

                            QGroupBox::title {
                            color: black;
                            bottom: 10px;
                            subcontrol-position: top;
                            }
                            
                            QLabel{
                            font-size: 12pt;
                            }

                            QPushButton{
                            background-color:dimgray;
                            color:white;
                            border:1px solid black;
                            }

                            QPushButton::hover{
                            background-color:steelblue;
                            color:white;
                            border:1px solid black;
                            }

                            QPushButton::pressed{
                            background-color:black;
                            color:white;
                            }

                            """)
