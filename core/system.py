import ctypes
import subprocess
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_restore_point(description=None):
    """
    Creates a Windows System Restore Point using PowerShell (Checkpoint-Computer).
    Returns (success: bool, message: str)
    """
    if not is_admin():
        return False, "Требуются права администратора"

    from core.wmi_manager import RestorePointManager
    if description is None:
        description = RestorePointManager.generate_next_name()

    try:
        # Try WMI creation first (faster, purely pythonic if using com)
        success_wmi = RestorePointManager.create_point_wmi(description)
        if success_wmi:
            from core.logger import Logger
            Logger().log_restore_point(description) # Keep logging but list relies on WMI
            return True, "Точка восстановления успешно создана"
        
        # Fallback to PowerShell if WMI method failed (backup)
        cmd = f'Checkpoint-Computer -Description "{description}" -RestorePointType "MODIFY_SETTINGS"'
        import subprocess
        result = subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode == 0:
            from core.logger import Logger
            Logger().log_restore_point(description)
            return True, "Точка восстановления успешно создана (PowerShell)"
        else:
            err = result.stderr.strip()
            return False, f"Ошибка создания: {err}"
            
    except Exception as e:
        return False, f"System error: {str(e)}"

def delete_restore_point_system(point_data):
    """
    Attempts to delete a restore point using a hybrid method (ShadowID or SequenceNumber).
    """
    from core.wmi_manager import RestorePointManager
    return RestorePointManager.delete_restore_point(point_data)

def run_as_admin():
    """Relaunch the app with admin rights"""
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
