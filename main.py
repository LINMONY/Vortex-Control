import sys
import ctypes
import subprocess
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QFile, QTextStream

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def force_elevation():
    """Relaunch the script with Admin rights using PowerShell Start-Process -Verb RunAs"""
    print("[SYSTEM] No Admin Rights! Attempting to force UAC...")
    
    script_path = Path(sys.argv[0]).resolve()
    python_exe = sys.executable
    
    if script_path.suffix == ".py":
        args_str = f"'{script_path}'" 
        cmd = [
            "powershell",
            "-Command",
            f"Start-Process '{python_exe}' -ArgumentList '{args_str}' -Verb RunAs"
        ]
    else:
        cmd = [
            "powershell",
            "-Command",
            f"Start-Process '{script_path}' -Verb RunAs"
        ]
        
    try:
        subprocess.Popen(cmd, shell=True)
        return True
    except Exception as e:
        print(f"[SYSTEM] Elevation Failed: {e}")
        # Show error dialog strictly for elevation failure if app instance exists? 
        # Usually main() handles the failure, but let's ensure we return valid status.
        return False

def main():
    # 1. Check Admin Rights BEFORE creating QApplication to avoid overhead
    if not is_admin():
        print("[SYSTEM] Current User is NOT Admin.")
        
        if force_elevation():
            print("[SYSTEM] Elevation request sent. Exiting restricted process.")
            sys.exit(0)
        else:
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "Ошибка запуска", "Не удалось запросить права администратора.\nЗапустите программу вручную от имени администратора.")
            sys.exit(1)
            
    # --- ADMIN RIGHTS GRANTED ---
    print("[SYSTEM] Running with Admin Privileges.")
    
    app = QApplication(sys.argv)
    
    # Resolve absolute path using pathlib
    base_dir = Path(__file__).resolve().parent
    style_path = base_dir / "ui/styles.qss"

    # Load Stylesheet
    style_file = QFile(str(style_path))
    if style_file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(style_file)
        app.setStyleSheet(stream.readAll())
        style_file.close()

    # DEFERRED IMPORT to avoid circular dependency
    try:
        from ui.mainwindow import MainWindow
    except ImportError as e:
        QMessageBox.critical(None, "Critical Error", f"Failed to import UI components:\n{e}\n\nCheck installation.")
        sys.exit(1)

    window = MainWindow()
    
    # Apply Dark Title Bar
    if sys.platform == "win32":
        try:
            hwnd = window.winId()
            ctypes.windll.dwmapi.DwmSetWindowAttribute(int(hwnd), 20, ctypes.byref(ctypes.c_int(1)), 4)
        except Exception:
            pass

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
