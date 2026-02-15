import time
import os
import sys
from zapv2 import ZAPv2

print("="*60)
print("OWASP ZAP SCAN - PyGoat")
print("="*60)

api_key = os.environ.get('ZAP_API_KEY', '')
target = 'http://localhost:8000'

print(f"[1] Target: {target}")
print(f"[2] API Key: {'✅ OK' if api_key else '❌ NO'}")

# Conectar a ZAP
print(f"[3] Conectando a ZAP en http://localhost:8080...")
zap = ZAPv2(apikey=api_key, proxies={'http': 'http://localhost:8080', 'https': 'http://localhost:8080'})

# Intentar conectar con reintentos
conectado = False
for i in range(20):
    try:
        version = zap.core.version
        print(f"    ✅ ZAP conectado. Versión: {version}")
        conectado = True
        break
    except Exception as e:
        print(f"    ⏳ Intento {i+1}/20: ZAP no responde, esperando 3s...")
        time.sleep(3)

if not conectado:
    print("    ❌ No se pudo conectar a ZAP")
    sys.exit(1)

# Nueva sesión
print("[4] Creando nueva sesión...")
zap.core.new_session(name='pygoat-scan', overwrite=True)

# Spider
print("[5] Iniciando spider...")
zap.spider.scan(target)
time.sleep(5)
for i in range(12):
    status = zap.spider.status()
    print(f"    Spider: {status}%")
    if status == '100':
        break
    time.sleep(5)

# Escaneo activo
print("[6] Iniciando escaneo activo...")
zap.ascan.scan(target)
time.sleep(5)
for i in range(15):
    status = zap.ascan.status()
    print(f"    Escaneo: {status}%")
    if status == '100':
        break
    time.sleep(5)

# Obtener alertas
print("[7] Obteniendo alertas...")
alerts = zap.core.alerts()
high_alerts = [a for a in alerts if a.get('risk') == 'High']
medium_alerts = [a for a in alerts if a.get('risk') == 'Medium']
low_alerts = [a for a in alerts if a.get('risk') == 'Low']

print(f"\n📊 RESULTADOS:")
print(f"  🔴 HIGH: {len(high_alerts)}")
print(f"  🟡 MEDIUM: {len(medium_alerts)}")
print(f"  🟢 LOW: {len(low_alerts)}")
print(f"  📋 TOTAL: {len(alerts)}")

# ============================================
# GENERAR REPORTE HTML MODERNO - DASHBOARD
# ============================================
print("[8] Generando reporte HTML moderno...")

