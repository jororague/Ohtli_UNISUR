"""Pruebas automatizadas de interfaz del prototipo OHTLI (P4).

Ejecuta en un navegador real (Chrome sin pantalla, Playwright) los pasos del
Protocolo de pruebas v1.0 que se pueden automatizar, guarda capturas y un
registro JSON con el resultado observado de cada prueba.

Uso:  python3 e2e_ohtli.py RUTA_AL_PROTOTIPO.html CARPETA_DE_SALIDA ETIQUETA
Cada bloque abre un contexto nuevo del navegador (almacenamiento vacío), lo que
equivale a «Restablecer datos sintéticos».
"""
import json, sys, datetime, pathlib, re
from playwright.sync_api import sync_playwright

PROTO = pathlib.Path(sys.argv[1]).resolve()
OUT = pathlib.Path(sys.argv[2]); OUT.mkdir(parents=True, exist_ok=True)
ETIQ = sys.argv[3] if len(sys.argv) > 3 else 'v0.1'
SHOTS = OUT / 'capturas'; SHOTS.mkdir(exist_ok=True)
URL = PROTO.as_uri()
R = []  # resultados


def reg(id_, observado, ok, capturas, parcial=False):
    R.append({'id': id_, 'observado': observado, 'resultado': 'Parcial' if (ok and parcial) else ('Pasa' if ok else 'Falla'), 'capturas': capturas})
    print(f"{id_:6} {R[-1]['resultado']:8} {observado[:110]}")


class UI:
    def __init__(self, page): self.p = page
    def shot(self, name, full=True):
        self.p.screenshot(path=str(SHOTS / name), full_page=full); return name
    def login(self, uid):
        if self.p.locator('[data-a=salir]').count(): self.p.click('[data-a=salir]')
        self.p.click(f'[data-login="{uid}"]')
    def nav(self, v): self.p.click(f'nav [data-v="{v}"]')
    def flash(self):
        f = self.p.locator('.flash'); return f.inner_text().strip() if f.count() else ''
    def folio(self, f): self.p.locator(f'[data-folio="{f}"]').first.click()
    def hist(self):
        rows = self.p.locator('main > table').last.locator('tbody tr')
        out = []
        for i in range(rows.count()):
            c = [x.strip() for x in rows.nth(i).locator('td').all_inner_texts()]
            out.append(c)  # fecha, origen, destino, usuario, observación, fuente
        return out
    def estado(self): return self.p.locator('.head .st').first.inner_text().strip()
    def text(self): return self.p.locator('main').inner_text()
    def tr(self, destino, obs=None, motivo=None):
        if obs is not None and self.p.locator('#fobs').count(): self.p.fill('#fobs', obs)
        if motivo is not None and self.p.locator('#fmot').count(): self.p.fill('#fmot', motivo)
        self.p.locator(f'[data-tr="{destino}"]').click()
    def solicitar(self, destino):
        self.p.locator('details summary').last.click()
        self.p.select_option('#fdest', destino); self.p.click('[data-a=trlibre]')


def nuevo(browser, **kw):
    ctx = browser.new_context(locale='es-MX', **kw)
    page = ctx.new_page(); page.goto(URL); page.wait_for_selector('[data-login]')
    return ctx, page, UI(page)


