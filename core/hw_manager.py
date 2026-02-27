import subprocess

class HardwareManager:
    _cpu_name = None
    _gpu_names = None

    @classmethod
    def get_cpu_name(cls) -> str:
        if cls._cpu_name is None:
            try:
                out = subprocess.check_output(["wmic", "cpu", "get", "name"], creationflags=subprocess.CREATE_NO_WINDOW).decode('utf-8', errors='ignore')
                lines = [line.strip() for line in out.splitlines() if line.strip()]
                if len(lines) > 1:
                    cls._cpu_name = lines[1]
                else:
                    cls._cpu_name = "Unknown"
            except Exception:
                cls._cpu_name = "Unknown"
        return cls._cpu_name

    @classmethod
    def get_gpu_names(cls) -> list[str]:
        if cls._gpu_names is None:
            cls._gpu_names = []
            try:
                out = subprocess.check_output(["wmic", "path", "win32_videocontroller", "get", "name"], creationflags=subprocess.CREATE_NO_WINDOW).decode('utf-8', errors='ignore')
                lines = [line.strip() for line in out.splitlines() if line.strip()]
                if len(lines) > 1:
                    cls._gpu_names = lines[1:]
            except Exception:
                pass
        return cls._gpu_names

    @classmethod
    def is_nvidia(cls) -> bool:
        return any("nvidia" in g.lower() for g in cls.get_gpu_names())

    @classmethod
    def is_amd_gpu(cls) -> bool:
        return any("amd" in g.lower() or "radeon" in g.lower() for g in cls.get_gpu_names())

    @classmethod
    def is_amd_cpu(cls) -> bool:
        return "amd" in cls.get_cpu_name().lower() or "ryzen" in cls.get_cpu_name().lower()

    @classmethod
    def is_intel_cpu(cls) -> bool:
        return "intel" in cls.get_cpu_name().lower()

    @classmethod
    def is_supported(cls, tags: list[str]) -> bool:
        if not tags:
            return True
        matched = False
        for tag in tags:
            t = tag.upper()
            if t == "NVIDIA" and cls.is_nvidia(): matched = True
            elif t == "AMD_GPU" and cls.is_amd_gpu(): matched = True
            elif t == "AMD_CPU" and cls.is_amd_cpu(): matched = True
            elif t == "INTEL_CPU" and cls.is_intel_cpu(): matched = True
        return matched
