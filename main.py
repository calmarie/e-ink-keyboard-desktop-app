from PySide6.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton

def on_click(index):
    print(f"Нажата кнопка {index+1}")


app = QApplication([])

window = QWidget()
window.setWindowTitle("E-Ink Keyboard")
window.resize(400, 400)

layout = QGridLayout()

# 4 кнопки (твоя клавиатура)
buttons = []

for i in range(4):
    btn = QPushButton(f"Key {i+1}")
    btn.setMinimumSize(100, 100)
    buttons.append(btn)
    btn.clicked.connect(lambda _, x=i: on_click(x))
    layout.addWidget(btn, i // 2, i % 2)

window.setLayout(layout)

window.show()
app.exec()