def bloque_A(b):
    ctx, page, u = nuevo(b, viewport={'width': 1280, 'height': 900})
    esperado = {'T01': (40, '6 + 3', 5, {'Atendida': 1, 'Cerrada': 1, 'En atención': 1, 'No asistió': 1, 'Recibida': 1}, 1),
                'T02': (40, '6 + 3', 5, {'Atendida': 1, 'Escalada': 1, 'No asistió': 1, 'Recibida': 1, 'Registrada': 1}, 1),
                'T03': (40, '6 + 3', 5, {'Cerrada': 1, 'En atención': 1, 'Escalada': 1, 'Recibida': 1, 'Registrada': 1}, 2)}
    obs, ok, caps = [], True, []
    for t, e in esperado.items():
        u.login(t); u.nav('informe'); page.fill('#icorte', '2026-11-18'); page.click('[data-a=corte]')
        big = page.locator('.panel .big').all_inner_texts()
        pe = {}
        for row in page.locator('.panel table').first.locator('tr').all():
            c = row.locator('td').all_inner_texts(); pe[c[0].strip()] = int(c[1])
        al = int(re.search(r'segundo incremento\): (\d+)', u.text().replace('2.º incremento', 'segundo incremento')).group(1))
        got = (int(big[0]), big[1].strip(), int(big[2]), pe, al)
        ok &= got == e
        obs.append(f"{t}: {got[0]} tutorados; {got[1]} sesiones; {got[2]} canalizaciones; por estado {', '.join(f'{k} {v}' for k, v in sorted(pe.items()))}; alertas {al}")
        caps.append(u.shot(f'A-01_{t}.png'))
    reg('A-01', ' | '.join(obs), ok, caps)

    u.login('COORD'); u.nav('alertas'); page.click('[data-a=alertas]')
    fol = [x.strip() for x in page.locator('main table tbody tr td:first-child').all_inner_texts()]
    reg('A-02', f"{len(fol)} alertas: {', '.join(fol)}. CAN-2026-0008 {'aparece' if 'CAN-2026-0008' in fol else 'no aparece'}.",
        fol == ['CAN-2026-0005', 'CAN-2026-0006', 'CAN-2026-0013', 'CAN-2026-0014'], [u.shot('A-02_alertas.png')])

    esp = [4, 3, 5, 3, 2, 1, 2, 2, 4, 3, 5, 3, 2, 1, 2]
    cont, ok, caps, defectos = [], True, [], []
    for i in range(15):
        f = f'CAN-2026-{i+1:04d}'; u.nav('folios'); u.folio(f)
        h = u.hist(); cont.append(len(h))
        prev = '—'
        for c in h:
            if not c[0] or not c[3]: defectos.append(f'{f}: fila sin usuario o fecha')
            if c[1] != prev: defectos.append(f'{f}: hueco {prev}→{c[1]}')
            prev = c[2]
        if i in (0, 6, 12): caps.append(u.shot(f'A-03_{f[-4:]}.png'))
    ok = cont == esp and not defectos
    reg('A-03', f"Total {sum(cont)} cambios; por folio {', '.join(f'{i+1:04d}:{n}' for i, n in enumerate(cont))}. {'Todas las filas con usuario y fecha; sin huecos.' if not defectos else '; '.join(defectos)}", ok, caps)

    u.nav('folios')
    heads = [x.strip() for x in page.locator('main table thead th').all_inner_texts()]
    caps = [u.shot('A-04_coord_lista.png')]
    fuga = []
    for cuenta, vista in (('COORD', 'folios'), ('JEF_CARRERA', 'jef')):
        u.login(cuenta)
        for f, nc in (('CAN-2026-0001', 'SIN261023'), ('CAN-2026-0013', 'SIN263002')):
            u.nav(vista); u.folio(f); tx = u.text()
            if nc in tx or 'Descripción sintética' in tx or 'Número de control' in tx: fuga.append(f'{cuenta} {f}')
            if 'Detalle confidencial' not in tx: fuga.append(f'{cuenta} {f} sin aviso')
        caps.append(u.shot(f"A-04_{cuenta.lower()}_folio.png"))
    reg('A-04', f"Columnas de COORD: {', '.join(heads)}. {'Ni COORD ni JEF_CARRERA ven número de control, motivo ni descripción; aparece el aviso de detalle confidencial.' if not fuga else 'Fugas: ' + '; '.join(fuga)}",
        not fuga and 'Número de control' not in heads, caps)

    mat, ok, caps = [], True, []
    esperado_menu = {'tutor': ['Tutorados', 'Sesiones', 'Canalizaciones', 'Informe', 'Notificaciones'], 'APOYO-PSI': ['Bandeja'], 'APOYO-DA': ['Bandeja'],
                     'JEF_CARRERA': ['Canalizaciones'], 'COORD': ['Estado por folio', 'Alertas', 'Tablero'], 'ADMIN': ['Bitácora', 'Catálogos', 'Yolia']}
    for cuenta in ['T01', 'T02', 'T03', 'APOYO-PSI', 'APOYO-DA', 'JEF_CARRERA', 'COORD', 'ADMIN']:
        u.login(cuenta)
        menu = [x.split(' (')[0].strip() for x in page.locator('nav button').all_inner_texts()]
        em = esperado_menu['tutor' if cuenta.startswith('T0') else cuenta]
        if cuenta.startswith('T0'):
            nt = page.locator('main table tbody tr').count(); u.nav('canal')
            fs = [x.strip() for x in page.locator('main table tbody tr td:first-child').all_inner_texts()]
            alc = f'{nt} tutorados; folios {fs[0][-4:]}–{fs[-1][-4:]}'; base = {'T01': 1, 'T02': 6, 'T03': 11}[cuenta]
            ok_a = nt == 40 and fs == [f'CAN-2026-{base+k:04d}' for k in range(5)]
        elif cuenta.startswith('APOYO'):
            page.click('[data-band="todas"]'); todas = page.locator('.card').count()
            page.click('[data-band=""]'); ab = page.locator('.card').count()
            alc = f'{todas} folios en «Todas», {ab} en «Abiertas»'; ok_a = (todas, ab) == ((9, 9) if cuenta == 'APOYO-PSI' else (6, 4))
        elif cuenta in ('JEF_CARRERA', 'COORD'):
            n = page.locator('main table tbody tr').count(); alc = f'{n} folios'; ok_a = n == 15
        else:
            alc = 'sin vistas de tutorados ni folios'; ok_a = not any(m in menu for m in ['Tutorados', 'Canalizaciones', 'Bandeja', 'Estado por folio'])
        ok &= menu == em and ok_a
        mat.append({'cuenta': cuenta, 'menu': ', '.join(menu), 'alcance': alc, 'coincide': 'Sí' if (menu == em and ok_a) else 'No'})
        caps.append(u.shot(f'A-05_{cuenta}.png', full=False))
    json.dump(mat, open(OUT / 'A-05_matriz.json', 'w'), ensure_ascii=False, indent=1)
    reg('A-05', ' | '.join(f"{m['cuenta']}: {m['menu']}; {m['alcance']}" for m in mat), ok, caps)

    bad, n = [], 0
    for t in ['T01', 'T02', 'T03']:
        u.login(t); ncs = [x.strip() for x in page.locator('main table tbody tr td:first-child').all_inner_texts()]
        n += len(ncs); bad += [x for x in ncs if not x.startswith('SIN')]
    aviso = 'sintéticos' in page.locator('.note').inner_text()
    reg('A-06', f'{n} números de control revisados; {len(bad)} sin prefijo SIN. Aviso de datos sintéticos visible en la franja: {"sí" if aviso else "no"}.', n == 120 and not bad and aviso, [u.shot('A-06_aviso.png', full=False)])
    ctx.close()


