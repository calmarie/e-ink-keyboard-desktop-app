import serial
import time

try:
    ser = serial.Serial("COM5", 115200)
except Exception as e:
    print(f"Не удалось открыть порт: {e}")
    ser = None

time.sleep(2)  # подождать сброс ESP32


timeout = 2


def check_sent(start):
    while time.time() - start < timeout:
        if ser.in_waiting:
            resp = ser.read(1)

            if resp == b'\x06':
                print("ACK ✅")
                return True

            elif resp == b'\x15':
                print("NACK ❌")
                return False


    print("TIMEOUT")
    return False

def send_packet(query: dict):
    for key in query:

        # HEADER
        packet = bytearray([0xAA, 0x55])

        # TYPE: NEW  - 0xF* OR AGAIN 0x0*
        #      id  0x*0
        #      img 0x*1
        #      action 0x*2
        match key:
            case "id":
                packet.append(0xF0)
                data = query[key].to_bytes()
            case "img":
                packet.append(0xF1)
                data = bytes(query[key])
            case "action":
                packet.append(0xF2)
                data = query[key].encode('utf-8')

        # SIZE
        packet += len(data).to_bytes(4, 'little')


        # DATA
        packet += data

        # CHECKSUM
        checksum = sum(data) % 256
        packet.append(checksum)

        # отправка
        ser.reset_input_buffer()
        ser.write(packet)
        ser.flush()
        time.sleep(0.1)


        start = time.time()
        if check_sent(start):
            continue
        else:
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
                break
            continue

