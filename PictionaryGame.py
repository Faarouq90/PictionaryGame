from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QDockWidget, QPushButton, QVBoxLayout, \
    QLabel, QMessageBox
from PyQt6.QtGui import QIcon, QPainter, QPen, QAction, QPixmap
import sys
import csv, random
from PyQt6.QtCore import Qt, QPoint, QTimer


class PictionaryGame(QMainWindow):
    '''
    Painting Application class
    '''

    def __init__(self):
        super().__init__()

        # set window title
        self.setWindowTitle("Pictionary Game - A2 Template")

        # set the windows dimensions
        top = 400
        left = 400
        width = 800
        height = 600
        self.setGeometry(top, left, width, height)

        # set the icon
        self.setWindowIcon(QIcon("./icons/paint-brush.png"))

        # image settings (default)
        self.image = QPixmap("./icons/canvas.png")
        self.image.fill(Qt.GlobalColor.white)
        mainWidget = QWidget()
        mainWidget.setMaximumWidth(300)

        # draw settings (default)
        self.drawing = False
        self.brushSize = 3
        self.brushColor = Qt.GlobalColor.black

        # reference to last point recorded by mouse
        self.lastPoint = QPoint()

        # set up menus
        mainMenu = self.menuBar()
        mainMenu.setNativeMenuBar(False)
        fileMenu = mainMenu.addMenu(" File")
        brushSizeMenu = mainMenu.addMenu(" Brush Size")
        brushColorMenu = mainMenu.addMenu(" Brush Colour")
        helpMenu = mainMenu.addMenu(" Help")  # Add Help menu

        # save menu item
        saveAction = QAction(QIcon("./icons/save.png"), "Save", self)
        saveAction.setShortcut("Ctrl+S")
        fileMenu.addAction(saveAction)
        saveAction.triggered.connect(self.save)

        # clear
        clearAction = QAction(QIcon("./icons/clear.png"), "Clear", self)
        clearAction.setShortcut("Ctrl+C")
        fileMenu.addAction(clearAction)
        clearAction.triggered.connect(self.clear)

        # brush thickness
        threepxAction = QAction(QIcon("./icons/threepx.png"), "3px", self)
        threepxAction.setShortcut("Ctrl+3")
        brushSizeMenu.addAction(threepxAction)
        threepxAction.triggered.connect(self.threepx)

        fivepxAction = QAction(QIcon("./icons/fivepx.png"), "5px", self)
        fivepxAction.setShortcut("Ctrl+5")
        brushSizeMenu.addAction(fivepxAction)
        fivepxAction.triggered.connect(self.fivepx)

        sevenpxAction = QAction(QIcon("./icons/sevenpx.png"), "7px", self)
        sevenpxAction.setShortcut("Ctrl+7")
        brushSizeMenu.addAction(sevenpxAction)
        sevenpxAction.triggered.connect(self.sevenpx)

        ninepxAction = QAction(QIcon("./icons/ninepx.png"), "9px", self)
        ninepxAction.setShortcut("Ctrl+9")
        brushSizeMenu.addAction(ninepxAction)
        ninepxAction.triggered.connect(self.ninepx)

        # brush colors
        blackAction = QAction(QIcon("./icons/black.png"), "Black", self)
        blackAction.setShortcut("Ctrl+B")
        brushColorMenu.addAction(blackAction)
        blackAction.triggered.connect(self.black)

        redAction = QAction(QIcon("./icons/red.png"), "Red", self)
        redAction.setShortcut("Ctrl+R")
        brushColorMenu.addAction(redAction)
        redAction.triggered.connect(self.red)

        greenAction = QAction(QIcon("./icons/green.png"), "Green", self)
        greenAction.setShortcut("Ctrl+G")
        brushColorMenu.addAction(greenAction)
        greenAction.triggered.connect(self.green)

        yellowAction = QAction(QIcon("./icons/yellow.png"), "Yellow", self)
        yellowAction.setShortcut("Ctrl+Y")
        brushColorMenu.addAction(yellowAction)
        yellowAction.triggered.connect(self.yellow)

        # Help Menu Actions
        aboutAction = QAction("About", self)  # About action
        aboutAction.triggered.connect(self.about)
        helpAction = QAction("Help", self)  # Help action
        helpAction.triggered.connect(self.help)

        helpMenu.addAction(aboutAction)
        helpMenu.addAction(helpAction)

        # Side Dock
        self.dockInfo = QDockWidget()
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockInfo)

        # widget inside the Dock
        playerInfo = QWidget()
        self.vbdock = QVBoxLayout()
        playerInfo.setLayout(self.vbdock)
        playerInfo.setMaximumSize(100, self.height())
        self.vbdock.addWidget(QLabel("Current Turn: -"))
        self.vbdock.addSpacing(20)
        self.vbdock.addWidget(QLabel("Scores:"))
        self.vbdock.addWidget(QLabel("Player 1: -"))
        self.vbdock.addWidget(QLabel("Player 2: -"))
        self.vbdock.addStretch(1)
        self.vbdock.addWidget(QPushButton("Button"))

        # Colour and Brush Size indicators
        self.colorLabel = QLabel("Selected Color: Black")
        self.vbdock.addWidget(self.colorLabel)
        self.thicknessLabel = QLabel(f"Brush Thickness: {self.brushSize}px")
        self.vbdock.addWidget(self.thicknessLabel)

        # Current Player and Score information
        self.currentPlayerLabel = QLabel("Current Player: Player 1")
        self.vbdock.addWidget(self.currentPlayerLabel)
        self.scoreLabel1 = QLabel("Player 1: 0")
        self.vbdock.addWidget(self.scoreLabel1)
        self.scoreLabel2 = QLabel("Player 2: 0")
        self.vbdock.addWidget(self.scoreLabel2)
        self.turnLabel = QLabel("Turn 1 of 5")
        self.vbdock.addWidget(self.turnLabel)

        # Start Game and Skip Turn Buttons
        self.startGameButton = QPushButton("Start Game")
        self.startGameButton.clicked.connect(self.start_game)
        self.vbdock.addWidget(self.startGameButton)

        self.skipTurnButton = QPushButton("Skip Turn")
        self.skipTurnButton.clicked.connect(self.skip_turn)
        self.vbdock.addWidget(self.skipTurnButton)

        # Setting colour of dock to gray
        playerInfo.setAutoFillBackground(True)
        p = playerInfo.palette()
        p.setColor(playerInfo.backgroundRole(), Qt.GlobalColor.gray)
        playerInfo.setPalette(p)

        # set widget for dock
        self.dockInfo.setWidget(playerInfo)

        self.getList("easy")
        self.currentWord = self.getWord()

        # Initialize gameplay state
        self.player1Score = 0
        self.player2Score = 0
        self.currentTurn = 1
        self.totalTurns = 5
        self.currentPlayer = 1  # Player 1 starts

        # Timer for the drawing session
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        # Gameplay state
        self.gameStarted = False
        self.turnTimeLeft = 60  # Set the default turn time (60 seconds)

    # event handlers
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.gameStarted:
            self.drawing = True
            self.lastPoint = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing and self.gameStarted:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
                                Qt.PenJoinStyle.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    # paint events
    def paintEvent(self, event):
        canvasPainter = QPainter(self)
        canvasPainter.drawPixmap(QPoint(), self.image)

    # resize event
    def resizeEvent(self, event):
        self.image = self.image.scaled(self.width(), self.height())

    # slots
    def save(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                                                  "PNG(*.png);;JPG(*.jpg *.jpeg);;All Files (*.*)")
        if filePath == "":
            return
        self.image.save(filePath)

    def clear(self):
        self.image.fill(Qt.GlobalColor.white)
        self.update()

    def threepx(self):
        self.brushSize = 3
        self.thicknessLabel.setText(f"Brush Thickness: {self.brushSize}px")

    def fivepx(self):
        self.brushSize = 5
        self.thicknessLabel.setText(f"Brush Thickness: {self.brushSize}px")

    def sevenpx(self):
        self.brushSize = 7
        self.thicknessLabel.setText(f"Brush Thickness: {self.brushSize}px")

    def ninepx(self):
        self.brushSize = 9
        self.thicknessLabel.setText(f"Brush Thickness: {self.brushSize}px")

    def black(self):
        self.brushColor = Qt.GlobalColor.black
        self.colorLabel.setText("Selected Color: Black")
        self.colorLabel.setStyleSheet("background-color: black; color: white")

    def red(self):
        self.brushColor = Qt.GlobalColor.red
        self.colorLabel.setText("Selected Color: Red")
        self.colorLabel.setStyleSheet("background-color: red; color: white")

    def green(self):
        self.brushColor = Qt.GlobalColor.green
        self.colorLabel.setText("Selected Color: Green")
        self.colorLabel.setStyleSheet("background-color: green; color: white")

    def yellow(self):
        self.brushColor = Qt.GlobalColor.yellow
        self.colorLabel.setText("Selected Color: Yellow")
        self.colorLabel.setStyleSheet("background-color: yellow; color: black")

    # Gameplay information update methods
    def update_turn(self):
        self.turnLabel.setText(f"Turn {self.currentTurn} of {self.totalTurns}")
        self.currentPlayerLabel.setText(f"Current Player: Player {self.currentPlayer}")

    def update_score(self, player, points):
        if player == 1:
            self.player1Score += points
            self.scoreLabel1.setText(f"Player 1: {self.player1Score}")
        elif player == 2:
            self.player2Score += points
            self.scoreLabel2.setText(f"Player 2: {self.player2Score}")

    def next_turn(self):
        if self.currentPlayer == 1:
            self.currentPlayer = 2
        else:
            self.currentPlayer = 1
            self.currentTurn += 1
        self.update_turn()

    def getList(self, difficulty):
        self.wordList = ["apple", "banana", "cherry", "date", "elderberry"]
        random.shuffle(self.wordList)

    def getWord(self):
        return self.wordList.pop()

    def start_game(self):
        self.gameStarted = True
        self.update_turn()
        self.timer.start(1000)  # Start timer for the round
        self.startGameButton.setEnabled(False)  # Disable Start Game button

    def skip_turn(self):
        self.next_turn()  # Skip to the next player's turn
        self.turnTimeLeft = 60  # Reset timer for the new turn
        self.timer.start(1000)  # Restart the timer

    def update_timer(self):
        if self.turnTimeLeft > 0:
            self.turnTimeLeft -= 1
            print(f"Time left for Turn: {self.turnTimeLeft} seconds")
        else:
            self.skip_turn()  # Time's up, skip to next turn

    # Help Methods
    def about(self):
        QMessageBox.about(self, "About", "Pictionary Game - A2 Template")

    def help(self):
        help_text = ("How to Draw: Click and drag the mouse to draw on the canvas.\n"
                     "How to select color: Go to Brush Color menu and select a color.\n"
                     "How to select thickness: Go to Brush Size menu and choose the desired thickness.\n"
                     "How to save: Press 'Ctrl + S' to save your drawing.\n"
                     "How to clear: Press 'Ctrl + C' to clear the canvas.")
        QMessageBox.information(self, "Help", help_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PictionaryGame()
    window.show()
    sys.exit(app.exec())
