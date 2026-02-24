from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QButtonGroup)
from PySide6.QtCore import Qt
from ui.tweaks import TweaksPage
from core.tweak_models import TweakDefinition, TweakCategory
from core.i18n import I18n as _

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
        
        self.add_tab(tabs_layout, _.get("performance"), 0)
        self.add_tab(tabs_layout, _.get("latency"), 1)
        self.add_tab(tabs_layout, _.get("network"), 2)
        self.add_tab(tabs_layout, _.get("other"), 3)

        layout.addWidget(tabs_container)

        # -- Content Stack --
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Performance Tweaks
        perf_tweaks = [
            TweakDefinition(id="power_plan", name_ru=_.get("tweak_power"), category=TweakCategory.PERFORMANCE),
            TweakDefinition(id="mem_prio", name_ru=_.get("tweak_mem"), category=TweakCategory.PERFORMANCE),
            TweakDefinition(id="nvidia_power", name_ru=_.get("tweak_gpu"), category=TweakCategory.PERFORMANCE),
            TweakDefinition(id="fast_boot", name_ru=_.get("tweak_boot"), category=TweakCategory.PERFORMANCE),
            TweakDefinition(id="game_prio", name_ru=_.get("tweak_game"), category=TweakCategory.PERFORMANCE),
            TweakDefinition(id="bg_ops", name_ru=_.get("tweak_bg"), category=TweakCategory.PERFORMANCE),
        ]
        
        # Latency Tweaks
        latency_tweaks = [
            TweakDefinition(id="mouse_accel", name_ru=_.get("tweak_mouse"), category=TweakCategory.LATENCY),
            TweakDefinition(id="startup_delay", name_ru=_.get("tweak_startup"), category=TweakCategory.LATENCY),
            TweakDefinition(id="input_filter", name_ru=_.get("tweak_input"), category=TweakCategory.LATENCY),
            TweakDefinition(id="win_delay", name_ru=_.get("tweak_win_delay"), category=TweakCategory.LATENCY),
        ]

        # Network Tweaks
        net_tweaks = [
            TweakDefinition(id="net_latency", name_ru=_.get("tweak_net_lat"), category=TweakCategory.NETWORK),
            TweakDefinition(id="del_opt", name_ru=_.get("tweak_del_opt"), category=TweakCategory.NETWORK),
            TweakDefinition(id="net_throttle", name_ru=_.get("tweak_throttle"), category=TweakCategory.NETWORK),
        ]

        # Other Tweaks
        other_tweaks = [
            TweakDefinition(id="temp_files", name_ru=_.get("tweak_temp"), category=TweakCategory.OTHER),
            TweakDefinition(id="update_cache", name_ru=_.get("tweak_update"), category=TweakCategory.OTHER),
            TweakDefinition(id="dns_cache", name_ru=_.get("tweak_dns"), category=TweakCategory.OTHER),
        ]

        # Init Pages
        self.stack.addWidget(TweaksPage(_.get("performance"), perf_tweaks))
        self.stack.addWidget(TweaksPage(_.get("latency"), latency_tweaks))
        self.stack.addWidget(TweaksPage(_.get("network"), net_tweaks))
        self.stack.addWidget(TweaksPage(_.get("other"), other_tweaks))

        # Init Pages
        self.stack.addWidget(TweaksPage("Производительность", perf_tweaks))
        self.stack.addWidget(TweaksPage("Задержка", latency_tweaks))
        self.stack.addWidget(TweaksPage("Интернет", net_tweaks))
        self.stack.addWidget(TweaksPage("Прочее", other_tweaks))

        
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
