import json
import re
import pandas as pd
import folium
from folium.plugins import HeatMap

# 1. Catálogo ampliado de Hospitales y Unidades Médicas del IMSS en México
COORDS_HOSPITALES_IMSS = {
    "HGZ 89 Guadalajara": {"coords": [20.6552, -103.3648], "zona": "Guadalajara, Jal."},
    "UMF 51 Zapopan": {"coords": [20.7225, -103.3892], "zona": "Zapopan, Jal."},
    "Centro Médico Nacional Occidente": {"coords": [20.6865, -103.3280], "zona": "Guadalajara, Jal."},
    "CMN Siglo XXI CDMX": {"coords": [19.4058, -99.1558], "zona": "Cuauhtémoc, CDMX"},
    "CMN La Raza CDMX": {"coords": [19.4695, -99.1432], "zona": "Azcapotzalco, CDMX"},
    "HGZ 33 Monterrey": {"coords": [25.6830, -100.3080], "zona": "Monterrey, N.L."},
    "HGR 1 Tijuana": {"coords": [32.5140, -116.9720], "zona": "Tijuana, B.C."},
    "HGZ 1 Puebla": {"coords": [19.0430, -98.1980], "zona": "Puebla, Pue."},
    "HGZ 71 Veracruz": {"coords": [19.1800, -96.1600], "zona": "Veracruz, Ver."},
    "HGR 1 Mérida": {"coords": [20.9700, -89.6200], "zona": "Mérida, Yuc."},
    "HGZ 1 León": {"coords": [21.1200, -101.6800], "zona": "León, Gto."},
    "HGZ 1 San Luis Potosí": {"coords": [22.1500, -100.9800], "zona": "San Luis Potosí, S.L.P."},
    "HGZ 1 Culiacán": {"coords": [24.8000, -107.3900], "zona": "Culiacán, Sin."},
    "HGZ 14 Hermosillo": {"coords": [29.0880, -110.9600], "zona": "Hermosillo, Son."},
    "HGZ 1 Tapachula": {"coords": [14.9080, -92.2600], "zona": "Tapachula, Chis."},
    "UMF 34 Guadalajara": {"coords": [20.6720, -103.3410], "zona": "Guadalajara, Jal."},
    "HGZ 1 Querétaro": {"coords": [20.5900, -100.3900], "zona": "Querétaro, Qro."},
    "HGZ 1 Morelia": {"coords": [19.7000, -101.1900], "zona": "Morelia, Mich."},
}

