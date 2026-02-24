"""
Internationalization support for Vortex Control.
"""
from typing import Dict

class I18n:
    RU: Dict[str, str] = {
        "performance": "Производительность",
        "latency": "Задержка",
        "network": "Интернет",
        "power": "Питание",
        "other": "Прочее",
        
        "apply": "Применить",
        "revert": "Откатить",
        "delete": "Удалить",
        "restore": "Восстановить",
        "create": "Создать",
        "refresh": "Обновить",
        
        "start_optimization": "Начать оптимизацию",
        "start_desc": "Нажмите кнопку ниже, чтобы применить\nрекомендованные настройки.",
        "start_title": "Начало использования",
        "update_info": "Информация обновлений",
        "version_info": "У вас актуальная версия: 1.2.0",
        
        "restore_point_created": "Точка восстановления создана",
        "restore_manager": "Менеджер точек восстановления (System Restore)",
        "create_point_btn": "Создать новую точку",
        "scan_system": "Сканирование системы...",
        
        "tweak_power": "Установить схему питания 'Максимальная производительность'",
        "tweak_mem": "Интеллектуальная производительность памяти",
        "tweak_gpu": "Отключить энергосбережение видеокарты NVIDIA",
        "tweak_boot": "Ускорить запуск Windows",
        "tweak_game": "Задать приоритет играм",
        "tweak_bg": "Убрать фоновые операции",
        
        "tweak_mouse": "Убрать ускорение мыши",
        "tweak_startup": "Автозапуск приложений без задержек",
        "tweak_input": "Отключить фильтрацию ввода",
        "tweak_win_delay": "Убрать задержку показа окон",
        
        "tweak_net_lat": "Уменьшить сетевую задержку (TCP NoDelay)",
        "tweak_del_opt": "Отключить оптимизацию доставки",
        "tweak_throttle": "Не ограничивать сетевой трафик",
        
        "tweak_temp": "Очистить временные файлы",
        "tweak_update": "Удалить кэш обновлений",
        "tweak_dns": "Очистить кэш DNS",

        "settings_title": "Настройки системы",
        "scanning_storage": "Место: сканирование...",
        "storage_used": "Занято точками",
        "system_ready": "Система готова к созданию первой точки",
        "settings_saved": "Настройки сохранены",
        
        "error": "Ошибка",
        "success": "Успех",
        "confirm": "Подтверждение",
        "are_you_sure": "Вы уверены?",
        "action_irreversible": "Это действие может быть необратимым.",
    }
    
    @classmethod
    def get(cls, key: str) -> str:
        return cls.RU.get(key, key)

# Convenient alias
_ = I18n.get
