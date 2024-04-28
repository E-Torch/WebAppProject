import hashlib, base64


class SocketFrame:
    def __init__(self, f, o, p_len, p):
        self.fin_bit = f
        self.opcode = o
        self.payload_length = p_len
        self.payload = p


def compute_accept(key: str):
    appendK = key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    sha1 = hashlib.sha1()
    sha1.update(appendK.encode())
    return base64.b64encode(sha1.digest()).decode("utf-8")


def parse_ws_frame(frame: bytes):
    fin_mask = 0x80
    opcode_mask = 0x0F
    payload_len_7bit = 0x7F

    finbit = fin_mask & frame[0]
    opcode = opcode_mask & frame[0]
    payload_len, payload_start = _get_payload_len(frame, payload_len_7bit & frame[1])
    payload = _get_payload(frame, fin_mask, payload_start)
    return SocketFrame(finbit, opcode, payload_len, payload)


def _get_payload_len(frame, payload_len):
    payload_start = 2
    if payload_len == 0x7E:
        payload_start += 2
        payload_len = _get_extended(frame, payload_start)
    elif payload_len == 0x7F:
        payload_start += 8
        payload_len = _get_extended(frame, payload_start)

    return [payload_len, payload_start]


def _get_payload(frame, fin_mask, payload_start):
    mask = fin_mask & frame[1]
    mask_result = b""
    if mask:
        mask_info = frame[payload_start : payload_start + 4]
        payload_start += 4
        payload = frame[payload_start:]
        p_index = 0
        while p_index < len(payload):
            for i in range(4):
                if i + p_index >= len(payload):
                    break
                mask_result += payload[i + p_index] ^ frame[i]
            p_index += 4
        return mask_result

    return frame[payload_start:]


def _get_extended(frame, end):
    data = frame[1:end]
    return _create_int_from_byte(data)


def _create_int_from_byte(byte_len):
    return int.from_bytes(byte_len, "big")


def generate_ws_frame(payload: bytes):
    return b""


if __name__ == "__main__":
    res = compute_accept("x6BweGU0VvnAoNDZAvk9nw==")
    assert res == "YeRsVEUiNewITV9hNUolbpQg12w="
