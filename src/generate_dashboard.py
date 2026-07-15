import os
import json
import time
from datetime import datetime
import pytz

def generate_dashboard():
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    
    # Load live buses
    buses_file = "data/processed/live_buses.json"
    active_buses = 0
    buses_json_str = "[]"
    if os.path.exists(buses_file):
        try:
            with open(buses_file, "r", encoding="utf-8") as f:
                buses = json.load(f)
                active_buses = len(buses)
                buses_json_str = json.dumps(buses)
        except Exception:
            pass

    # Load routes
    routes_file = "data/raw/routes.json"
    total_routes = 0
    routes_json_str = "[]"
    if os.path.exists(routes_file):
        try:
            with open(routes_file, "r", encoding="utf-8") as f:
                routes = json.load(f)
                total_routes = len(routes)
                routes_json_str = json.dumps(routes)
        except Exception:
            pass

    # Generate timestamp
    tz = pytz.timezone('Europe/Istanbul')
    now = datetime.now(tz)
    update_time = now.strftime("%d %B %Y, %H:%M:%S")

    html_content = f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kocaeli Transit GTFS Pipeline</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0f172a;
            --text-color: #f8fafc;
            --accent-color: #3b82f6;
            --card-bg: rgba(30, 41, 59, 0.7);
            --card-border: rgba(255, 255, 255, 0.1);
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle at top left, #1e1b4b, #0f172a 60%);
            padding: 20px;
        }}
        
        .container {{
            max-width: 800px;
            width: 100%;
            backdrop-filter: blur(16px);
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            text-align: center;
            animation: fadeIn 0.8s ease-out;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        h1 {{
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 10px;
            background: linear-gradient(to right, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        p.subtitle {{
            color: #94a3b8;
            font-size: 1.1rem;
            margin-bottom: 40px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 24px;
            cursor: pointer;
            transition: transform 0.3s ease, background 0.3s ease;
            position: relative;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(255,255,255,0.3);
        }}
        
        .stat-card::after {{
            content: 'Detayları Gör →';
            display: block;
            margin-top: 10px;
            font-size: 0.8rem;
            color: var(--accent-color);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .stat-card:hover::after {{
            opacity: 1;
        }}
        
        .stat-value {{
            font-size: 3rem;
            font-weight: 800;
            color: #fff;
            margin-bottom: 8px;
        }}
        
        .stat-label {{
            color: #94a3b8;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
        }}
        
        .download-section {{
            display: flex;
            gap: 20px;
            justify-content: center;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }}
        
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 10px;
            background: var(--accent-color);
            color: white;
            text-decoration: none;
            padding: 14px 28px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .btn:hover {{
            background: #2563eb;
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);
        }}
        
        .btn-secondary {{
            background: rgba(255, 255, 255, 0.1);
        }}
        
        .btn-secondary:hover {{
            background: rgba(255, 255, 255, 0.15);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
        }}
        
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--card-border);
            color: #64748b;
            font-size: 0.9rem;
        }}
        
        .pulse {{
            display: inline-block;
            width: 10px;
            height: 10px;
            background-color: #22c55e;
            border-radius: 50%;
            margin-right: 8px;
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }}
            70% {{ box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }}
            100% {{ box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }}
        }}

        /* Modal Styles */
        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(8px);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            padding: 20px;
            animation: fadeIn 0.3s ease-out;
        }}

        .modal-content {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            width: 100%;
            max-width: 700px;
            max-height: 80vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
        }}

        .modal-header {{
            padding: 20px 30px;
            border-bottom: 1px solid var(--card-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .modal-header h2 {{
            font-size: 1.5rem;
            margin: 0;
        }}

        .close-btn {{
            background: none;
            border: none;
            color: #94a3b8;
            font-size: 1.5rem;
            cursor: pointer;
            transition: color 0.3s;
        }}

        .close-btn:hover {{
            color: #fff;
        }}

        .modal-body {{
            padding: 20px 30px;
            overflow-y: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}

        th, td {{
            padding: 12px 15px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}

        th {{
            background: rgba(255,255,255,0.05);
            color: #94a3b8;
            font-weight: 600;
            position: sticky;
            top: 0;
            backdrop-filter: blur(10px);
        }}

        tr:hover td {{
            background: rgba(255,255,255,0.02);
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Kocaeli Transit GTFS</h1>
        <p class="subtitle">Otomatik GTFS & GTFS-Realtime Veri Boru Hattı</p>
        
        <div class="stats-grid">
            <div class="stat-card" onclick="openModal('bus')">
                <div class="stat-value">{active_buses}</div>
                <div class="stat-label">Aktif Otobüs (Canlı)</div>
            </div>
            <div class="stat-card" onclick="openModal('route')">
                <div class="stat-value">{total_routes}</div>
                <div class="stat-label">Kayıtlı Hat</div>
            </div>
        </div>
        
        <div class="download-section">
            <a href="gtfs/vehicle_positions.pb" class="btn">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                Canlı Veri İndir (RT)
            </a>
            <a href="gtfs/gtfs.zip" class="btn btn-secondary">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                Statik Veri İndir (ZIP)
            </a>
        </div>
        
        <div class="footer">
            <span class="pulse"></span>
            Son Güncelleme: <strong>{update_time}</strong> (Sistem her 5 dakikada bir otomatik güncellenir)
        </div>
    </div>

    <!-- Modal -->
    <div class="modal-overlay" id="dataModal" onclick="closeModal(event)">
        <div class="modal-content" onclick="event.stopPropagation()">
            <div class="modal-header">
                <h2 id="modalTitle">Detaylar</h2>
                <button class="close-btn" onclick="closeModal(event)">&times;</button>
            </div>
            <div class="modal-body" id="modalBody">
                <!-- Table injects here -->
            </div>
        </div>
    </div>

    <script>
        const liveBuses = {buses_json_str};
        const allRoutes = {routes_json_str};

        function openModal(type) {{
            const modal = document.getElementById('dataModal');
            const title = document.getElementById('modalTitle');
            const body = document.getElementById('modalBody');
            
            modal.style.display = 'flex';
            
            let html = '<table>';
            
            if (type === 'bus') {{
                title.innerText = 'Aktif Otobüsler (Canlı)';
                html += `<thead><tr><th>Hat Kodu</th><th>Plaka</th><th>Hız (km/h)</th></tr></thead><tbody>`;
                liveBuses.forEach(bus => {{
                    html += `<tr>
                        <td><strong>${{bus.route_code || '-'}}</strong></td>
                        <td>${{bus.plate || '-'}}</td>
                        <td>${{bus.extra || '0'}}</td>
                    </tr>`;
                }});
            }} else if (type === 'route') {{
                title.innerText = 'Kayıtlı Hatlar';
                html += `<thead><tr><th>Hat Kodu</th><th>Hat Adı</th></tr></thead><tbody>`;
                allRoutes.forEach(route => {{
                    html += `<tr>
                        <td><strong>${{route.route_code || '-'}}</strong></td>
                        <td>${{route.route_name || '-'}}</td>
                    </tr>`;
                }});
            }}
            
            html += '</tbody></table>';
            
            if ((type === 'bus' && liveBuses.length === 0) || (type === 'route' && allRoutes.length === 0)) {{
                html = '<p style="text-align: center; color: #94a3b8;">Şu anda veri bulunmamaktadır.</p>';
            }}
            
            body.innerHTML = html;
        }}

        function closeModal(e) {{
            if (e) e.preventDefault();
            document.getElementById('dataModal').style.display = 'none';
        }}
    </script>
</body>
</html>"""

    with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"Dashboard HTML generated successfully at {output_dir}/index.html")

if __name__ == "__main__":
    generate_dashboard()

