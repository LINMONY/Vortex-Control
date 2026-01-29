import sys
import ctypes
import os
import subprocess
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QFile, QTextStream

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def force_elevation():
    """Relaunch the script with Admin rights using PowerShell Start-Process -Verb RunAs"""
    print("[SYSTEM] No Admin Rights! Attempting to force UAC...")
    
    script_path = os.path.abspath(sys.argv[0])
    python_exe = sys.executable
    
    # Check if we are running as a script or exe
    # If script, we need: python_exe script_path args
    # If exe/frozen, we need: executable args
    
    if script_path.endswith(".py"):
        # Arguments to pass to the new process
        # We need to wrap paths in quotes to handle spaces
        args_str = f"'{script_path}'" 
        # Add any other sys.argv[1:] if needed, though usually main.py handles its own
        
        # PowerShell command: try to start python with script as argument, verb runas
        # Start-Process "python_exe" -ArgumentList "script_path" -Verb RunAs
        
        cmd = [
            "powershell",
            "-Command",
            f"Start-Process '{python_exe}' -ArgumentList '{args_str}' -Verb RunAs"
        ]
    else:
        # Running as compiled exe (future proofing) or similar
        cmd = [
            "powershell",
            "-Command",
            f"Start-Process '{script_path}' -Verb RunAs"
        ]
        
    try:
        # We use subprocess.call to wait? No, Start-Process returns immediately unless -Wait
        # But we want to exit THIS process immediately after launching the new one.
        subprocess.Popen(cmd, shell=True)
        return True
    except Exception as e:
        print(f"[SYSTEM] Elevation Failed: {e}")
        return False

def check_wmi_access():
    """Verify we can actually read system restore points now."""
    print("[SYSTEM] Verifying WMI Access...")
    try:
        import wmi
        c = wmi.WMI(namespace="root\\default")
        # Just try to get count, don't need full list
        points = c.SystemRestore()
        print(f"[SYSTEM] WMI Access OK. Found {len(points)} system restore points.")
    except Exception as e:
        print(f"[SYSTEM] WMI Warning (Access might still be restricted): {e}")

def main():
    # 1. Check Admin Rights BEFORE creating QApplication to avoid overhead if restarting
    if not is_admin():
        print("[SYSTEM] Current User is NOT Admin.")
        
        # We need a small app just for the MessageBox if we want to ask user
        # But requirement says "Auto Elevation".
        # Let's try to elevate immediately.
        
        if force_elevation():
            print("[SYSTEM] Elevation request sent. Exiting restricted process.")
            sys.exit(0)
        else:
            # Fallback if powershell fails entirely?
            # Initialize minimal app to show error
            app = QApplication(sys.argv)
            QMessageBox.critical(None, "Ошибка запуска", "Не удалось запросить права администратора.\nЗапустите программу вручную от имени администратора.")
            sys.exit(1)
            
    # --- ADMIN RIGHTS GRANTED ---
    print("[SYSTEM] Running with Admin Privileges.")
    
    # verify wmi
    check_wmi_access()
    
    app = QApplication(sys.argv)
    
    # Resolve absolute path
    base_dir = os.path.dirname(os.path.abspath(__file__))
    style_path = os.path.join(base_dir, "ui/styles.qss")

    # Load Stylesheet
    style_file = QFile(style_path)
    if style_file.open(QFile.ReadOnly | QFile.Text):
        stream = QTextStream(style_file)
        app.setStyleSheet(stream.readAll())
        style_file.close()

    from ui.mainwindow import MainWindow
    window = MainWindow()
    
    # Apply Dark Title Bar
    if sys.platform == "win32":
        try:
            hwnd = window.winId()
            ctypes.windll.dwmapi.DwmSetWindowAttribute(int(hwnd), 20, ctypes.byref(ctypes.c_int(1)), 4)
        except Exception as e:
            pass

    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
