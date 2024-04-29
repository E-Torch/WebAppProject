import hashlib, base64


class SocketFrame:
    def __init__(self, f, o, p_len, p, e):
        self.fin_bit = f
        self.opcode = o
        self.payload_length = p_len
        self.payload = p
        self.extra = e


def compute_accept(key: str):
    appendK = key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    sha1 = hashlib.sha1()
    sha1.update(appendK.encode())
    return base64.b64encode(sha1.digest()).decode("utf-8")


def parse_ws_frame(frame: bytes):
    fin_mask = 0x80
    opcode_mask = 0x0F
    payload_len_7bit = 0x7F

    finbit = (fin_mask & frame[0]) >> 7
    opcode = opcode_mask & frame[0]
    payload_len, payload_start = get_payload_len(frame, 0x7F & frame[1])
    payload, extra = _get_payload(frame, fin_mask, payload_start, payload_len)
    return SocketFrame(finbit, opcode, payload_len, payload, extra)


def get_payload_len(frame, payload_len):
    payload_start = 2
    if payload_len == 0x7E:
        payload_start += 2
        payload_len = _get_extended(frame, payload_start)
    elif payload_len == 0x7F:
        payload_start += 8
        payload_len = _get_extended(frame, payload_start)

    return [payload_len, payload_start]


def _get_payload(frame, fin_mask, payload_start, payload_len):
    mask = (fin_mask & frame[1]) >> 7
    mask_result = b""
    extra = None
    if mask:
        mask_info = frame[payload_start : payload_start + 4]
        payload_start += 4
        payload = frame[payload_start : payload_start + payload_len]
        p_index = 0
        while p_index < len(payload):
            for i in range(4):
                if i + p_index >= len(payload):
                    break
                m = payload[i + p_index] ^ mask_info[i]
                mask_result += m.to_bytes(1, "big")

            p_index += 4

        return [mask_result, frame[payload_start + payload_len :]]

    return [
        frame[payload_start : payload_start + payload_len],
        frame[payload_start + payload_len :],
    ]


def _get_extended(frame, end):
    data = frame[2:end]
    return _create_int_from_byte(data)


def _create_int_from_byte(byte_len):
    return int.from_bytes(byte_len, "big")


def generate_ws_frame(payload: bytes):
    payload_len = len(payload)
    if payload_len < 126:
        payload_len = payload_len.to_bytes(1, "big")
    elif payload_len < 65536:
        payload_len = b"\x7e" + payload_len.to_bytes(2, "big")
    else:
        payload_len = b"\x7f" + payload_len.to_bytes(8, "big")

    return b"\x81" + payload_len + payload


if __name__ == "__main__":
    res = compute_accept("x6BweGU0VvnAoNDZAvk9nw==")
    assert res == "YeRsVEUiNewITV9hNUolbpQg12w="
    frame = b"\x81\x86\x1A\x2B\x3C\x4D\x52\x4e\x50\x21\x75\x0a"
    ws = parse_ws_frame(frame)
    assert ws.fin_bit == 1
    assert ws.opcode == 1
    assert ws.payload_length == 6
    assert ws.payload == b"Hello!"

    frame = b"\x81\x06Hello!"
    ws = parse_ws_frame(frame)
    assert ws.fin_bit == 1
    assert ws.opcode == 1
    assert ws.payload_length == 6
    assert ws.payload == b"Hello!"
