"""
Central registry for system tweaks management.
Handles registration, application, reversion, and state persistence of system optimizations.
"""
import winreg
import ctypes
import psutil
from typing import Dict, List, Optional, Tuple, Callable
from core.tweak_models import TweakDefinition
from core.config import config
from core.logger import logger
from core.wmi_manager import RestorePointManager
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
        # Assign handler if available
        if tweak.id in self._handlers:
            tweak.apply_func = self._handlers[tweak.id]

    def get(self, tweak_id: str) -> Optional[TweakDefinition]:
        """Retrieve a tweak definition by ID."""
        return self._tweaks.get(tweak_id)

    def apply_tweak(self, tweak_id: str, create_checkpoint: bool = False) -> bool:
        """
        Apply a specific tweak by ID.

        Args:
            tweak_id: ID of the tweak to apply.
            create_checkpoint: Whether to create a system restore point before applying.

        Returns:
            True if applied successfully, False otherwise.
        """
        tweak = self.get(tweak_id)
        if not tweak:
            logger.log_system(f"Tweak not found: {tweak_id}", "ERROR")
            return False
            
        try:
            logger.log_system(f"Applying tweak: {tweak.name_ru}")
            
            if create_checkpoint:
                # Safety First
                RestorePointManager.create_point_wmi(f"Pre-Tweak: {tweak.name_ru}")

            # Execute Logic
            if tweak.apply_func:
                success, msg = tweak.apply_func(True)
                if not success:
                    logger.log_system(f"Failed to apply {tweak_id}: {msg}", "ERROR")
                    return False
            else:
                logger.log_system(f"No handler for {tweak_id}, simulating success.", "WARNING")
            
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
                if not success:
                    logger.log_system(f"Failed to revert {tweak_id}: {msg}", "ERROR")
                    return False
            
            config.set(f"tweak_{tweak_id}", False)
            return True
        except Exception as e:
            logger.log_system(f"Exception reverting {tweak_id}: {e}", "ERROR")
            return False

    def get_status(self, tweak_id: str) -> bool:
        """Check if a tweak is currently enabled via config."""
        return config.get(f"tweak_{tweak_id}", False)

    def apply_batch(self, tweak_ids: List[str]) -> int:
        """
        Apply a list of tweaks sequentially. 
        Creates ONE restore point for the batch.
        """
        if not tweak_ids: return 0
        
        RestorePointManager.create_point_wmi("Vortex Batch Optimization")
        
        count = 0
        for tid in tweak_ids:
            # We skip individual checkpoints for batch
            if self.apply_tweak(tid, create_checkpoint=False):
                count += 1
        return count

    # --- Internal Tweak Handlers ---

    def _register_handlers(self):
        self._handlers = {
            "disable_paging_exec": self._handler_paging_executive,
            "large_system_cache": self._handler_system_cache,
            # Placeholder mappings for others
            "power_plan": self._handler_placeholder,
        }

    def _set_reg_dword(self, path: str, name: str, value: int) -> bool:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            winreg.CloseKey(key)
            return True
        except Exception as e:
            logger.log_system(f"Registry Write Failed [{path}\\{name}]: {e}", "ERROR")
            return False

    def _handler_paging_executive(self, enable: bool) -> Tuple[bool, str]:
        """
        DisablePagingExecutive: Keeps kernel drivers in RAM.
        Recommended only for >8GB RAM.
        """
        key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
        ram_gb = psutil.virtual_memory().total / (1024**3)
        
        if enable:
            if ram_gb < 8:
                return False, "Not enough RAM (<8GB)"
            if self._set_reg_dword(key_path, "DisablePagingExecutive", 1):
                return True, "Kernel paging disabled"
        else:
            if self._set_reg_dword(key_path, "DisablePagingExecutive", 0):
                return True, "Reverted to default"
                
        return False, "Registry access failed"

    def _handler_system_cache(self, enable: bool) -> Tuple[bool, str]:
        """
        LargeSystemCache: Optimizes file system cache.
        Recommended for servers or high-RAM systems (>16GB).
        """
        key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
        ram_gb = psutil.virtual_memory().total / (1024**3)
        
        if enable:
            if ram_gb < 16:
                return False, "Not enough RAM (<16GB)"
            if self._set_reg_dword(key_path, "LargeSystemCache", 1):
                return True, "Large System Cache enabled"
        else:
            if self._set_reg_dword(key_path, "LargeSystemCache", 0):
                return True, "Reverted to default"
                
        return False, "Registry access failed"

    def _handler_placeholder(self, enable: bool) -> Tuple[bool, str]:
        return True, "Simulated action completed"

registry = TweakRegistry()
