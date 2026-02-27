"""
Central registry for system tweaks management.
Handles registration, application, reversion, and state persistence of system optimizations.
"""
import winreg
import ctypes
import psutil
import subprocess
from typing import Dict, List, Optional, Tuple, Callable
from core.tweak_models import TweakDefinition
from core.config import config
from core.logger import logger
from core.i18n import I18n as _

class TweakRegistry:
    """
    Singleton registry for managing all system tweaks.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TweakRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized: return
        self._tweaks: Dict[str, TweakDefinition] = {}
        self._handlers: Dict[str, Callable[[bool], Tuple[bool, str]]] = {}
        self._register_handlers()
        self._initialized = True

    def register(self, tweak: TweakDefinition):
        """
        Register a new tweak definition.
        
        Args:
            tweak: The TweakDefinition object to register.
        """
        self._tweaks[tweak.id] = tweak
        # Assign handlers/checkers if available
        if tweak.id in self._handlers:
            tweak.apply_func = self._handlers[tweak.id]
        if tweak.id in self._checkers:
            tweak.check_func = self._checkers[tweak.id]

    def get(self, tweak_id: str) -> Optional[TweakDefinition]:
        """Retrieve a tweak definition by ID."""
        return self._tweaks.get(tweak_id)

    def apply_tweak(self, tweak_id: str) -> bool:
        """
        Apply a specific tweak by ID.

        Args:
            tweak_id: ID of the tweak to apply.

        Returns:
            True if applied successfully, False otherwise.
        """
        tweak = self.get(tweak_id)
        if not tweak:
            logger.log_system(f"Tweak not found: {tweak_id}", "ERROR")
            return False
            
        try:
            logger.log_system(f"Applying tweak: {tweak.name_ru}")

            # Execute Logic
            if tweak.apply_func:
                success, msg = tweak.apply_func(True)
            else:
                success, msg = self._apply_registry_generic(tweak, True)
                
            if not success:
                logger.log_system(f"Failed to apply {tweak_id}: {msg}", "ERROR")
                return False
            
            # Save state
            config.set(f"tweak_{tweak_id}", True)
            return True
        except Exception as e:
            logger.log_system(f"Exception applying {tweak_id}: {e}", "ERROR")
            return False

    def revert_tweak(self, tweak_id: str) -> bool:
        """
        Revert a specific tweak by ID.
        """
        tweak = self.get(tweak_id)
        if not tweak: return False
        
        try:
            logger.log_system(f"Reverting tweak: {tweak.name_ru}")
            
            if tweak.apply_func:
                success, msg = tweak.apply_func(False)
            else:
                success, msg = self._apply_registry_generic(tweak, False)
                
            if not success:
                logger.log_system(f"Failed to revert {tweak_id}: {msg}", "ERROR")
                return False
            
            config.set(f"tweak_{tweak_id}", False)
            return True
        except Exception as e:
            logger.log_system(f"Exception reverting {tweak_id}: {e}", "ERROR")
            return False

    def get_status(self, tweak_id: str) -> bool:
        """Check if a tweak is currently enabled by querying the actual system state."""
        tweak = self.get(tweak_id)
        if not tweak: return False
        
        # If it has a custom check function
        if tweak.check_func:
            return tweak.check_func()
            
        # Try generic registry check
        if tweak.registry_path and tweak.value_name:
            return self._check_registry_generic(tweak)
            
        # Fallback to config if no way to verify
        return config.get(f"tweak_{tweak_id}", False)

    def apply_batch(self, tweak_ids: List[str]) -> int:
        """
        Apply a list of tweaks sequentially. 
        """
        if not tweak_ids: return 0
        
        count = 0
        for tid in tweak_ids:
            if self.apply_tweak(tid):
                count += 1
        return count

    # --- Internal Tweak Handlers ---

    def _register_handlers(self):
        self._handlers = {
            "power_plan": self._handler_power_plan,
            "fast_boot": self._handler_fast_boot,
            "mouse_accel": self._handler_mouse_accel,
            "mmcss_gaming": self._handler_mmcss_gaming,
            "tcp_nagle": self._handler_tcp_nagle,
            "net_heuristics": self._handler_net_heuristics,
            "nvidia_msi": self._handler_nvidia_msi,
            "amd_ulps": self._handler_amd_ulps,
            "nv_telemetry": self._handler_nv_telemetry,
        }
        self._checkers = {
            "power_plan": self._check_power_plan,
            "mouse_accel": self._check_mouse_accel,
            "mmcss_gaming": self._check_mmcss_gaming,
            "tcp_nagle": self._check_tcp_nagle,
            "nvidia_msi": self._check_nvidia_msi,
            "amd_ulps": self._check_amd_ulps,
            "nv_telemetry": self._check_nv_telemetry,
        }

    def _apply_registry_generic(self, tweak: TweakDefinition, enable: bool) -> Tuple[bool, str]:
        if not tweak.registry_path or not tweak.value_name:
            return False, "Отсутствуют параметры реестра в конфигурации твика"
            
        value = tweak.value_on if enable else tweak.value_off
        if value is None:
            return False, "Отсутствует значение для применения"

        try:
            parts = tweak.registry_path.split("\\", 1)
            root_str = parts[0].upper()
            sub_key = parts[1] if len(parts) > 1 else ""
            
            root_map = {
                "HKLM": winreg.HKEY_LOCAL_MACHINE,
                "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
                "HKCU": winreg.HKEY_CURRENT_USER,
                "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
                "HKCR": winreg.HKEY_CLASSES_ROOT,
                "HKU": winreg.HKEY_USERS
            }
            
            root = root_map.get(root_str, winreg.HKEY_LOCAL_MACHINE)
            
            # Determine type
            type_map = {
                "REG_DWORD": winreg.REG_DWORD,
                "REG_SZ": winreg.REG_SZ,
                "REG_BINARY": winreg.REG_BINARY,
                "REG_QWORD": winreg.REG_QWORD,
                "REG_MULTI_SZ": winreg.REG_MULTI_SZ,
            }
            v_type = type_map.get(tweak.value_type, winreg.REG_DWORD)
            
            # Format value based on type
            if v_type in (winreg.REG_DWORD, winreg.REG_QWORD):
                value = int(value)
            elif v_type == winreg.REG_SZ:
                value = str(value)
            elif v_type == winreg.REG_MULTI_SZ:
                value = list(value) if isinstance(value, (list, tuple)) else [str(value)]
            elif v_type == winreg.REG_BINARY:
                if not isinstance(value, bytes):
                    value = bytes(value)

            try:
                key = winreg.OpenKey(root, sub_key, 0, winreg.KEY_SET_VALUE)
            except FileNotFoundError:
                key = winreg.CreateKey(root, sub_key)
                
            winreg.SetValueEx(key, tweak.value_name, 0, v_type, value)
            winreg.CloseKey(key)
            return True, f"Успешно установлено значение в реестре"
        except PermissionError as pe:
            # Fallback for protected Services (TrustedInstaller)
            if "CurrentControlSet\\Services\\" in tweak.registry_path and tweak.value_name == "Start":
                try:
                    service_name = tweak.registry_path.split("\\")[-1]
                    start_str = "disabled" if value == 4 else ("demand" if value == 3 else "auto")
                    import subprocess
                    subprocess.run(["sc", "config", service_name, "start=", start_str], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    return True, "Успешно применено через Service Control Manager"
                except Exception as ex:
                    return False, f"Ошибка доступа (TI) и сбой sc: {ex}"
            return False, f"Отказано в доступе к реестру (Запустите от имени Администратора): {pe}"
        except Exception as e:
            return False, f"Ошибка доступа к реестру ({type(e).__name__}): {e}"

    def _check_registry_generic(self, tweak: TweakDefinition) -> bool:
        if not tweak.registry_path or not tweak.value_name:
            return False
            
        try:
            parts = tweak.registry_path.split("\\", 1)
            root_str = parts[0].upper()
            sub_key = parts[1] if len(parts) > 1 else ""
            
            root_map = {
                "HKLM": winreg.HKEY_LOCAL_MACHINE, "HKEY_LOCAL_MACHINE": winreg.HKEY_LOCAL_MACHINE,
                "HKCU": winreg.HKEY_CURRENT_USER, "HKEY_CURRENT_USER": winreg.HKEY_CURRENT_USER,
                "HKCR": winreg.HKEY_CLASSES_ROOT, "HKU": winreg.HKEY_USERS
            }
            root = root_map.get(root_str, winreg.HKEY_LOCAL_MACHINE)
            
            key = winreg.OpenKey(root, sub_key, 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(key, tweak.value_name)
            winreg.CloseKey(key)
            
            # Compare
            expected = tweak.value_on
            if type(val) == int and type(expected) == int:
                return val == expected
            elif type(val) == bytes and type(expected) == bytes:
                return val == expected
            else:
                return str(val) == str(expected)
        except Exception:
            return False

    def _set_reg_dword(self, path: str, name: str, value: int, root=winreg.HKEY_LOCAL_MACHINE) -> bool:
        try:
            key = winreg.OpenKey(root, path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            logger.log_system(f"Registry Write Failed [{path}\\{name}]: {e}", "ERROR")
            return False

    def _handler_power_plan(self, enable: bool) -> Tuple[bool, str]:
        try:
            if enable:
                # High performance plan GUID: 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
                subprocess.run(["powercfg", "/setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return True, "Активирован план высокой производительности"
            else:
                # Balanced plan GUID: 381b4222-f694-41f0-9685-ff5bb260df2e
                subprocess.run(["powercfg", "/setactive", "381b4222-f694-41f0-9685-ff5bb260df2e"], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return True, "Активирован сбалансированный план"
        except Exception as e:
            return False, f"Сбой управления питанием: {e}"
            
    def _handler_fast_boot(self, enable: bool) -> Tuple[bool, str]:
        # Fast Boot depends on Hibernation
        if enable:
            if self._set_reg_dword(r"SYSTEM\CurrentControlSet\Control\Session Manager\Power", "HiberbootEnabled", 1):
                return True, "Быстрый запуск включен"
        else:
            if self._set_reg_dword(r"SYSTEM\CurrentControlSet\Control\Session Manager\Power", "HiberbootEnabled", 0):
                return True, "Быстрый запуск отключен"
        return False, "Сбой записи в реестр"

    def _handler_mouse_accel(self, enable: bool) -> Tuple[bool, str]:
        try:
            # Mouse speed/accel is usually in HKCU\Control Panel\Mouse
            # SmoothMouseXCurve, SmoothMouseYCurve, MouseSpeed, MouseThreshold1, MouseThreshold2
            if enable:
                self._set_reg_dword(r"Control Panel\Mouse", "MouseSpeed", 0, root=winreg.HKEY_CURRENT_USER)
                self._set_reg_dword(r"Control Panel\Mouse", "MouseThreshold1", 0, root=winreg.HKEY_CURRENT_USER)
                self._set_reg_dword(r"Control Panel\Mouse", "MouseThreshold2", 0, root=winreg.HKEY_CURRENT_USER)
                return True, "Ускорение мыши отключено"
            else:
                self._set_reg_dword(r"Control Panel\Mouse", "MouseSpeed", 1, root=winreg.HKEY_CURRENT_USER)
                self._set_reg_dword(r"Control Panel\Mouse", "MouseThreshold1", 6, root=winreg.HKEY_CURRENT_USER)
                self._set_reg_dword(r"Control Panel\Mouse", "MouseThreshold2", 10, root=winreg.HKEY_CURRENT_USER)
                return True, "Сброс ускорения мыши по умолчанию"
        except Exception as e:
            return False, f"Ошибка реестра: {e}"

    def _handler_mmcss_gaming(self, enable: bool) -> Tuple[bool, str]:
        path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games"
        try:
            if enable:
                self._set_reg_dword(path, "GPU Priority", 8)
                self._set_reg_dword(path, "Priority", 6)
                self._set_reg_str(path, "Scheduling Category", "High")
                self._set_reg_str(path, "SFIO Priority", "High")
                return True, "MMCSS Gaming профиль оптимизирован"
            else:
                self._set_reg_dword(path, "GPU Priority", 2)
                self._set_reg_dword(path, "Priority", 2)
                self._set_reg_str(path, "Scheduling Category", "Medium")
                self._set_reg_str(path, "SFIO Priority", "Normal")
                return True, "Сброс MMCSS Gaming профиля"
        except Exception as e:
            return False, f"Ошибка MMCSS: {e}"
            
    def _set_reg_str(self, path: str, name: str, value: str, root=winreg.HKEY_LOCAL_MACHINE) -> bool:
        try:
            key = winreg.OpenKey(root, path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            winreg.CloseKey(key)
            return True
        except Exception:
            return False

    def _handler_tcp_nagle(self, enable: bool) -> Tuple[bool, str]:
        path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
            subkeys = []
            try:
                i = 0
                while True:
                    subkeys.append(winreg.EnumKey(key, i))
                    i += 1
            except OSError:
                pass
                
            val = 1 if enable else 0
            for sub in subkeys:
                sub_path = f"{path}\\{sub}"
                self._set_reg_dword(sub_path, "TcpAckFrequency", val)
                self._set_reg_dword(sub_path, "TCPNoDelay", val)
                self._set_reg_dword(sub_path, "TcpDelAckTicks", 0)
            winreg.CloseKey(key)
            return True, "Алгоритм Нейгла " + ("отключен" if enable else "включен")
        except Exception as e:
            return False, f"Ошибка Tcpip: {e}"

    def _handler_net_heuristics(self, enable: bool) -> Tuple[bool, str]:
        try:
            val = "disabled" if enable else "enabled"
            subprocess.run(["netsh", "int", "tcp", "set", "heuristics", val], check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(["netsh", "int", "tcp", "set", "global", "autotuninglevel=normal"], creationflags=subprocess.CREATE_NO_WINDOW)
            return True, f"Сетевая эвристика {val}"
        except Exception as e:
            return False, f"Сбой netsh: {e}"

    def _handler_nv_telemetry(self, enable: bool) -> Tuple[bool, str]:
        path = r"SOFTWARE\NVIDIA Corporation\Global\NvTelemetry"
        try:
            val = 0 if enable else 1 # If tweak is enabled -> Telemetry=0
            self._set_reg_dword(path, "EnableTelemetry", val)
            self._set_reg_dword(path, "LogEnabled", val)
            return True, "Телеметрия NVIDIA " + ("отключена" if enable else "включена")
        except Exception as e:
            return False, str(e)

    def _handler_nvidia_msi(self, enable: bool) -> Tuple[bool, str]:
        path = r"SYSTEM\CurrentControlSet\Enum\PCI"
        patched = 0
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)
            for i in range(1000):
                try:
                    pci_dev = winreg.EnumKey(key, i)
                    if "VEN_10DE" in pci_dev: # NVIDIA Vendor ID
                        dev_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{path}\\{pci_dev}", 0, winreg.KEY_READ)
                        for j in range(100):
                            try:
                                sub_dev = winreg.EnumKey(dev_key, j)
                                target_path = f"{path}\\{pci_dev}\\{sub_dev}\\Device Parameters\\Interrupt Management\\MessageSignaledInterruptProperties"
                                self._set_reg_dword(target_path, "MSISupported", 1 if enable else 0)
                                patched += 1
                            except OSError: break
                        winreg.CloseKey(dev_key)
                except OSError: break
            winreg.CloseKey(key)
            if patched > 0:
                return True, "MSI Mode для GPU " + ("активирован" if enable else "деактивирован")
            return False, "NVIDIA GPU не найден в реестре"
        except Exception as e:
            return False, f"Ошибка поиска PCI: {e}"

    def _handler_amd_ulps(self, enable: bool) -> Tuple[bool, str]:
        path = r"SYSTEM\CurrentControlSet\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
        patched = 0
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)
            for i in range(100):
                try:
                    sub = winreg.EnumKey(key, i)
                    sub_path = f"{path}\\{sub}"
                    sub_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub_path, 0, winreg.KEY_READ | winreg.KEY_WRITE)
                    
                    # Check if it has EnableUlps
                    try:
                        winreg.QueryValueEx(sub_key, "EnableUlps")
                        winreg.SetValueEx(sub_key, "EnableUlps", 0, winreg.REG_DWORD, 0 if enable else 1)
                        patched += 1
                    except FileNotFoundError: pass
                    winreg.CloseKey(sub_key)
                except OSError: break
            winreg.CloseKey(key)
            if patched > 0:
                return True, "AMD ULPS " + ("отключен" if enable else "включен")
            return False, "Ключ EnableUlps не найден на данной системе"
        except Exception as e:
            return False, f"Ошибка реестра: {e}"

    # Checkers
    def _check_power_plan(self) -> bool:
        try:
            out = subprocess.check_output(["powercfg", "/getactivescheme"], creationflags=subprocess.CREATE_NO_WINDOW).decode('cp866', errors='ignore')
            return "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c" in out.lower()
        except: return False

    def _check_mouse_accel(self) -> bool:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Mouse", 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(key, "MouseSpeed")
            winreg.CloseKey(key)
            return str(val) == "0"
        except: return False

    def _check_mmcss_gaming(self) -> bool:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games", 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(key, "GPU Priority")
            winreg.CloseKey(key)
            return int(val) == 8
        except: return False

    def _check_tcp_nagle(self) -> bool:
        path = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)
            sub = winreg.EnumKey(key, 0)
            sub_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{path}\\{sub}", 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(sub_key, "TcpAckFrequency")
            winreg.CloseKey(key); winreg.CloseKey(sub_key)
            return int(val) == 1
        except: return False

    def _check_nv_telemetry(self) -> bool:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\NVIDIA Corporation\Global\NvTelemetry", 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(key, "EnableTelemetry")
            winreg.CloseKey(key)
            return int(val) == 0
        except: return False
        
    def _check_nvidia_msi(self) -> bool:
        path = r"SYSTEM\CurrentControlSet\Enum\PCI"
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)
            for i in range(1000):
                try:
                    pci_dev = winreg.EnumKey(key, i)
                    if "VEN_10DE" in pci_dev:
                        dev_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{path}\\{pci_dev}", 0, winreg.KEY_READ)
                        sub_dev = winreg.EnumKey(dev_key, 0)
                        target_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{path}\\{pci_dev}\\{sub_dev}\\Device Parameters\\Interrupt Management\\MessageSignaledInterruptProperties", 0, winreg.KEY_READ)
                        val, _ = winreg.QueryValueEx(target_key, "MSISupported")
                        winreg.CloseKey(target_key); winreg.CloseKey(dev_key)
                        return int(val) == 1
                except OSError: pass
            winreg.CloseKey(key)
            return False
        except: return False

    def _check_amd_ulps(self) -> bool:
        path = r"SYSTEM\CurrentControlSet\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_READ)
            for i in range(100):
                try:
                    sub = winreg.EnumKey(key, i)
                    sub_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, f"{path}\\{sub}", 0, winreg.KEY_READ)
                    try:
                        val, _ = winreg.QueryValueEx(sub_key, "EnableUlps")
                        winreg.CloseKey(sub_key)
                        return int(val) == 0
                    except FileNotFoundError: pass
                    winreg.CloseKey(sub_key)
                except OSError: break
            winreg.CloseKey(key)
            return False
        except: return False

registry = TweakRegistry()
