import time

import serial
from serial.tools import list_ports


BAUDRATE = 115200
timeout = 2
ser = None

PORT_HINTS = (
    "esp",
    "wch",
    "ch9102",
    "ch340",
    "cp210",
    "usb serial",
    "usb-enhanced-serial",
)


def _port_score(port_info) -> tuple[int, int]:
    haystack = " ".join(
        str(value).lower()
        for value in (
            port_info.device,
            port_info.description,
            getattr(port_info, "manufacturer", ""),
            getattr(port_info, "product", ""),
            getattr(port_info, "hwid", ""),
        )
        if value
    )
    hint_matches = sum(1 for hint in PORT_HINTS if hint in haystack)
    has_usb_ids = int(port_info.vid is not None and port_info.pid is not None)
    return hint_matches, has_usb_ids


def find_esp_port() -> str | None:
    ports = list(list_ports.comports())
    if not ports:
        return None

    sorted_ports = sorted(ports, key=_port_score, reverse=True)
    best_port = sorted_ports[0]
    if _port_score(best_port) == (0, 0):
        return None
    return best_port.device


def ensure_connection() -> bool:
    global ser

    if ser is not None and ser.is_open:
        return True

    port_name = find_esp_port()
    if port_name is None:
        print("Не удалось автоматически найти ESP/USB COM-порт.")
        ser = None
        return False

    try:
        ser = serial.Serial(port_name, BAUDRATE)
        time.sleep(2)  # дать ESP время перезагрузиться после открытия порта
        print(f"Подключено к {port_name}")
        return True
    except Exception as exc:
        print(f"Не удалось открыть порт {port_name}: {exc}")
        ser = None
        return False


def check_sent(start):
    if ser is None:
        return False

    while time.time() - start < timeout:
        if ser.in_waiting:
            resp = ser.read(1)

            if resp == b"\x06":
                print("ACK")
                return True

            if resp == b"\x15":
                print("NACK")
                return False

    print("TIMEOUT")
    return False


def send_packet(query: dict):
    if not ensure_connection():
        return False

    for key in query:
        packet = bytearray([0xAA, 0x55])

        match key:
            case "id":
                packet.append(0xF0)
                data = query[key].to_bytes()
            case "img":
                packet.append(0xF1)
                data = bytes(query[key])
            case "action":
                packet.append(0xF2)
                if isinstance(query[key], str):
                    data = query[key].encode("utf-8")
                else:
                    data = bytes(query[key])
            case _:
                continue

        packet += len(data).to_bytes(4, "little")
        packet += data
        checksum = sum(data) % 256
        packet.append(checksum)

        ser.reset_input_buffer()
        ser.write(packet)
        ser.flush()
        time.sleep(0.1)

        start = time.time()
        if check_sent(start):
            continue

        retries = 0
        max_retries = 5
        match key:
            case "id":
                packet[2] = 0x00
            case "img":
                packet[2] = 0x01
            case "action":
                packet[2] = 0x02

        while retries < max_retries:
            ser.write(packet)
            ser.flush()
            time.sleep(0.1)

            start = time.time()
            if check_sent(start):
                break

            print("Retry...")
            retries += 1

        if retries == max_retries:
            print("FAILED to send chunk")
            return False

    return True
