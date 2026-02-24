
GET_RESTORE_POINTS_PS = """
$rps = Get-WmiObject -Namespace root\\default -Class SystemRestore;
$shadows = Get-WmiObject Win32_ShadowCopy;
$results = @();
foreach ($rp in $rps) {
  $best_sid = '';
  if ($rp.CreationTime) {
    try {
        $rt = [Management.ManagementDateTimeConverter]::ToDateTime($rp.CreationTime);
        $min = 120;
        foreach ($sh in $shadows) {
          try {
            $st = [Management.ManagementDateTimeConverter]::ToDateTime($sh.InstallDate);
            $diff = [Math]::Abs(($rt - $st).TotalSeconds);
            if ($diff -lt $min) { $min=$diff; $best_sid=$sh.ID }
          } catch {}
        }
    } catch {}
  }
  $results += @{
    SequenceNumber = $rp.SequenceNumber;
    Description = $rp.Description;
    CreationTime = $rp.CreationTime;
    ShadowID = $best_sid
  }
};
$results | ConvertTo-Json -Compress
"""

DELETE_SHADOW_PS = """
Get-WmiObject Win32_ShadowCopy | Where-Object {{ $_.ID -eq '{sid}' }} | ForEach-Object {{ $_.Delete() }}
"""

DELETE_SYSTEM_PS = """
Get-WmiObject -Namespace root\\default -Class SystemRestore | Where-Object {{ $_.SequenceNumber -eq {seq} }} | ForEach-Object {{ $_.Delete() }}
"""

GET_STORAGE_INFO_PS = """
$results = @();
$vols = Get-WmiObject Win32_Volume;
$shadows = Get-WmiObject Win32_ShadowStorage;
foreach ($sh in $shadows) {
  $v = $vols | Where-Object { $_.DeviceID -eq $sh.Volume.DeviceID };
  $dl = if ($v) { $v.DriveLetter } else { '?' };
  $results += @{ Drive=$dl; Used=$sh.UsedSpace }
};
$results | ConvertTo-Json -Compress
"""

CHECKPOINT_COMPUTER_PS = """
Checkpoint-Computer -Description "{description}" -RestorePointType "MODIFY_SETTINGS"
"""