html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OWASP ZAP · PyGoat Report</title>
    <!-- Font Awesome 6 (gratuito) -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            background: linear-gradient(145deg, #f6f9fc 0%, #e9f1f8 100%);
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            padding: 2rem 1.5rem;
            color: #1a2639;
        }}
        .dashboard {{
            max-width: 1600px;
            margin: 0 auto;
        }}
        /* header */
        .header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 2rem;
            flex-wrap: wrap;
            gap: 1rem;
        }}
        .header h1 {{
            font-size: 2.2rem;
            font-weight: 600;
            background: linear-gradient(135deg, #0b2b3d, #1b4a6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            display: inline-flex;
            align-items: center;
            gap: 12px;
        }}
        .badge-date {{
            background: rgba(255,255,255,0.7);
            backdrop-filter: blur(6px);
            padding: 0.5rem 1.2rem;
            border-radius: 40px;
            font-weight: 500;
            box-shadow: 0 8px 20px rgba(0,20,40,0.08);
            border: 1px solid rgba(255,255,255,0.5);
        }}
        .target-info {{
            background: #ffffffcc;
            backdrop-filter: blur(4px);
            padding: 0.5rem 1.5rem;
            border-radius: 40px;
            font-family: monospace;
            font-size: 1.1rem;
            border: 1px solid #ffffff;
            box-shadow: 0 4px 10px rgba(0,0,0,0.02);
        }}
        /* KPI Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1.5rem;
            margin-bottom: 2.5rem;
        }}
        .kpi-card {{
            background: white;
            padding: 1.5rem 1rem;
            border-radius: 28px;
            box-shadow: 0 20px 35px -8px rgba(0,30,60,0.15);
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: transform 0.2s ease;
            border: 1px solid rgba(255,255,255,0.6);
            backdrop-filter: blur(2px);
        }}
        .kpi-card:hover {{
            transform: translateY(-5px);
        }}
        .kpi-icon {{
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
        }}
        .kpi-content {{
            text-align: right;
        }}
        .kpi-label {{
            font-size: 1rem;
            font-weight: 500;
            color: #4a5b6e;
            letter-spacing: 0.3px;
        }}
        .kpi-value {{
            font-size: 2.8rem;
            font-weight: 700;
            line-height: 1.2;
        }}
        .high-bg {{ background: #fee9e7; color: #b81b1b; }}
        .medium-bg {{ background: #fff0d9; color: #b45b0a; }}
        .low-bg {{ background: #e0f2e9; color: #1e7b4c; }}
        .total-bg {{ background: #e1e8f5; color: #1a3a6b; }}
        /* tabs para secciones de riesgo */
        .risk-tabs {{
            display: flex;
            gap: 0.8rem;
            margin: 2rem 0 1.2rem;
            flex-wrap: wrap;
        }}
        .tab {{
            padding: 0.7rem 2rem;
            border-radius: 60px;
            font-weight: 600;
            background: white;
            box-shadow: 0 6px 14px rgba(0,0,0,0.02);
            border: 1px solid #dee7ef;
            color: #2c3e50;
            cursor: default;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .tab.high {{ border-left: 6px solid #c42e2e; }}
        .tab.medium {{ border-left: 6px solid #e68a2e; }}
        .tab.low {{ border-left: 6px solid #2e9a6e; }}
        .tab i {{ font-size: 1.1rem; }}
        /* contador en tabs */
        .count-badge {{
            background: #edf2f7;
            padding: 2px 12px;
            border-radius: 40px;
            font-size: 0.85rem;
            font-weight: 600;
            color: #1e2f40;
        }}
        /* grid de alertas */
        .alerts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
            margin-bottom: 2rem;
        }}
        .alert-card {{
            background: white;
            border-radius: 24px;
            padding: 1.5rem;
            box-shadow: 0 12px 28px -8px rgba(0,20,40,0.12);
            border-left: 6px solid;
            transition: all 0.2s;
            display: flex;
            flex-direction: column;
            border-image: none;
        }}
        .alert-card.high {{ border-left-color: #c42e2e; }}
        .alert-card.medium {{ border-left-color: #e68a2e; }}
        .alert-card.low {{ border-left-color: #2e9a6e; }}
        .alert-title {{
            font-size: 1.3rem;
            font-weight: 600;
            margin-bottom: 0.7rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .risk-tag {{
            padding: 4px 12px;
            border-radius: 40px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }}
        .risk-tag.high {{ background: #c42e2e10; color: #aa2222; border: 1px solid #c42e2e30; }}
        .risk-tag.medium {{ background: #e68a2e10; color: #a35200; border: 1px solid #e68a2e30; }}
        .risk-tag.low {{ background: #2e9a6e10; color: #1b6e4a; border: 1px solid #2e9a6e30; }}
        .url {{
            background: #f2f6fa;
            padding: 0.5rem 0.8rem;
            border-radius: 14px;
            font-family: 'SF Mono', 'Fira Code', monospace;
            font-size: 0.85rem;
            word-break: break-all;
            margin: 0.8rem 0;
            border: 1px solid #dde5ed;
        }}
        .conf-badge {{
            display: inline-block;
            background: #eaeef3;
            padding: 0.2rem 0.8rem;
            border-radius: 40px;
            font-size: 0.8rem;
            font-weight: 500;
            margin-bottom: 0.8rem;
        }}
        .description {{
            color: #2e405b;
            line-height: 1.5;
            margin: 0.5rem 0;
            font-size: 0.95rem;
        }}
        .solution-box {{
            background: #f1f9f0;
            padding: 1rem;
            border-radius: 18px;
            margin: 0.8rem 0;
            border-left: 4px solid #368f55;
            font-size: 0.9rem;
        }}
        .reference {{
            margin-top: 0.6rem;
            font-size: 0.8rem;
            color: #5a6f88;
            word-break: break-all;
        }}
        .reference a {{
            color: #1a5d9c;
            text-decoration: none;
        }}
        .footer {{
            margin-top: 3rem;
            text-align: right;
            color: #4f6f8f;
            border-top: 1px dashed #b3c6d9;
            padding-top: 1.5rem;
            font-size: 0.9rem;
        }}
        .no-alerts {{
            background: white;
            border-radius: 32px;
            padding: 3rem;
            text-align: center;
            color: #4a6885;
            font-size: 1.3rem;
            border: 2px dashed #bdd3e8;
        }}
        @media (max-width: 700px) {{
            .kpi-grid {{ grid-template-columns: 1fr 1fr; }}
            .alerts-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
<div class="dashboard">
    <div class="header">
        <div>
            <h1><i class="fas fa-shield-halved" style="background: linear-gradient(135deg,#1b4a6b,#0b2b3d); -webkit-background-clip:text; -webkit-text-fill-color:transparent;"></i> OWASP ZAP · PyGoat</h1>
            <div style="display: flex; gap: 1rem; margin-top: 0.5rem; flex-wrap: wrap;">
                <span class="badge-date"><i class="far fa-calendar-alt"></i> {time.strftime('%Y-%m-%d %H:%M:%S')}</span>
                <span class="target-info"><i class="fas fa-crosshairs"></i> {target}</span>
            </div>
        </div>
        <div style="font-size: 1.2rem; background: white; padding: 0.5rem 1.8rem; border-radius: 60px; box-shadow: 0 4px 12px rgba(0,0,0,0.02);">
            <i class="fas fa-bolt" style="color: #f97316;"></i> DAST Scan
        </div>
    </div>

    <!-- KPIs -->
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-icon high-bg"><i class="fas fa-exclamation-triangle"></i></div>
            <div class="kpi-content">
                <div class="kpi-label">ALTO RIESGO</div>
                <div class="kpi-value" style="color:#b81b1b;">{len(high_alerts)}</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon medium-bg"><i class="fas fa-chart-line"></i></div>
            <div class="kpi-content">
                <div class="kpi-label">MEDIO</div>
                <div class="kpi-value" style="color:#b45b0a;">{len(medium_alerts)}</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon low-bg"><i class="fas fa-info-circle"></i></div>
            <div class="kpi-content">
                <div class="kpi-label">BAJO</div>
                <div class="kpi-value" style="color:#1e7b4c;">{len(low_alerts)}</div>
            </div>
        </div>
        <div class="kpi-card">
            <div class="kpi-icon total-bg"><i class="fas fa-list-check"></i></div>
            <div class="kpi-content">
                <div class="kpi-label">TOTAL</div>
                <div class="kpi-value" style="color:#1a3a6b;">{len(alerts)}</div>
            </div>
        </div>
    </div>

    <!-- Pestañas indicativas (solo decoración) -->
    <div class="risk-tabs">
        <div class="tab high"><i class="fas fa-bolt"></i> HIGH <span class="count-badge">{len(high_alerts)}</span></div>
        <div class="tab medium"><i class="fas fa-wave-square"></i> MEDIUM <span class="count-badge">{len(medium_alerts)}</span></div>
        <div class="tab low"><i class="fas fa-leaf"></i> LOW <span class="count-badge">{len(low_alerts)}</span></div>
    </div>
"""

# ============================================
# SECCIÓN HIGH
# ============================================
html_content += f"""
    <h2 style="font-weight: 600; margin-top: 1rem; display: flex; align-items: center; gap:10px;"><i class="fas fa-bolt" style="color:#c42e2e;"></i> Vulnerabilidades de Alto Riesgo ({len(high_alerts)})</h2>
"""
if high_alerts:
    html_content += '<div class="alerts-grid">'
    for alert in high_alerts:
        html_content += f"""
        <div class="alert-card high">
            <div class="alert-title">
                <span>{alert.get('alert', 'N/A')}</span>
                <span class="risk-tag high">HIGH</span>
            </div>
            <div class="url"><i class="fas fa-link" style="opacity:0.7;"></i> {alert.get('url', 'N/A')}</div>
            <div><span class="conf-badge"><i class="fas fa-check-circle"></i> Confianza: {alert.get('confidence', 'N/A')}</span></div>
            <div class="description"><i class="fas fa-align-left" style="margin-right:6px; color:#4f6f8f;"></i> {alert.get('description', 'N/A')}</div>
            <div class="solution-box"><i class="fas fa-lightbulb" style="margin-right:8px;"></i> <strong>Solución:</strong> {alert.get('solution', 'No disponible')}</div>
            <div class="reference"><i class="fas fa-book-open"></i> <strong>Referencia:</strong> {alert.get('reference', 'N/A')}</div>
        </div>
        """
    html_content += '</div>'
else:
    html_content += '<div class="no-alerts"><i class="fas fa-circle-check" style="color: #2e9a6e;"></i> No se encontraron vulnerabilidades de alto riesgo.</div>'

# ============================================
# SECCIÓN MEDIUM
# ============================================
html_content += f"""
    <h2 style="font-weight: 600; margin-top: 2.5rem; display: flex; align-items: center; gap:10px;"><i class="fas fa-wave-square" style="color:#e68a2e;"></i> Vulnerabilidades de Riesgo Medio ({len(medium_alerts)})</h2>
"""
if medium_alerts:
    html_content += '<div class="alerts-grid">'
    for alert in medium_alerts:
        html_content += f"""
        <div class="alert-card medium">
            <div class="alert-title">
                <span>{alert.get('alert', 'N/A')}</span>
                <span class="risk-tag medium">MEDIUM</span>
            </div>
            <div class="url"><i class="fas fa-link" style="opacity:0.7;"></i> {alert.get('url', 'N/A')}</div>
            <div><span class="conf-badge"><i class="fas fa-check-circle"></i> Confianza: {alert.get('confidence', 'N/A')}</span></div>
            <div class="description"><i class="fas fa-align-left" style="margin-right:6px; color:#4f6f8f;"></i> {alert.get('description', 'N/A')}</div>
            <div class="solution-box"><i class="fas fa-lightbulb" style="margin-right:8px;"></i> <strong>Solución:</strong> {alert.get('solution', 'No disponible')}</div>
        </div>
        """
    html_content += '</div>'
else:
    html_content += '<div class="no-alerts"><i class="fas fa-circle-check" style="color: #2e9a6e;"></i> No se encontraron vulnerabilidades de riesgo medio.</div>'

# ============================================
# SECCIÓN LOW
# ============================================
html_content += f"""
    <h2 style="font-weight: 600; margin-top: 2.5rem; display: flex; align-items: center; gap:10px;"><i class="fas fa-leaf" style="color:#2e9a6e;"></i> Vulnerabilidades de Riesgo Bajo ({len(low_alerts)})</h2>
"""
if low_alerts:
    html_content += '<div class="alerts-grid">'
    for alert in low_alerts:
        html_content += f"""
        <div class="alert-card low">
            <div class="alert-title">
                <span>{alert.get('alert', 'N/A')}</span>
                <span class="risk-tag low">LOW</span>
            </div>
            <div class="url"><i class="fas fa-link" style="opacity:0.7;"></i> {alert.get('url', 'N/A')}</div>
            <div><span class="conf-badge"><i class="fas fa-check-circle"></i> Confianza: {alert.get('confidence', 'N/A')}</span></div>
            <div class="description"><i class="fas fa-align-left" style="margin-right:6px; color:#4f6f8f;"></i> {alert.get('description', 'N/A')}</div>
        </div>
        """
    html_content += '</div>'
else:
    html_content += '<div class="no-alerts"><i class="fas fa-circle-check" style="color: #2e9a6e;"></i> No se encontraron vulnerabilidades de riesgo bajo.</div>'

# ============================================
# PIE DE PÁGINA CON METADATOS
# ============================================
try:
    commit_hash = os.popen('git rev-parse --short HEAD').read().strip()
except:
    commit_hash = 'N/A'
html_content += f"""
    <div class="footer">
        <i class="fas fa-bug"></i> Reporte generado automáticamente · <strong>Versión ZAP:</strong> {zap.core.version} · <i class="fas fa-code-branch"></i> commit {commit_hash if commit_hash else 'desconocido'}<br>
        <span style="opacity:0.5;">OWASP ZAP DAST · PyGoat · {time.strftime('%Y-%m-%d %H:%M')}</span>
    </div>
</div>
</body>
</html>
"""

# Guardar reporte
with open('zap-report.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

# Verificar
if os.path.exists('zap-report.html'):
    size = os.path.getsize('zap-report.html')
    print(f"    ✅ Reporte HTML moderno generado: {size} bytes")
else:
    print("    ❌ No se pudo generar el reporte")
    sys.exit(1)

# ============================================
# ACEPTACIÓN DE RIESGOS - PRÁCTICA DOCENTE
# ============================================
if len(high_alerts) > 0:
    print(f"\n⚠️  SE ENCONTRARON {len(high_alerts)} VULNERABILIDADES HIGH")
    print("   🔴 EN UN ENTORNO REAL ESTO PARARÍA EL PIPELINE")
    print("   🟢 ACEPTADAS PARA LABORATORIO DOCENTE - CONTINUANDO...")
    print("\n   Vulnerabilidades encontradas (solo informe):")
    for alert in high_alerts[:5]:
        print(f"     • {alert.get('alert', 'N/A')}")
    if len(high_alerts) > 5:
        print(f"     • ... y {len(high_alerts)-5} más")
    sys.exit(0)
else:
    print("\n✅ PIPELINE EXITOSO: No hay vulnerabilidades HIGH")
    sys.exit(0)