def bloque_B(b):
    ctx, page, u = nuevo(b, viewport={'width': 1280, 'height': 900})
    u.login('T01'); nt = page.locator('main table tbody tr').count(); c1 = u.shot('B-01_lista.png', full=False)
    u.nav('canal'); page.click('[data-nueva=""]')
    page.fill('#cnc', 'SIN262001'); page.select_option('#cmot', 'conducta'); page.select_option('#cins', 'Psicología')
    page.select_option('#cpri', 'normal'); page.select_option('#cinf', 'si'); page.fill('#cdes', 'Prueba B-01')
    page.click('[data-a=canalizar]'); fl = u.flash(); c2 = u.shot('B-01_rechazo.png', full=False)
    nfol = None; u.nav('canal'); nfol = page.locator('main table tbody tr').count()
    u.login('ADMIN'); bt = u.text(); c3 = u.shot('B-01_bitacora.png', full=False)
    ok = nt == 40 and 'RN-03' in fl and nfol == 5 and 'Intento denegado de canalización' in bt and 'T01' in bt
    reg('B-01', f'T01 ve {nt} tutorados. Mensaje: «{fl}». Folios de T01 después del intento: {nfol}. Bitácora con «Intento denegado de canalización» de T01: {"sí" if "Intento denegado de canalización" in bt else "no"}.', ok, [c1, c2, c3])

    u.login('T01'); u.nav('canal'); page.click('[data-nueva=""]')
    page.fill('#cnc', 'SIN261001'); page.select_option('#cmot', 'bajo rendimiento'); page.select_option('#cpri', 'normal'); page.select_option('#cinf', 'si'); page.fill('#cdes', 'Prueba B-02')
    page.click('[data-a=canalizar]'); f1 = u.flash(); c1 = u.shot('B-02_1.png', full=False)
    page.select_option('#cins', 'Psicología'); page.select_option('#cinf', ''); page.click('[data-a=canalizar]'); f2 = u.flash(); c2 = u.shot('B-02_2.png', full=False)
    page.select_option('#cinf', 'si'); page.fill('#cdes', 'x' * 520); cont = page.locator('#ccount').inner_text()
    page.click('[data-a=canalizar]'); f3 = u.flash(); c3 = u.shot('B-02_3.png', full=False)
    form_tx = page.locator('main').inner_text().lower(); diag_campo = page.locator('label', has_text='iagnóstico').count()
    aviso = 'minimización' in form_tx
    page.fill('#cdes', 'Prueba B-02'); page.click('[data-a=canalizar]'); f4 = u.flash()
    h = u.hist(); est = u.estado(); c4 = u.shot('B-02_4.png', full=False)
    ok = 'instancia' in f1 and 'informado' in f2 and '500' in f3 and 'CAN-2026-0016' in f4 and est == 'Registrada' and len(h) == 1 and h[0][3] == 'T01' and diag_campo == 0 and aviso
    reg('B-02', f'Paso 1: «{f1}» Paso 2: «{f2}» Paso 3: «{f3}» (contador {cont}). Paso 4: «{f4}»; estado {est}; historial {len(h)} fila, usuario {h[0][3]}, fecha {h[0][0]}. Campos de diagnóstico: {diag_campo}; aviso de minimización: {"sí" if aviso else "no"}.', ok, [c1, c2, c3, c4])

    u.nav('tutorados'); page.locator('[data-exp="SIN261001"]').first.click()
    page.fill('#ntexto', 'Prueba B-03'); page.click('[data-a=nota]'); f1 = u.flash(); c1 = u.shot('B-03_1.png', full=False)
    page.select_option('#eje', 'académico'); page.fill('#ntexto', 'Prueba B-03'); page.click('[data-a=nota]'); f2 = u.flash()
    nota = page.locator('.zone').first.inner_text(); c2 = u.shot('B-03_2.png', full=False)
    reg('B-03', f'Paso 1: «{f1}» Paso 2: «{f2}»; nota mostrada: «{" ".join(nota.split())}».', 'eje' in f1 and f2 == 'Nota guardada.' and 'académico' in nota and 'T01' in nota, [c1, c2])

    u.nav('sesiones'); page.select_option('#stipo', 'individual'); page.fill('#stema', 'Prueba B-04')
    page.locator('[name=asis]').first.check(); page.click('[data-a=sesion]'); f1 = u.flash(); c1 = u.shot('B-04_1.png', full=False)
    page.select_option('#stipo', 'grupal'); page.fill('#stema', 'Prueba B-04 grupal'); page.click('[data-a=todos]')
    cbs = page.locator('[name=asis]')
    for i in range(25, 40): cbs.nth(i).uncheck()
    page.click('[data-a=sesion]'); f2 = u.flash()
    fila = page.locator('main table tbody tr', has_text='Prueba B-04 grupal').first.inner_text(); c2 = u.shot('B-04_2.png', full=False)
    u.nav('informe'); page.fill('#icorte', '2026-11-18'); page.click('[data-a=corte]')
    big = page.locator('.panel .big').all_inner_texts(); itx = page.locator('.panel').inner_text(); c3 = u.shot('B-04_informe.png', full=False)
    fila_inf = page.locator('.panel table tbody tr', has_text='Prueba B-04 grupal')
    muestra_sesion = fila_inf.count() > 0 and '25' in fila_inf.first.inner_text()
    ok = 'acuerdos' in f1 and '25 asistente' in f2 and big[1].startswith('7 +')
    reg('B-04', f'Paso 1: «{f1}» Paso 2: «{f2}»; fila: «{" ".join(fila.split())}». Paso 3: el informe muestra «{big[1]}» sesiones; {"lista la sesión con sus asistentes" if muestra_sesion else "no lista la sesión ni su número de asistentes, solo los conteos por tipo"}.', ok, [c1, c2, c3], parcial=not muestra_sesion)

    u.login('APOYO-PSI'); u.folio('CAN-2026-0014'); u.solicitar('Atendida'); fl = u.flash(); h = u.hist(); est = u.estado()
    reg('B-05', f'Mensaje: «{fl}». Historial: {len(h)} cambio(s); estado {est}.', 'Transición no permitida' in fl and len(h) == 1 and est == 'Registrada', [u.shot('B-05_rechazo.png', full=False)])

    u.login('T01'); u.nav('canal'); u.folio('CAN-2026-0005'); u.solicitar('Cerrada'); f1 = u.flash(); e1 = u.estado(); c1 = u.shot('B-06_1.png', full=False)
    u.login('T02'); u.nav('canal'); u.folio('CAN-2026-0006'); u.tr('Cerrada', motivo=''); f2 = u.flash(); e2 = u.estado(); c2 = u.shot('B-06_2.png', full=False)
    reg('B-06', f'Paso 1: «{f1}»; estado {e1}. Paso 2: «{f2}»; estado {e2}.', 'no permitida' in f1 and 'RN-04' in f2 and e1 == 'Recibida' and e2 == 'Registrada', [c1, c2])

    u.login('APOYO-PSI'); u.folio('CAN-2026-0013'); u.tr('No asistió', obs='Prueba ESC-05'); f1 = u.flash(); e1 = u.estado(); c1 = u.shot('B-07_1.png', full=False)
    page.click('main [data-v="bandeja"]'); abiertas = [x.split('\n')[0] for x in page.locator('.card').all_inner_texts()]; c2 = u.shot('B-07_2.png', full=False)
    u.login('T03'); u.nav('canal'); u.folio('CAN-2026-0013'); u.tr('Cerrada', obs='Prueba ESC-05', motivo='Prueba ESC-05'); f3 = u.flash(); e3 = u.estado(); c3 = u.shot('B-07_3.png', full=False)
    ok = e1 == 'No asistió' and any('CAN-2026-0013' in a for a in abiertas) and e3 == 'Cerrada'
    reg('B-07', f'Paso 1: «{f1}»; estado {e1}. Paso 2: CAN-2026-0013 {"sigue" if any("CAN-2026-0013" in a for a in abiertas) else "no está"} en «Abiertas». Paso 3: «{f3}»; estado {e3}.', ok, [c1, c2, c3])

    u.login('APOYO-DA'); page.click('[data-band="todas"]'); todas = page.locator('.card').count(); page.click('[data-band=""]'); ab = page.locator('.card').count()
    insts = u.text(); c1 = u.shot('B-08_1.png', full=False)
    u.folio('CAN-2026-0012'); u.tr('Atendida', obs='Prueba B-08'); f2 = u.flash(); e2 = u.estado(); c2 = u.shot('B-08_2.png', full=False)
    u.login('T03'); u.nav('canal'); fila = page.locator('main table tbody tr', has_text='CAN-2026-0012').inner_text()
    u.nav('notif'); notif = [x.strip() for x in page.locator('main table tbody tr td:nth-child(2)').all_inner_texts()]; c3 = u.shot('B-08_3.png', full=False)
    ok = (todas, ab) == (6, 4) and e2 == 'Atendida' and 'Atendida' in fila and 'CAN-2026-0012' in notif and 'CAN-2026-0013' in notif
    reg('B-08', f'APOYO-DA: {todas} en «Todas», {ab} en «Abiertas». «{f2}»; estado {e2}. T03 ve CAN-2026-0012 en {"Atendida" if "Atendida" in fila else fila}; notificaciones: {", ".join(notif)}.', ok, [c1, c2, c3])

    u.login('ADMIN'); acc = [" ".join(x.split()) for x in page.locator('main table tbody tr td:nth-child(4)').all_inner_texts()]
    c1 = u.shot('B-09_bitacora.png')
    req = ['Intento denegado de canalización', 'Registro de canalización', 'Consulta de expediente', 'Registro de nota de seguimiento', 'Registro de sesión',
           'Cambio de estado Recibida → No asistió', 'Cambio de estado No asistió → Cerrada', 'Cambio de estado En atención → Atendida']
    falt = [x for x in req if x not in acc]
    extra = [x for x in acc if 'Recibida → Cerrada' in x or 'Registrada → Atendida' in x]
    reg('B-09', f'{len(acc)} registros en la bitácora. Acciones: {"; ".join(sorted(set(acc)))}. {"Faltan: " + ", ".join(falt) if falt else "Están todas las operaciones esperadas."} {"Rechazos registrados: " + ", ".join(extra) if extra else "Los rechazos no aparecen."}', not falt and not extra, [c1])
    ctx.close()


