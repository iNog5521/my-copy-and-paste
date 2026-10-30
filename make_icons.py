"""Gera os ícones PNG do app (somente biblioteca padrão). Uso: python3 make_icons.py"""
import zlib, struct, os

def rrect(px, py, cx, cy, hw, hh, r):
    qx, qy = abs(px - cx) - (hw - r), abs(py - cy) - (hh - r)
    ox, oy = max(qx, 0), max(qy, 0)
    return (ox * ox + oy * oy) ** 0.5 + min(max(qx, qy), 0) - r

def cov(d, aa):  # distância assinada -> cobertura 0..1
    return min(1, max(0, 0.5 - d / aa))

def mix(a, b, t):
    return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))

def render(n):
    aa = max(1.0, n / 256)
    rows = []
    for y in range(n):
        row = bytearray([0])
        for x in range(n):
            u, v = x / n, y / n
            col = mix((99, 102, 241), (168, 85, 247), (u + v) / 2)  # gradiente índigo -> violeta
            # folha de trás (cópia)
            c = cov(rrect(u * n, v * n, .40 * n, .40 * n, .20 * n, .24 * n, .055 * n), aa)
            col = mix(col, (255, 255, 255), c * .55)
            # folha da frente (com borda na cor do fundo para separar)
            c = cov(rrect(u * n, v * n, .58 * n, .58 * n, .215 * n, .255 * n, .06 * n), aa)
            col = mix(col, (255, 255, 255), c)
            # linhas de texto
            for i, w in enumerate((.13, .13, .08)):
                cy = (.50 + i * .09) * n
                c = cov(rrect(u * n, v * n, (.43 + w) * n, cy, w * n, .017 * n, .017 * n), aa)
                col = mix(col, (129, 100, 245), c)
            row += bytes(int(round(k)) for k in col) + b'\xff'
        rows.append(bytes(row))
    raw = b''.join(rows)
    def chunk(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', n, n, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))

os.makedirs('icons', exist_ok=True)
for name, size in (('icon-180.png', 180), ('icon-192.png', 192), ('icon-512.png', 512)):
    with open(os.path.join('icons', name), 'wb') as f:
        f.write(render(size))
    print('ok', name)
