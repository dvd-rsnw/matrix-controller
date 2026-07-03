import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "detect_hardware.py"

spec = importlib.util.spec_from_file_location("detect_hardware", SCRIPT)
assert spec and spec.loader
detect_hardware = importlib.util.module_from_spec(spec)
spec.loader.exec_module(detect_hardware)


def fake_pi(tmp_path: Path, model: str, cmdline: str = "console=tty1") -> Path:
    (tmp_path / "proc/device-tree").mkdir(parents=True)
    (tmp_path / "proc/device-tree/model").write_bytes(model.encode() + b"\x00")
    (tmp_path / "proc/cpuinfo").write_text("processor\t: 0\nRevision\t: 902120\n")
    (tmp_path / "proc/meminfo").write_text("MemTotal:         442372 kB\n")
    (tmp_path / "proc/cmdline").write_text(cmdline + "\n")
    gov = tmp_path / "sys/devices/system/cpu/cpu0/cpufreq"
    gov.mkdir(parents=True)
    (gov / "scaling_governor").write_text("ondemand\n")
    return tmp_path


def test_detect_on_fake_pi_zero_2w(tmp_path: Path) -> None:
    root = fake_pi(tmp_path, "Raspberry Pi Zero 2 W Rev 1.0")
    info = detect_hardware.detect(root)
    assert info["model"] == "Raspberry Pi Zero 2 W Rev 1.0"
    assert info["revision"] == "902120"
    assert info["mem_mb"] == 432
    assert info["isolcpus"] is None
    assert info["governor"] == "ondemand"
    assert info["recommended_profile"] == "pi-zero-2w"


def test_detect_isolcpus_flag(tmp_path: Path) -> None:
    root = fake_pi(tmp_path, "Raspberry Pi 4 Model B Rev 1.4", cmdline="isolcpus=3 console=tty1")
    info = detect_hardware.detect(root)
    assert info["isolcpus"] == "3"
    assert info["recommended_profile"] == "pi-4"


def test_detect_pi5_warns(tmp_path: Path) -> None:
    root = fake_pi(tmp_path, "Raspberry Pi 5 Model B Rev 1.0")
    info = detect_hardware.detect(root)
    assert any("not supported" in note for note in info["notes"])


def test_detect_off_pi_degrades(tmp_path: Path) -> None:
    (tmp_path / "proc").mkdir()
    info = detect_hardware.detect(tmp_path)
    assert info["model"] is None
    assert info["recommended_profile"] == "pi-3"
    assert json.dumps(info)  # must be JSON-serializable