def bloque_C(b):
    ctx, page, u = nuevo(b, viewport={'width': 1280, 'height': 900})
    pasos = [('TR-01', 'APOYO-PSI', 'CAN-2026-0006', 'Recibida', False), ('TR-02', 'APOYO-PSI', 'CAN-2026-0005', 'En atención', False),
             ('TR-03', 'APOYO-PSI', 'CAN-2026-0004', 'Atendida', False), ('TR-04', 'APOYO-PSI', 'CAN-2026-0013', 'No asistió', False),
             ('TR-05', 'APOYO-DA', 'CAN-2026-0002', 'Recibida', False), ('TR-06', 'T01', 'CAN-2026-0001', 'Cerrada', False),
             ('TR-07', 'T03', 'CAN-2026-0014', 'Cerrada', True), ('TR-08', 'T02', 'CAN-2026-0010', 'Cerrada', True)]
    for id_, cuenta, f, dest, mot in pasos:
        u.login(cuenta)
        if cuenta.startswith('T0'): u.nav('canal')
        u.folio(f); u.tr(dest, obs=f'Prueba {id_}', motivo=f'Prueba {id_}' if mot else None)
        fl = u.flash(); est = u.estado(); h = u.hist()[-1]
        ok = est == dest and h[2] == dest and h[3] == cuenta and h[0].startswith('2026-11-18') and f'Prueba {id_}' in h[4] and (not mot or 'Motivo de cierre' in h[4])
        reg(id_, f'«{fl}»; estado {est}. Fila nueva: fecha {h[0]}, {h[1]} → {h[2]}, usuario {h[3]}, observación «{h[4]}».', ok, [u.shot(f'{id_}.png', full=False)])
    u.login('JEF_CARRERA'); u.folio('CAN-2026-0008'); u.tr('Escalada'); fl = u.flash(); est = u.estado()
    reg('TR-09', f'«{fl}»; estado {est}.', 'segundo incremento' in fl and est == 'Recibida', [u.shot('TR-09.png', full=False)])
    u.login('APOYO-DA'); u.folio('CAN-2026-0008'); u.tr('En atención', obs=''); fl = u.flash(); est = u.estado(); h = u.hist()[-1]
    acepto = est == 'En atención'
    reg('TR-10', f'«{fl}»; estado {est}. ' + (f'El cambio se registró con observación vacía (fila: {h[1]} → {h[2]}, usuario {h[3]}).' if acepto else 'El cambio no se registró.'), not acepto, [u.shot('TR-10.png', full=False)])
    notif = {}
    for t in ['T01', 'T02', 'T03']:
        u.login(t); u.nav('notif'); notif[t] = [x.strip() for x in page.locator('main table tbody tr td:nth-child(2)').all_inner_texts()]
        u.shot(f'TR-11_{t}.png', full=False)
    esp = {'T01': {'CAN-2026-0005', 'CAN-2026-0004', 'CAN-2026-0002'}, 'T02': {'CAN-2026-0006'} | ({'CAN-2026-0008'} if acepto else set()), 'T03': {'CAN-2026-0013'}}
    ok = all(set(notif[t]) == esp[t] and len(notif[t]) == len(esp[t]) for t in esp)
    reg('TR-11', ' | '.join(f'{t}: {len(v)} ({", ".join(v)})' for t, v in notif.items()), ok, [f'TR-11_{t}.png' for t in notif])
    ctx.close()


