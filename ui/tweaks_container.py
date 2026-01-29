from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QButtonGroup)
from PySide6.QtCore import Qt
from ui.tweaks import TweaksPage

class TweaksContainer(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 20)
        layout.setSpacing(15)

        # -- Top Tab Bar --
        tabs_container = QWidget()
        tabs_layout = QHBoxLayout(tabs_container)
        tabs_layout.setContentsMargins(0, 0, 0, 0)
        tabs_layout.setSpacing(20)
        tabs_layout.setAlignment(Qt.AlignLeft)

        self.tab_group = QButtonGroup(self)
        self.tab_group.setExclusive(True)
        
        self.add_tab(tabs_layout, "Производительность", 0)
        self.add_tab(tabs_layout, "Задержка", 1)
        self.add_tab(tabs_layout, "Интернет", 2)
        self.add_tab(tabs_layout, "Прочее", 3)

        layout.addWidget(tabs_container)

        # -- Content Stack --
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Init Pages
        self.stack.addWidget(TweaksPage("Производительность", [
            "Установить схему питания", "Интеллектуальная производительность памяти",
            "Отключить энергосбережение видеокарты NVIDIA", "Ускорить запуск Windows",
            "Задать приоритет играм", "Убрать фоновые операции"
        ]))
        
        self.stack.addWidget(TweaksPage("Задержка", [
            "Убрать ускорение мыши", "Автозапуск приложений без задержек",
            "Отключить фильтрацию ввода", "Убрать задержку показа окон"
        ]))

        self.stack.addWidget(TweaksPage("Интернет", [
            "Уменьшить сетевую задержку", "Отключить оптимизацию доставки",
            "Не ограничивать сетевой трафик"
        ]))
        
        self.stack.addWidget(TweaksPage("Прочее", [
            "Очистить временные файлы", "Удалить кэш обновлений", "Очистить кэш DNS"
        ]))
        
        # Select first
        self.tab_group.button(0).setChecked(True)

    def add_tab(self, layout, text, index):
        btn = QPushButton(text)
        btn.setObjectName("tabButton")
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda: self.stack.setCurrentIndex(index))
        layout.addWidget(btn)
        self.tab_group.addButton(btn, index)
