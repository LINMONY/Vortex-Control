import subprocess
import json
from datetime import datetime, timedelta
from core.ps_scripts import (
    GET_RESTORE_POINTS_PS, 
    DELETE_SHADOW_PS, 
    DELETE_SYSTEM_PS, 
    GET_STORAGE_INFO_PS,
    CHECKPOINT_COMPUTER_PS
)
from core.config import config
from core.constants import ErrorMessages
from core.logger import logger

class RestorePointManager:
    @staticmethod
    def get_all_restore_points():
        all_points = []
        
        # OPTIMIZATION: Try WMI COM first (10x faster than PowerShell)
        try:
            import win32com.client
            # Connect to WMI
            wmi = win32com.client.GetObject("winmgmts:\\\\.\\root\\default")
            items = wmi.InstancesOf("SystemRestore")
            
            for item in items:
                try:
                    seq_num = item.SequenceNumber
                    desc = item.Description
                    raw_time = item.CreationTime # YYYYMMDDHHMMSS.uuuuuu+OOO
                    
                    # WMI Date Parsing
                    friendly_time = "Unknown Date"
                    dt_obj = datetime.min
                    if raw_time and len(raw_time) >= 14:
                        main_part = raw_time.split('.')[0]
                        dt_obj = datetime.strptime(main_part, "%Y%m%d%H%M%S")
                        friendly_time = dt_obj.strftime("%d.%m.%Y | %H:%M")
                    
                    all_points.append({
                        'id': seq_num,
                        'shadow_id': None, # Not available in basic SystemRestore class, needed only for VSS manual delete
                        'name': desc,
                        'timestamp': friendly_time,
                        'dt_obj': dt_obj
                    })
                except Exception as e:
                    logger.log_system(f"Error parsing WMI item: {e}")
                    continue
                
            # If we found items or verified connection worked (items could be empty)
            all_points.sort(key=lambda x: x['dt_obj'], reverse=True)
            return all_points
        except Exception as e:
            # Fallback to PowerShell if win32com missing or error
            logger.log_system(f"WMI COM failed, falling back to PowerShell: {e}")

        data = RestorePointManager._run_ps_json(GET_RESTORE_POINTS_PS)
        
        for item in data:
            try:
                seq_num = item.get('SequenceNumber')
                if seq_num is None: continue
                
                desc = item.get('Description', 'Unknown Point')
                shadow_id = item.get('ShadowID', '')
                raw_time = item.get('CreationTime', '') 
                
                friendly_time = "Unknown Date"
                dt_obj = datetime.min
                
                if raw_time and len(raw_time) >= 14:
                    try:
                        main_part = raw_time.split('.')[0]
                        dt_obj = datetime.strptime(main_part, "%Y%m%d%H%M%S")
                        friendly_time = dt_obj.strftime("%d.%m.%Y | %H:%M")
                    except Exception as e: 
                        logger.log_system(f"Error parsing date {raw_time}: {e}")

                all_points.append({
                    'id': seq_num,
                    'shadow_id': shadow_id,
                    'name': desc,
                    'timestamp': friendly_time,
                    'dt_obj': dt_obj
                })
            except Exception as item_error:
                logger.log_system(f"Error processing item: {item_error}")
                continue
        
        all_points.sort(key=lambda x: x['dt_obj'], reverse=True)
        return all_points

    @staticmethod
    def delete_restore_point(point_data):
        """
        Hybrid deletion: tries Native API (srclient), then ShadowID, then SequenceNumber via PS.
        """
        sid = point_data.get('shadow_id')
        seq = point_data.get('sequence_number')
        
        print(f"[SYSTEM] Attempting to delete point. ShadowID: {sid or 'None'}, Seq: {seq}")
        
        # Phase 0: Native API (Fastest) - srclient.dll
        if seq is not None:
            try:
                import ctypes
                # SRRemoveRestorePoint returns 0 (ERROR_SUCCESS) on success
                res = ctypes.windll.srclient.SRRemoveRestorePoint(int(seq))
                if res == 0:
                    return True, "Точка успешно удалена (Native API)"
            except Exception as e:
                logger.log_system(f"Native delete failed: {e}")

        # Phase 1: Try ShadowCopy (GUID) - Best for space retrieval
        if sid:
            cmd_shadow = DELETE_SHADOW_PS.format(sid=sid)
            res = RestorePointManager._run_ps_raw(cmd_shadow)
            if res['success']:
                return True, "Точка успешно удалена (VSS)"
        
        # Phase 2: Fallback to SequenceNumber (SystemRestore class via PowerShell)
        if seq is not None:
            print(f"[SYSTEM] Falling back to PowerShell deletion for: {seq}")
            cmd_sys = DELETE_SYSTEM_PS.format(seq=seq)
            
            res = RestorePointManager._run_ps_raw(cmd_sys)
            if res['success']:
                return True, "Точка удалена (SystemRestore)"
            else:
                err_msg = res['error'].lower()
                if "0x80041003" in err_msg or "access denied" in err_msg or "отказано в доступе" in err_msg:
                    return False, "Ошибка: Доступ запрещен. Запустите Vortex от имени Системы или проверьте антивирус."
                return False, f"Ошибка ОС: {res['error']}"

        return False, "Не удалось определить идентификаторы точки для удаления"

    @staticmethod
    def get_vss_storage_info():
        """
        Calculates total space used by shadow copies across all drives.
        """
        data = RestorePointManager._run_ps_json(GET_STORAGE_INFO_PS)
        
        total_bytes = 0
        drive_map = {}
        
        for item in data:
            try:
                used = int(item.get('Used', 0))
                total_bytes += used
                drv = item.get('Drive', '?') or '?'
                drive_map[drv] = drive_map.get(drv, 0) + used
            except Exception as e:
                logger.log_system(f"Error processing storage info item: {e}")
            
        total_gb = total_bytes / (1024**3)
        
        details = []
        # Sort by drive letter
        for drv in sorted(drive_map.keys()):
            gb = drive_map[drv] / (1024**3)
            details.append(f"{drv} {gb:.2f} GB")
            
        return {
            'total_gb': total_gb,
            'details': "\n".join(details) if details else "Нет данных"
        }

    @staticmethod
    def _run_ps_raw(cmd):
        full_cmd = f"powershell -NoProfile -ExecutionPolicy Bypass -Command \"{cmd}\""
        try:
            res = subprocess.run(full_cmd, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, text=True)
            if res.returncode == 0:
                return {'success': True, 'error': ''}
            else:
                return {'success': False, 'error': res.stderr.strip() or "Unknown PS Error"}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @staticmethod
    def _run_ps_json(cmd):
        full_cmd = f"powershell -NoProfile -ExecutionPolicy Bypass -Command \"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; {cmd}\""
        try:
            res = subprocess.run(full_cmd, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            raw = res.stdout.decode('utf-8', errors='ignore').strip()
            if not raw: return []
            try:
                data = json.loads(raw)
            except Exception as json_err: 
                logger.log_system(f"JSON Parse Error: {json_err}, Raw: {raw[:50]}...")
                return []
            if isinstance(data, dict): data = [data]
            return data
        except Exception as e:
            logger.log_system(f"PowerShell Execution Error: {e}")
            return []

    @staticmethod
    def generate_next_name():
        count = config.get('restore_count', 0)
        new_count = count + 1
        name = f"Vortex Restore Point #{new_count}"
        config.set('restore_count', new_count)
        return name

    @staticmethod
    def create_point_wmi(description):
        # Primary: win32com
        try:
            import win32com.client
            o = win32com.client.GetObject("winmgmts:\\\\.\\root\\default:SystemRestore")
            result = o.CreateRestorePoint(description, 12, 100) # 12=MODIFY_SETTINGS, 100=BEGIN_SYSTEM_CHANGE
            return result == 0
        except Exception as e:
            logger.log_system(f"WMI create failed: {e}. Trying PowerShell Fallback.")
            
            cmd = CHECKPOINT_COMPUTER_PS.format(description=description)
            res = RestorePointManager._run_ps_raw(cmd)
            if res['success']:
                return True
                
            return False