def cargar_datos_compras():
    contratos = [
        # Insulina Humana
        {"id_contrato": "IMSS-2026-0101", "medicamento": "Insulina Humana NPH", "proveedor": "FarmaDistribuidora MX", "cantidad": 150000, "monto_total": 22500000, "precio_unitario": 150.0, "estatus": "A tiempo", "hospital": "HGZ 89 Guadalajara"},
        {"id_contrato": "IMSS-2026-0102", "medicamento": "Insulina Humana NPH", "proveedor": "Suministros Médicos del Norte", "cantidad": 50000, "monto_total": 16000000, "precio_unitario": 320.0, "estatus": "Crítico / Faltante", "hospital": "Centro Médico Nacional Occidente"},
        {"id_contrato": "IMSS-2026-0103", "medicamento": "Insulina Humana NPH", "proveedor": "FarmaDistribuidora MX", "cantidad": 80000, "monto_total": 12000000, "precio_unitario": 150.0, "estatus": "Atrasado", "hospital": "UMF 51 Zapopan"},
        {"id_contrato": "IMSS-2026-0104", "medicamento": "Insulina Humana NPH", "proveedor": "PharmaSur SA", "cantidad": 60000, "monto_total": 18000000, "precio_unitario": 300.0, "estatus": "Crítico / Faltante", "hospital": "HGZ 1 Puebla"},
        
        # Metformina
        {"id_contrato": "IMSS-2026-0201", "medicamento": "Metformina 850mg", "proveedor": "Comercializadora Meds SA", "cantidad": 500000, "monto_total": 7500000, "precio_unitario": 15.0, "estatus": "Atrasado", "hospital": "UMF 51 Zapopan"},
        {"id_contrato": "IMSS-2026-0202", "medicamento": "Metformina 850mg", "proveedor": "Laboratorios Unidos", "cantidad": 300000, "monto_total": 4200000, "precio_unitario": 14.0, "estatus": "A tiempo", "hospital": "UMF 34 Guadalajara"},
        {"id_contrato": "IMSS-2026-0203", "medicamento": "Metformina 850mg", "proveedor": "ProveeSalud Norte", "cantidad": 400000, "monto_total": 12000000, "precio_unitario": 30.0, "estatus": "Crítico / Faltante", "hospital": "HGZ 33 Monterrey"},
        
        # Inmunosupresores y Oncología
        {"id_contrato": "IMSS-2026-0301", "medicamento": "Ciclosporina 100mg", "proveedor": "Grupo Pharma Global", "cantidad": 20000, "monto_total": 18000000, "precio_unitario": 900.0, "estatus": "Crítico / Faltante", "hospital": "Centro Médico Nacional Occidente"},
        {"id_contrato": "IMSS-2026-0302", "medicamento": "Ciclosporina 100mg", "proveedor": "BioTech Solutions", "cantidad": 10000, "monto_total": 18500000, "precio_unitario": 1850.0, "estatus": "Crítico / Faltante", "hospital": "CMN Siglo XXI CDMX"},
        {"id_contrato": "IMSS-2026-0303", "medicamento": "Paclitaxel 100mg", "proveedor": "OncoFarma MX", "cantidad": 15000, "monto_total": 45000000, "precio_unitario": 3000.0, "estatus": "Atrasado", "hospital": "CMN La Raza CDMX"},
        {"id_contrato": "IMSS-2026-0304", "medicamento": "Paclitaxel 100mg", "proveedor": "Distribuidora Especializada", "cantidad": 8000, "monto_total": 48000000, "precio_unitario": 6000.0, "estatus": "Crítico / Faltante", "hospital": "HGR 1 Tijuana"},

        # Antihipertensivos y Básicos
        {"id_contrato": "IMSS-2026-0401", "medicamento": "Losartán 50mg", "proveedor": "Genéricos de México", "cantidad": 600000, "monto_total": 6000000, "precio_unitario": 10.0, "estatus": "A tiempo", "hospital": "HGZ 71 Veracruz"},
        {"id_contrato": "IMSS-2026-0402", "medicamento": "Losartán 50mg", "proveedor": "Suministros Globales", "cantidad": 200000, "monto_total": 5000000, "precio_unitario": 25.0, "estatus": "Atrasado", "hospital": "HGR 1 Mérida"},
        {"id_contrato": "IMSS-2026-0403", "medicamento": "Paracetamol 500mg", "proveedor": "FarmaDistribuidora MX", "cantidad": 1000000, "monto_total": 3000000, "precio_unitario": 3.0, "estatus": "A tiempo", "hospital": "HGZ 14 Hermosillo"},
        {"id_contrato": "IMSS-2026-0404", "medicamento": "Paracetamol 500mg", "proveedor": "Distribuidora Express", "cantidad": 200000, "monto_total": 1800000, "precio_unitario": 9.0, "estatus": "Atrasado", "hospital": "HGZ 1 Tapachula"},
        {"id_contrato": "IMSS-2026-0405", "medicamento": "Omeprazol 20mg", "proveedor": "Meds del Bajío", "cantidad": 400000, "monto_total": 3200000, "precio_unitario": 8.0, "estatus": "A tiempo", "hospital": "HGZ 1 León"},
        {"id_contrato": "IMSS-2026-0406", "medicamento": "Omeprazol 20mg", "proveedor": "Pharma Potosí", "cantidad": 150000, "monto_total": 2700000, "precio_unitario": 18.0, "estatus": "Atrasado", "hospital": "HGZ 1 San Luis Potosí"},
        {"id_contrato": "IMSS-2026-0407", "medicamento": "Losartán 50mg", "proveedor": "Farma Sinaloa", "cantidad": 300000, "monto_total": 3600000, "precio_unitario": 12.0, "estatus": "A tiempo", "hospital": "HGZ 1 Culiacán"},
        {"id_contrato": "IMSS-2026-0408", "medicamento": "Metformina 850mg", "proveedor": "Distribuidora del Centro", "cantidad": 250000, "monto_total": 3750000, "precio_unitario": 15.0, "estatus": "A tiempo", "hospital": "HGZ 1 Querétaro"},
        {"id_contrato": "IMSS-2026-0409", "medicamento": "Insulina Humana NPH", "proveedor": "Meds Michoacán", "cantidad": 40000, "monto_total": 11200000, "precio_unitario": 280.0, "estatus": "Crítico / Faltante", "hospital": "HGZ 1 Morelia"},
    ]
    return pd.DataFrame(contratos)

def detectar_sobreprecios(df):
    promedios = df.groupby("medicamento")["precio_unitario"].mean().to_dict()
    df["precio_promedio_mercado"] = df["medicamento"].map(promedios)
    df["alerta_sobreprecio"] = df["precio_unitario"] > (df["precio_promedio_mercado"] * 1.35)
    df["porcentaje_desvio"] = ((df["precio_unitario"] - df["precio_promedio_mercado"]) / df["precio_promedio_mercado"]) * 100
    return df

