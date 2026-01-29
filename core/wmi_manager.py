class RestorePointManager:
    @staticmethod
    def get_all_restore_points():
        import subprocess
        import json
        from datetime import datetime
        
        # We need both SequenceNumber (Official) and ShadowID (VSS)
        # We'll use a more direct WMI query to avoid complex correlation if possible,
        # but correlation is needed for ShadowID.
        ps_script = (
            "$rps = Get-WmiObject -Namespace root\\default -Class SystemRestore; "
            "$shadows = Get-WmiObject Win32_ShadowCopy; "
            "$results = @(); "
            "foreach ($rp in $rps) { "
            "  $best_sid = ''; "
            "  if ($rp.CreationTime) { "
            "    $rt = [Management.ManagementDateTimeConverter]::ToDateTime($rp.CreationTime); "
            "    $min = 120; "
            "    foreach ($sh in $shadows) { "
            "      try { "
            "        $st = [Management.ManagementDateTimeConverter]::ToDateTime($sh.InstallDate); "
            "        $diff = [Math]::Abs(($rt - $st).TotalSeconds); "
            "        if ($diff -lt $min) { $min=$diff; $best_sid=$sh.ID } "
            "      } catch {} "
            "    } "
            "  } "
            "  $results += @{ "
            "    SequenceNumber = $rp.SequenceNumber; "
            "    Description = $rp.Description; "
            "    CreationTime = $rp.CreationTime; "
            "    ShadowID = $best_sid "
            "  } "
            "}; "
            "$results | ConvertTo-Json -Compress"
        )
        
        all_points = []
        data = RestorePointManager._run_ps_json(ps_script)
        
        for item in data:
            try:
                seq_num = item.get('SequenceNumber')
                if seq_num is None: continue
                
                desc = item.get('Description', 'Unknown Point')
                shadow_id = item.get('ShadowID', '')
                raw_time = item.get('CreationTime', '') # e.g. 20260124162444.000000-000
                
                # Parse WMI Date (YYYYMMDDHHMMSS...)
                friendly_time = "Unknown Date"
                dt_obj = datetime.min
                
                if raw_time and len(raw_time) >= 14:
                    try:
                        # Extract YYYY MM DD HH MM SS
                        y = int(raw_time[0:4])
                        m = int(raw_time[4:6])
                        d = int(raw_time[6:8])
                        hh = int(raw_time[8:10])
                        mm = int(raw_time[10:12])
                        ss = int(raw_time[12:14])
                        dt_obj = datetime(y, m, d, hh, mm, ss)
                        friendly_time = dt_obj.strftime("%d.%m.%Y | %H:%M")
                    except: pass

                all_points.append({
                    'id': seq_num,
                    'shadow_id': shadow_id,
                    'name': desc,
                    'timestamp': friendly_time,
                    'dt_obj': dt_obj
                })
            except:
                continue
        
        # FORCE SORT: Newest first
        all_points.sort(key=lambda x: x['dt_obj'], reverse=True)
        return all_points

    @staticmethod
    def delete_restore_point(point_data):
        """
        Hybrid deletion: tries ShadowID first, then SequenceNumber.
        point_data should be a dict with 'shadow_id' and 'sequence_number'.
        """
        sid = point_data.get('shadow_id')
        seq = point_data.get('sequence_number')
        
        print(f"[SYSTEM] Attempting to delete point. ShadowID: {sid or 'None'}, Seq: {seq}")
        
        # Phase 1: Try ShadowCopy (GUID) - Best for space retrieval
        if sid:
            cmd_shadow = f"Get-WmiObject Win32_ShadowCopy | Where-Object {{ $_.ID -eq '{sid}' }} | ForEach-Object {{ $_.Delete() }}"
            res = RestorePointManager._run_ps_raw(cmd_shadow)
            if res['success']:
                return True, "Точка успешно удалена (VSS)"
        
        # Phase 2: Fallback to SequenceNumber (SystemRestore class)
        if seq is not None:
            print(f"[SYSTEM] Falling back to SequenceNumber deletion for: {seq}")
            cmd_sys = f"Get-WmiObject -Namespace root\\default -Class SystemRestore | Where-Object {{ $_.SequenceNumber -eq {seq} }} | ForEach-Object {{ $_.Delete() }}"
            res = RestorePointManager._run_ps_raw(cmd_sys)
            if res['success']:
                return True, "Точка удалена (SystemRestore)"
            else:
                err_msg = res['error'].lower()
                if "access denied" in err_msg or "0x80041003" in err_msg:
                    return False, "Ошибка: Доступ запрещен. Запустите Vortex от имени Системы или проверьте антивирус."
                return False, f"Ошибка ОС: {res['error']}"

        return False, "Не удалось определить идентификаторы точки для удаления"

    @staticmethod
    def get_vss_storage_info():
        """
        Calculates total space used by shadow copies across all drives.
        """
        # We'll use Get-WmiObject Win32_ShadowStorage as it's cleaner for JSON parsing
        # Mapping Volume DeviceID to Drive Letter for details
        script = (
            "$results = @(); "
            "$vols = Get-WmiObject Win32_Volume; "
            "$shadows = Get-WmiObject Win32_ShadowStorage; "
            "foreach ($sh in $shadows) { "
            "  $v = $vols | Where-Object { $_.DeviceID -eq $sh.Volume.DeviceID }; "
            "  $dl = if ($v) { $v.DriveLetter } else { '?' }; "
            "  $results += @{ Drive=$dl; Used=$sh.UsedSpace } "
            "}; "
            "$results | ConvertTo-Json -Compress"
        )
        
        data = RestorePointManager._run_ps_json(script)
        
        total_bytes = 0
        drive_map = {}
        
        for item in data:
            try:
                used = int(item.get('Used', 0))
                total_bytes += used
                drv = item.get('Drive', '?') or '?'
                drive_map[drv] = drive_map.get(drv, 0) + used
            except: pass
            
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
        import subprocess
        full_cmd = f"powershell -NoProfile -Command \"{cmd}\""
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
        import json
        import subprocess
        full_cmd = f"powershell -NoProfile -Command \"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; {cmd}\""
        try:
            res = subprocess.run(full_cmd, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            raw = res.stdout.decode('utf-8', errors='ignore').strip()
            if not raw: return []
            try:
                data = json.loads(raw)
            except: 
                # Recovery for partial/bad JSON
                return []
            if isinstance(data, dict): data = [data]
            return data
        except: return []

    @staticmethod
    def generate_next_name():
        points = RestorePointManager.get_all_restore_points()
        return f"Vortex Restore Point #{len(points) + 1}"

    @staticmethod
    def create_point_wmi(description):
        import win32com.client
        try:
            o = win32com.client.GetObject("winmgmts:\\\\.\\root\\default:SystemRestore")
            return o.CreateRestorePoint(description, 12, 100) == 0
        except: return False
