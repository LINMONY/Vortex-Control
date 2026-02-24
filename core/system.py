import ctypes
import subprocess
import sys
from pathlib import Path
from core.wmi_manager import RestorePointManager
from core.logger import logger
from core.constants import ErrorMessages

def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def create_restore_point(description: str = None) -> tuple[bool, str]:
    """
    Creates a Windows System Restore Point using PowerShell (Checkpoint-Computer).
    Returns (success: bool, message: str)
    """
    if not is_admin():
        return False, ErrorMessages.ADMIN_REQUIRED

    if description is None:
        description = RestorePointManager.generate_next_name()

    try:
        # Try WMI creation first (faster, purely pythonic if using com)
        success_wmi = RestorePointManager.create_point_wmi(description)
        if success_wmi:
            logger.log_restore_point(description) 
            return True, ErrorMessages.RESTORE_POINT_CREATED
        
        # Fallback to PowerShell if WMI method failed (backup)
        # We carefully quote the description to handle spaces
        cmd = f'Checkpoint-Computer -Description "{description}" -RestorePointType "MODIFY_SETTINGS"'
        
        result = subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode == 0:
            logger.log_restore_point(description)
            return True, ErrorMessages.RESTORE_POINT_CREATED_PS
        else:
            err = result.stderr.strip()
            return False, f"{ErrorMessages.CREATION_ERROR_PREFIX}{err}"
            
    except Exception as e:
        return False, f"{ErrorMessages.SYSTEM_ERROR_PREFIX}{str(e)}"

def delete_restore_point_system(point_data: dict) -> tuple[bool, str]:
    """
    Attempts to delete a restore point using a hybrid method (ShadowID or SequenceNumber).
    """
    return RestorePointManager.delete_restore_point(point_data)

def run_as_admin() -> None:
    """Relaunch the app with admin rights"""
    # Get the absolute path of the script
    script = Path(sys.argv[0]).resolve()
    
    # Construct parameters: quote the script path and any subsequent arguments
    params_list = [f'"{script}"'] + [f'"{arg}"' for arg in sys.argv[1:]]
    params = " ".join(params_list)
    
    directory = str(script.parent)
    
    # execute runas on sys.executable which should be python/pythonw.exe
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, directory, 1)

