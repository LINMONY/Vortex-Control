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
        
        self.add_tab(tabs_layout, "Производительность", 0)
        self.add_tab(tabs_layout, "Задержка", 1)
        self.add_tab(tabs_layout, "Сеть", 2)
        self.add_tab(tabs_layout, "Службы", 3)
        self.add_tab(tabs_layout, "Приватность", 4)

        layout.addWidget(tabs_container)

        # -- Content Stack --
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Performance Tweaks (FPS / CPU / Memory)
        perf_tweaks = [
            TweakDefinition(id="power_plan", name_ru="Схема Максимальной Производительности", category=TweakCategory.PERFORMANCE, 
                            detailed_info="Активирует скрытую схему питания 'Высокая производительность' (powercfg). Снимает агрессивные функции энергосбережения ЦП (Power Throttling)."),
            TweakDefinition(id="power_throttling", name_ru="Отключить Power Throttling", category=TweakCategory.PERFORMANCE,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerThrottling",
                            value_name="PowerThrottlingOff", value_on=1, value_off=0,
                            detailed_info="Запрещает Windows принудительно снижать рабочие частоты процессора для фоновых и неактивных процессов. Путь: HKLM\\...\\PowerThrottling"),
            TweakDefinition(id="disable_paging_exec", name_ru="Не выгружать ядро в файл подкачки", category=TweakCategory.PERFORMANCE,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
                            value_name="DisablePagingExecutive", value_on=1, value_off=0,
                            detailed_info="Удерживает системные драйверы и ядро (Kernel) строго в высокоскоростной RAM, минуя медленный диск (DisablePagingExecutive=1)."),
            TweakDefinition(id="large_system_cache", name_ru="Увеличить системный кэш (RAM)", category=TweakCategory.PERFORMANCE,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
                            value_name="LargeSystemCache", value_on=1, value_off=0,
                            detailed_info="Отдает приоритет оперативной памяти для кэширования файловых операций, улучшая общую пропускную способность ОС."),
            TweakDefinition(id="hw_sch_mode", name_ru="Аппаратное ускорение графики (HAGS)", category=TweakCategory.PERFORMANCE,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                            value_name="HwSchMode", value_on=2, value_off=1,
                            detailed_info="Hardware-Accelerated GPU Scheduling. Позволяет видеокарте самой управлять своей видеопамятью, разгружая ЦП. Путь: HKLM\\...\\GraphicsDrivers"),
            TweakDefinition(id="mmcss_gaming", name_ru="Игровой профиль MMCSS", category=TweakCategory.PERFORMANCE,
                            registry_path=r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games",
                            detailed_info="Жестко переназначает параметры планировщика мультимедиа (Tasks\\Games): GPU Priority=8, Priority=6, Scheduling Category=High."),
            TweakDefinition(id="fast_boot", name_ru="Быстрый запуск Windows (Fastboot)", category=TweakCategory.PERFORMANCE,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power",
                            detailed_info="Параметр HiberbootEnabled. Отключение полезно для идеального аптайма без багов гибернации, включение - для моментального старта ПК."),
            TweakDefinition(id="game_dvr", name_ru="Отключить Xbox Game DVR / Game Bar", category=TweakCategory.PERFORMANCE,
                            registry_path=r"HKCU\System\GameConfigStore",
                            value_name="GameDVR_Enabled", value_on=0, value_off=1,
                            detailed_info="Убирает лишние невидимые оверлеи Microsoft и фоновую запись экрана, повышая итоговый FPS."),
            TweakDefinition(id="fbl", name_ru="Отключить Fullscreen Borderless Optimizations", category=TweakCategory.PERFORMANCE,
                            registry_path=r"HKCU\System\GameConfigStore",
                            value_name="GameDVR_DXGIHonorFSEWindowsCompatible", value_on=0, value_off=1,
                            detailed_info="Запрещает Windows 11 применять 'Оптимизацию в оконном режиме', которая может ломать эксклюзивный полный экран."),
            TweakDefinition(id="cpu_core_parking", name_ru="Отключить парковку ядер ЦП (100% Active)", category=TweakCategory.PERFORMANCE,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\0cc5b647-c1df-4637-891a-dec35c318583",
                            value_name="ValueMax", value_on=0, value_off=100,
                            detailed_info="Отключает агрессивную экономию энергии на многоядерных процессорах (AMD Ryzen / Intel Core), заставляя ядра всегда быть готовыми к нагрузке."),
            TweakDefinition(id="mem_compression", name_ru="Отключить сжатие памяти (Memory Compression)", category=TweakCategory.PERFORMANCE,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management",
                            value_name="DisableMemoryCompression", value_on=1, value_off=0,
                            detailed_info="При достатке ОЗУ (>16ГБ) отключает сжатие страниц памяти силами процессора. Снижает нагрузку на CPU в тяжелых играх."),
            TweakDefinition(id="energy_estim", name_ru="Отключить службу Energy Estimation", category=TweakCategory.PERFORMANCE,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Control\Power\EnergyEstimation",
                            value_name="Enabled", value_on=0, value_off=1,
                            detailed_info="Системный таймер собирает статистику батареи даже на десктопах, тратя ресурсы CPU. Отключение убирает лишние прерывания."),
            TweakDefinition(id="svchost_split", name_ru="Оптимизация упаковки Svchost (>8GB RAM)", category=TweakCategory.PERFORMANCE,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Control",
                            value_name="SvcHostSplitThresholdInKB", value_on=8388608, value_off=380000,
                            detailed_info="Разделяет службы в отдельные процессы для большей стабильности системы, требуются современные процессоры и много ОЗУ."),
            TweakDefinition(id="tpm_opt", name_ru="Снизить нагрузку TPM поллинга", category=TweakCategory.PERFORMANCE,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Services\Tpm\WMI",
                            value_name="NoTpmToWmi", value_on=1, value_off=0,
                            detailed_info="Отключает постоянный опрос TPM модуля через WMI, устраняя микро-статтеры на AMD Ryzen (fTPM stutter fixes).", hardware_tags=["AMD_CPU"]),
            TweakDefinition(id="igpu_multi", name_ru="iGPU Multi-Monitor отключение", category=TweakCategory.PERFORMANCE,
                            hardware_tags=["INTEL_CPU", "AMD_CPU"],
                            detailed_info="Требуется аппаратное отключение iGPU в BIOS для снижения DPC задержек и освобождения линий PCIe.")
        ]
        
        # Latency Tweaks (Input Lag / Snappiness)
        latency_tweaks = [
            TweakDefinition(id="win32_priority", name_ru="Абсолютный приоритет Win32 (0x26)", category=TweakCategory.LATENCY,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl",
                            value_name="Win32PrioritySeparation", value_on=38, value_off=2,
                            detailed_info="Выделяет активному процессу (игре) максимальные короткие кванты процессорного времени (Значение 38 / Hex 26)."),
            TweakDefinition(id="timer_res", name_ru="Отключить коалесцирование таймеров (HPET)", category=TweakCategory.LATENCY,
                            registry_path=r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
                            value_name="TimerResolution", value_on=0, value_off=1,
                            detailed_info="Снижает системную задержку, отключая группировку прерываний таймера и заставляя ОС реагировать немедленно (TimerResolution=0)."),
            TweakDefinition(id="disable_fse", name_ru="Классический эксклюзивный Fullscreen", category=TweakCategory.LATENCY,
                            registry_path=r"HKCU\System\GameConfigStore",
                            value_name="GameDVR_FSEBehaviorMode", value_on=2, value_off=0,
                            detailed_info="Возвращает классический эксклюзивный полный экран (FSE), убирая композитор DWM и снижая инпут-лаг на уровне Desktop Window Manager."),
            TweakDefinition(id="disable_mpo", name_ru="Отключить Multiplane Overlay (MPO)", category=TweakCategory.LATENCY,
                            registry_path=r"HKLM\SOFTWARE\Microsoft\Windows\Dwm",
                            value_name="OverlayTestMode", value_on=5, value_off=0,
                            detailed_info="Фиксит мерцания и микрофризы современных видеокарт (Nvidia/AMD), отключая композитные MPO слои (OverlayTestMode=5)."),
            TweakDefinition(id="nvidia_msi", name_ru="NVIDIA MSI Mode (Прерывания ядра)", category=TweakCategory.LATENCY,
                            hardware_tags=["NVIDIA"],
                            detailed_info="АКТИВИРУЕТ Message Signaled Interrupts для видеокарты. Сокращает задержку обработки прерываний DPC/ISR, напрямую связывая GPU и CPU."),
            TweakDefinition(id="amd_ulps", name_ru="Отключить AMD ULPS (Энергосбережение)", category=TweakCategory.LATENCY,
                            hardware_tags=["AMD_GPU"],
                            detailed_info="Запрещает видеокарте Radeon падать в глубокий сон (Ultra Low Power State). Фиксит статтеры при резкой нагрузке в играх."),
            TweakDefinition(id="mouse_accel", name_ru="Убрать RAW ускорение мыши", category=TweakCategory.LATENCY,
                            registry_path=r"HKCU\Control Panel\Mouse",
                            detailed_info="Вносит нулевые параметры в MouseSpeed, MouseThreshold1(2). Предоставляет идеальный 1:1 аим без системной интерполяции курсора."),
            TweakDefinition(id="kb_delay", name_ru="Минимальная задержка ввода (Клавиатура)", category=TweakCategory.LATENCY,
                            registry_path=r"HKCU\Control Panel\Keyboard",
                            value_name="KeyboardDelay", value_on="0", value_off="1", value_type="REG_SZ",
                            detailed_info="Ускоряет время до повторного срабатывания клавиши. Путь: HKCU\\Control Panel\\Keyboard (KeyboardDelay=0)"),
            TweakDefinition(id="win_delay", name_ru="Мгновенное раскрытие меню", category=TweakCategory.LATENCY,
                            registry_path=r"HKCU\Control Panel\Desktop",
                            value_name="MenuShowDelay", value_on="0", value_off="400", value_type="REG_SZ",
                            detailed_info="Уменьшает задержку раскрытия подменю (ContextMenu) в интерфейсе с 400мс до 0мс (MenuShowDelay=00)."),
            TweakDefinition(id="win_anim", name_ru="Отключить системные анимации DWM", category=TweakCategory.LATENCY,
                            registry_path=r"HKCU\Control Panel\Desktop",
                            value_name="UserPreferencesMask", value_on=b'\x90\x12\x03\x80\x10\x00\x00\x00', value_off=b'\x9E\x3E\x07\x80\x12\x00\x00\x00', value_type="REG_BINARY",
                            detailed_info="Убивает все затухания, анимации сворачивания/разворачивания, делая интерфейс максимально острым."),
            TweakDefinition(id="max_prerender", name_ru="Max Pre-Rendered Frames = 1", category=TweakCategory.LATENCY,
                            registry_path=r"HKLM\SOFTWARE\WOW6432Node\Microsoft\Direct3D",
                            value_name="MaxPreRenderedFrames", value_on=1, value_off=3,
                            detailed_info="Собственный драйвер DirectX. Заставляет CPU подготавливать не более 1 кадра заранее. Снижает input lag ценой возможной потери пары FPS."),
            TweakDefinition(id="tdr_level", name_ru="Отключить GPU TDR (Таймаут восстановления)", category=TweakCategory.LATENCY,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers",
                            value_name="TdrLevel", value_on=0, value_off=3,
                            detailed_info="ОПАСТНЫЙ ТВИК: Отключает Timeout Detection and Recovery. Предотвращает микро-фриз, если видеодрайвер задумался, но при сбое придется перезагружать ПК."),
            TweakDefinition(id="usb_polling", name_ru="Оптимизация опроса USB (Poling Rate)", category=TweakCategory.LATENCY,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Control\usbstor",
                            value_name="ErrorRecoveryTimeout", value_on=1000, value_off=5000,
                            detailed_info="Сокращает время ожидания ответа USB-контроллера. Общая стабилизация шины для игровых периферийных устройств 1000Hz+.")
        ]

        # Network Tweaks (Ping / Packet Loss)
        net_tweaks = [
            TweakDefinition(id="tcp_nagle", name_ru="Отключить алгоритм Нейгла (TcpNoDelay/AckFreq)", category=TweakCategory.NETWORK,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces",
                            detailed_info="Критический твик для онлайн-шутеров. Модулирует TcpAckFrequency=1 на всех сетевых интерфейсах, отправляя мелкие пакеты мгновенно без склейки."),
            TweakDefinition(id="net_heuristics", name_ru="Отключить сетевую эвристику (Disable Heuristics)", category=TweakCategory.NETWORK,
                            detailed_info="Дезактивирует Window Auto-Tuning heuristics (netsh int tcp set heuristics disabled), стабилизируя пинг."),
            TweakDefinition(id="system_resp", name_ru="Приоритет сети для игр (SystemResponsiveness=10)", category=TweakCategory.NETWORK,
                            registry_path=r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
                            value_name="SystemResponsiveness", value_on=10, value_off=20,
                            detailed_info="Снижает резерв ЦП для фоновой сети. Значение 10 выделяет 90% вычислительных мощностей активной игре."),
            TweakDefinition(id="net_throttle", name_ru="Снять лимит сетевого трафика мультимедиа", category=TweakCategory.NETWORK,
                            registry_path=r"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile",
                            value_name="NetworkThrottlingIndex", value_on=4294967295, value_off=10,
                            detailed_info="Снимает 10-пакетный встроенный лимит ОС. Необходим для игр с огромным тикрейтом (Valorant, CS2 - 0xFFFFFFFF)."),
            TweakDefinition(id="del_opt", name_ru="Отключить Оптимизацию доставки (P2P Updates)", category=TweakCategory.NETWORK,
                            registry_path=r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DeliveryOptimization",
                            value_name="DODownloadMode", value_on=0, value_off=3,
                            detailed_info="Запрещает раздавать загруженные апдейты Windows другим устройствам в интернете с вашего ПК."),
            TweakDefinition(id="disable_ndu", name_ru="Отключить мониторинг сети драйвером NDU", category=TweakCategory.NETWORK,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Services\Ndu",
                            value_name="Start", value_on=4, value_off=2,
                            detailed_info="Отключает службу Network Data Usage. Предотвращает колоссальные утечки невыгружаемого пула памяти и статтеры в онлайн-каст сценах."),
            TweakDefinition(id="tcp_offload", name_ru="Отключить аппаратную разгрузку TCP/IP", category=TweakCategory.NETWORK,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                            value_name="DisableTaskOffload", value_on=1, value_off=0,
                            detailed_info="Переносит обработку TCP/IP с дешевых чипов сетевых карт (Realtek) на мощный центральный процессор. Снижает джиттер и пакетлосс."),
            TweakDefinition(id="autotuning", name_ru="Строгий уровень TCP AutoTuning", category=TweakCategory.NETWORK,
                            detailed_info="Рекомендуется установить 'netsh int tcp set global autotuninglevel=restricted'. Обрабатывается в хендлере Net Heuristics.")
        ]

        # Services Tweaks (Atlas-OS approach - Debloat Background)
        services_tweaks = [
            TweakDefinition(id="disable_sysmain", name_ru="Отключить SysMain (SuperFetch)", category=TweakCategory.OTHER,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Services\SysMain",
                            value_name="Start", value_on=4, value_off=2,
                            detailed_info="Предзагрузка RAM. MUST HAVE ДЛЯ ОС НА SSD. Обязательно к отключению, освобождает диск и память от ненужного кэширования."),
            TweakDefinition(id="disable_ws", name_ru="Отключить Windows Search (Индексатор)", category=TweakCategory.OTHER,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Services\WSearch",
                            value_name="Start", value_on=4, value_off=2,
                            detailed_info="Отключает постоянное сканирование файлов на жестком диске. Резко снижает Disk 100% Usage в диспетчере задач."),
            TweakDefinition(id="disable_pca", name_ru="Отключить Службу Совместимости (PCA)", category=TweakCategory.OTHER,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Services\PcaSvc",
                            value_name="Start", value_on=4, value_off=2,
                            detailed_info="Program Compatibility Assistant постоянно мониторит запуск КАЖДОГО .exe файла. Отключение экономит заметный процент CPU."),
            TweakDefinition(id="disable_wer", name_ru="Отключить Отчеты об ошибках (WER)", category=TweakCategory.OTHER,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Services\WerSvc",
                            value_name="Start", value_on=4, value_off=3,
                            detailed_info="Windows Error Reporting. Предотвращает дамп памяти и загрузку сети, когда какая-то программа крашится."),
            TweakDefinition(id="bg_ops", name_ru="Глобальная блокировка фоновых (UWP) приложений", category=TweakCategory.OTHER,
                            registry_path=r"HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications",
                            value_name="GlobalUserDisabled", value_on=1, value_off=0,
                            detailed_info="Полностью убивает фоновое выполнение всех встроенных Metro/UWP приложений Windows."),
            TweakDefinition(id="print_spooler", name_ru="Отключить Диспетчер печати", category=TweakCategory.OTHER,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Services\Spooler",
                            value_name="Start", value_on=4, value_off=2,
                            detailed_info="Отключает службу Print Spooler. Включать только если у вас физически подключен принтер."),
            TweakDefinition(id="fax_service", name_ru="Отключить службу Fax", category=TweakCategory.OTHER,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Services\Fax",
                            value_name="Start", value_on=4, value_off=3,
                            detailed_info="Легаси-служба, абсолютно бесполезна в 2025 году."),
            TweakDefinition(id="biometric", name_ru="Биометрическая служба Windows", category=TweakCategory.OTHER,
                            registry_path=r"HKLM\SYSTEM\CurrentControlSet\Services\WbioSrvc",
                            value_name="Start", value_on=4, value_off=3,
                            detailed_info="Используется только для отпечатков пальцев ноутбуков или FaceID. Для десктопов можно смело вырубать.")
        ]

        # Privacy & OS Bloat Tweaks
        privacy_tweaks = [
            TweakDefinition(id="disable_telemetry", name_ru="Отключить глубокую телеметрию Windows", category=TweakCategory.OTHER,
                            registry_path=r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection",
                            value_name="AllowTelemetry", value_on=0, value_off=1,
                            detailed_info="Блокирует отправку отладочных пакетов и диагностической телеметрии на сервера Microsoft (AllowTelemetry=0)."),
            TweakDefinition(id="nv_telemetry", name_ru="Отключить агрессивную телеметрию NVIDIA", category=TweakCategory.OTHER,
                            registry_path=r"HKLM\SOFTWARE\NVIDIA Corporation\Global\NvTelemetry", hardware_tags=["NVIDIA"],
                            detailed_info="Блокирует процессы NvTelemetry (NvContainer), которые постоянно работают в фоне, собирают инфу и нагружают сеть."),
            TweakDefinition(id="cortana", name_ru="Отключить Cortana & Windows Search Web", category=TweakCategory.OTHER,
                            registry_path=r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search",
                            value_name="AllowCortana", value_on=0, value_off=1,
                            detailed_info="Вырезает голосового ассистента и запрещает меню пуск искать веб-результаты в интернете (bing)."),
            TweakDefinition(id="telemetry_tasks", name_ru="Отключить Телеметрию Планировщика (CEIP)", category=TweakCategory.OTHER,
                            registry_path=r"HKLM\SOFTWARE\Microsoft\SQMClient\Windows",
                            value_name="CEIPEnable", value_on=0, value_off=1,
                            detailed_info="Customer Experience Improvement Program. Дополнительный слой сбора данных Microsoft."),
            TweakDefinition(id="temp_files", name_ru="Очищать кэш истории (RecentDocs) при выходе", category=TweakCategory.OTHER,
                            registry_path=r"HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
                            value_name="ClearRecentDocsOnExit", value_on=1, value_off=0,
                            detailed_info="Повышает конфиденциальность, убивая списки Quick Access и 'Недавние документы'."),
            TweakDefinition(id="activity_history", name_ru="Отключить историю активности (Timeline)", category=TweakCategory.OTHER,
                            registry_path=r"HKLM\SOFTWARE\Policies\Microsoft\Windows\System",
                            value_name="EnableActivityFeed", value_on=0, value_off=1,
                            detailed_info="Освобождает CPU от логирования всего, что вы открываете. Убирает 'Временную шкалу'."),
            TweakDefinition(id="consumer_features", name_ru="Отключить Consumer Features (App Promos)", category=TweakCategory.OTHER,
                            registry_path=r"HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent",
                            value_name="DisableWindowsConsumerFeatures", value_on=1, value_off=0,
                            detailed_info="Запрещает Windows 10/11 автоматически скачивать и подсовывать TikTok, CandyCrush и другой рекламный мусор в меню Пуск.")
        ]

        # Init Pages
        self.stack.addWidget(TweaksPage("Производительность", perf_tweaks))
        self.stack.addWidget(TweaksPage("Минимальная задержка", latency_tweaks))
        self.stack.addWidget(TweaksPage("Оптимизация сети", net_tweaks))
        self.stack.addWidget(TweaksPage("Службы", services_tweaks))
        self.stack.addWidget(TweaksPage("Приватность", privacy_tweaks))
        
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