def bloque_D(b):
    ctx, page, u = nuevo(b, viewport={'width': 360, 'height': 740}, device_scale_factor=3, is_mobile=True, has_touch=True,
                         user_agent='Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Mobile Safari/537.36')
    anchos, caps = [], []
    def medir(n):
        w = page.evaluate('[document.documentElement.scrollWidth, document.documentElement.clientWidth]')
        # elementos que rebasan el ancho visible (excepto los contenedores con desplazamiento propio: nav y .scroll)
        fuera = page.evaluate('''() => { const cw = document.documentElement.clientWidth; return [...document.querySelectorAll('body *')].filter(e => !e.closest('nav,.scroll') && e.getClientRects().length && e.getBoundingClientRect().right > cw + 1).length; }''')
        anchos.append((n, (w[0] + fuera * 10000, w[1]) if fuera else w)); caps.append(u.shot(f'D-02_{n}.png'))
    medir('1_entrada'); u.login('APOYO-PSI'); medir('2_bandeja')
    u.folio('CAN-2026-0006'); medir('3_folio')
    for d in ['Recibida', 'En atención', 'Atendida']: u.tr(d, obs='Prueba D-02')
    medir('4_atendida')
    est = u.estado(); ok = all(sw <= cw for _, (sw, cw) in anchos) and est == 'Atendida'
    reg('D-02', f'Vista de 360 × 740 px (emulación móvil en Chrome). Ancho del contenido frente al de la pantalla (y elementos que lo rebasan): {"; ".join(f"{n}: {sw % 10000}/{cw} px, {sw // 10000} fuera" for n, (sw, cw) in anchos)}. Tareas de RF-07 completadas; estado final {est}.', ok, caps)
    ctx.close()

    ctx = b.new_context(viewport={'width': 1280, 'height': 900}); page = ctx.new_page()
    page.clock.install(); page.goto(URL); page.wait_for_selector('[data-login]'); u = UI(page)
    u.login('T01'); antes = page.locator('[data-a=salir]').count()
    page.clock.run_for('16:00'); page.wait_for_timeout(200)
    despues_login = page.locator('[data-login]').count() > 0
    reg('D-03', f'Sesión abierta con T01 ({"sí" if antes else "no"}); tras avanzar el reloj del navegador 16 minutos sin actividad, {"aparece la pantalla de selección de cuenta" if despues_login else "la sesión sigue abierta"}.', bool(antes) and despues_login, [u.shot('D-03.png', full=False)])
    ctx.close()


with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path='/usr/bin/google-chrome', headless=True)
    inicio = datetime.datetime.now().isoformat(timespec='seconds')
    for f in (bloque_A, bloque_B, bloque_C, bloque_D):
        try: f(browser)
        except Exception as e:
            print('ERROR en', f.__name__, repr(e)); R.append({'id': f.__name__, 'observado': 'Error del script: ' + repr(e), 'resultado': 'Error', 'capturas': []})
    ver = browser.version; browser.close()
json.dump({'etiqueta': ETIQ, 'prototipo': PROTO.name, 'inicio': inicio, 'fin': datetime.datetime.now().isoformat(timespec='seconds'),
           'navegador': f'Google Chrome {ver} sin pantalla (Playwright)', 'resultados': R}, open(OUT / 'resultados.json', 'w'), ensure_ascii=False, indent=1)
print('Pasa', sum(r['resultado'] == 'Pasa' for r in R), 'Falla', sum(r['resultado'] == 'Falla' for r in R), 'Parcial', sum(r['resultado'] == 'Parcial' for r in R), 'Error', sum(r['resultado'] == 'Error' for r in R))