def generar_dashboard(df):
    print("[*] Generando mapa interactivo geoespacial y reporte enriquecido...")
    
    mapa = folium.Map(location=[23.6345, -102.5528], zoom_start=5, tiles="OpenStreetMap")
    
    # Capa de Mapa de Calor
    puntos_calor = []
    for _, row in df.iterrows():
        hosp_info = COORDS_HOSPITALES_IMSS.get(row["hospital"])
        if hosp_info:
            peso = 2.0 if row["alerta_sobreprecio"] or "Crítico" in row["estatus"] else 1.0
            puntos_calor.append([hosp_info["coords"][0], hosp_info["coords"][1], peso])
            
    HeatMap(puntos_calor, radius=28, blur=18, max_zoom=10).add_to(mapa)
    
    # Capa de Marcadores de Hospitales
    capa_alertas = folium.FeatureGroup(name="Hospitales Auditados").add_to(mapa)
    
    for _, row in df.iterrows():
        hosp_info = COORDS_HOSPITALES_IMSS.get(row["hospital"])
        if not hosp_info:
            continue
            
        lat, lon = hosp_info["coords"]
        
        if row["alerta_sobreprecio"] or "Crítico" in row["estatus"]:
            color_pin = "red"
            icono = "exclamation-triangle"
        elif "Atrasado" in row["estatus"]:
            color_pin = "orange"
            icono = "clock"
        else:
            color_pin = "green"
            icono = "check-circle"
            
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 12px; width: 260px;">
            <h4 style="margin: 0 0 5px 0;">{row['hospital']}</h4>
            <b>{hosp_info['zona']}</b><hr style="margin: 5px 0;">
            <b>Medicamento:</b> {row['medicamento']}<br>
            <b>Estatus Abasto:</b> <b style="color: {'red' if 'Crítico' in row['estatus'] else 'orange' if 'Atrasado' in row['estatus'] else 'green'};">{row['estatus']}</b><br>
            <b>Proveedor:</b> {row['proveedor']}<br>
            <b>Precio Unitario:</b> ${row['precio_unitario']:,.2f} MXN<br>
            <b>Promedio Mercado:</b> ${row['precio_promedio_mercado']:,.2f} MXN<br>
            <b>Contrato ID:</b> {row['id_contrato']}
        </div>
        """
        
        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{row['hospital']} - {row['medicamento']}",
            icon=folium.Icon(color=color_pin, icon=icono, prefix="fa")
        ).add_to(capa_alertas)

    mapa.save("index.html")
    
    monto_total = df["monto_total"].sum()
    total_alertas = len(df[df["alerta_sobreprecio"]])
    total_criticos = len(df[df["estatus"].str.contains("Crítico")])
    
    filas_tabla_html = ""
    for _, r in df.iterrows():
        badge_color = "#e53935" if "Crítico" in r["estatus"] else ("#f57c00" if "Atrasado" in r["estatus"] else "#43a047")
        sobreprecio_str = f"<span style='color:#d32f2f; font-weight:bold;'>+ {r['porcentaje_desvio']:.0f}%</span>" if r["alerta_sobreprecio"] else "<span style='color:#388e3c;'>Normal</span>"
        
        filas_tabla_html += f"""
        <tr style="border-bottom: 1px solid #ddd; font-size: 11px;">
            <td style="padding: 6px;"><b>{r['hospital']}</b></td>
            <td style="padding: 6px;">{r['medicamento']}</td>
            <td style="padding: 6px;">{r['proveedor']}</td>
            <td style="padding: 6px;">${r['precio_unitario']:,.2f}</td>
            <td style="padding: 6px;">${r['precio_promedio_mercado']:,.2f}</td>
            <td style="padding: 6px;">{sobreprecio_str}</td>
            <td style="padding: 6px;"><span style="background:{badge_color}; color:white; padding:2px 6px; border-radius:3px; font-weight:bold;">{r['estatus']}</span></td>
        </tr>
        """

    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    template_interfaz = """
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>

    <div id="export-container" style="position: absolute; top: 12px; right: 12px; z-index: 9999; background: white; padding: 16px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.25); font-family: sans-serif; width: 310px;">
        <h3 style="margin:0 0 6px 0; font-size: 15px; color: #b71c1c;">📋 Auditoría de Abasto IMSS</h3>
        <p style="font-size: 11px; color: #555; margin-bottom: 12px;">Monitoreo cívico de compras públicas, sobreprecios y desabasto.</p>

        <button onclick="exportarPDF()" style="width: 100%; background: #b71c1c; color: white; border: none; padding: 9px; border-radius: 5px; font-weight: bold; cursor: pointer; margin-bottom: 8px; font-size: 12px;">
            📄 Descargar Reporte PDF
        </button>

        <button onclick="exportarPNG()" style="width: 100%; background: #1565c0; color: white; border: none; padding: 9px; border-radius: 5px; font-weight: bold; cursor: pointer; font-size: 12px;">
            🖼️ Exportar Infografía (PNG)
        </button>
    </div>

    <div id="reporte-ejecutivo" style="display:none; width: 800px; padding: 30px; background: white; font-family: Arial, sans-serif; color: #222;">
        <div style="border-bottom: 3px solid #b71c1c; padding-bottom: 10px; margin-bottom: 20px;">
            <h1 style="margin:0; color: #b71c1c; font-size: 24px;">REPORTE EJECUTIVO DE AUDITORÍA Y ABASTO IMSS</h1>
            <p style="margin: 5px 0 0 0; color: #666; font-size: 12px;">Monitor Cívico de Compras Públicas e Insumos Médicos | Datos Abiertos</p>
        </div>

        <div style="display: flex; gap: 15px; margin-bottom: 20px;">
            <div style="flex: 1; background: #f5f5f5; padding: 12px; border-radius: 6px; border-left: 4px solid #b71c1c;">
                <span style="font-size: 10px; color: #666; text-transform: uppercase;">Monto Auditado</span>
                <h3 style="margin: 4px 0 0 0; font-size: 18px;">${MONTO_TOTAL} MXN</h3>
            </div>
            <div style="flex: 1; background: #f5f5f5; padding: 12px; border-radius: 6px; border-left: 4px solid #d32f2f;">
                <span style="font-size: 10px; color: #666; text-transform: uppercase;">Sobreprecios Alerta</span>
                <h3 style="margin: 4px 0 0 0; font-size: 18px; color: #d32f2f;">{TOTAL_ALERTAS} Contratos</h3>
            </div>
            <div style="flex: 1; background: #f5f5f5; padding: 12px; border-radius: 6px; border-left: 4px solid #f57c00;">
                <span style="font-size: 10px; color: #666; text-transform: uppercase;">Faltantes Críticos</span>
                <h3 style="margin: 4px 0 0 0; font-size: 18px; color: #f57c00;">{TOTAL_CRITICOS} Hospitales</h3>
            </div>
        </div>

        <h3 style="font-size: 14px; margin-bottom: 8px; color: #333;">Desglose de Contratos e Inconsistencias Detectadas</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <thead>
                <tr style="background: #212121; color: white; font-size: 11px; text-align: left;">
                    <th style="padding: 8px;">Hospital / Unidad</th>
                    <th style="padding: 8px;">Medicamento</th>
                    <th style="padding: 8px;">Proveedor</th>
                    <th style="padding: 8px;">Precio Pagado</th>
                    <th style="padding: 8px;">Prom. Mercado</th>
                    <th style="padding: 8px;">Desvío</th>
                    <th style="padding: 8px;">Estatus</th>
                </tr>
            </thead>
            <tbody>
                {FILAS_TABLA}
            </tbody>
        </table>

        <div style="border-top: 1px solid #ccc; pt: 10px; font-size: 10px; color: #777; display: flex; justify-content: space-between;">
            <span>Generado automáticamente por Monitor Cívico IMSS (OSINT & Data Analytics)</span>
            <span>https://ilovelace-2004.github.io/monitor-imss-datos/</span>
        </div>
    </div>

    <script>
    function exportarPDF() {
        const element = document.getElementById('reporte-ejecutivo');
        element.style.display = 'block';
        const opt = {
          margin:       0.3,
          filename:     'Reporte_Auditoria_IMSS_Completo.pdf',
          image:        { type: 'jpeg', quality: 0.98 },
          html2canvas:  { scale: 2 },
          jsPDF:        { unit: 'in', format: 'letter', orientation: 'landscape' }
        };
        html2pdf().set(opt).from(element).save().then(() => {
            element.style.display = 'none';
        });
    }

    function exportarPNG() {
        const element = document.getElementById('reporte-ejecutivo');
        element.style.display = 'block';
        html2canvas(element, { scale: 2 }).then(canvas => {
            const link = document.createElement('a');
            link.download = 'Infografia_Auditoria_IMSS.png';
            link.href = canvas.toDataURL('image/png');
            link.click();
            element.style.display = 'none';
        });
    }
    </script>
    """

    panel_interfaz = (template_interfaz
                      .replace("{MONTO_TOTAL}", f"{monto_total:,.2f}")
                      .replace("{TOTAL_ALERTAS}", str(total_alertas))
                      .replace("{TOTAL_CRITICOS}", str(total_criticos))
                      .replace("{FILAS_TABLA}", filas_tabla_html))

    html_content = html_content.replace("<body>", "<body>" + panel_interfaz)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("[✓] Dashboard web generado exitosamente en index.html")

if __name__ == "__main__":
    df_raw = cargar_datos_compras()
    df_analizado = detectar_sobreprecios(df_raw)
    generar_dashboard(df_analizado)