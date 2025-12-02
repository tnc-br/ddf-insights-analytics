"""
Mock do geemap para testes locais
Simula a criação de mapas sem precisar do Earth Engine real
"""

class MockMap:
    """Mock de geemap.Map"""
    
    def __init__(self):
        self.layers = []
        self.center = None
        self.zoom = None
        print("  🗺️  Mapa geemap criado (MOCK)")
    
    def addLayer(self, ee_object, vis_params, name):
        """Adiciona camada ao mapa"""
        layer = {
            "name": name,
            "vis_params": vis_params,
            "ee_object": ee_object
        }
        self.layers.append(layer)
        print(f"  ➕ Camada adicionada: '{name}' (total: {len(self.layers)} camadas)")
    
    def remove_ee_layer(self, name):
        """Remove camada do mapa"""
        original_count = len(self.layers)
        self.layers = [layer for layer in self.layers if layer["name"] != name]
        removed = original_count - len(self.layers)
        if removed > 0:
            print(f"  ➖ Camada removida: '{name}'")
        else:
            print(f"  ⚠️  Camada não encontrada: '{name}'")
    
    def centerObject(self, ee_object, zoom):
        """Centraliza mapa em objeto"""
        self.center = ee_object
        self.zoom = zoom
        print(f"  🎯 Mapa centralizado com zoom {zoom}")
    
    def to_html(self, filename, title, width, height):
        """Gera arquivo HTML do mapa"""
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ margin: 0; padding: 20px; font-family: Arial, sans-serif; }}
        .map-container {{ width: {width}; height: {height}; border: 2px solid #ccc; }}
        .info {{ padding: 10px; background: #f0f0f0; margin-bottom: 10px; }}
    </style>
</head>
<body>
    <div class="info">
        <h2>{title}</h2>
        <p><strong>MOCK MAP</strong> - Este é um mapa simulado para testes locais</p>
        <p>Camadas: {len(self.layers)}</p>
        <ul>
            {''.join([f'<li>{layer["name"]}</li>' for layer in self.layers])}
        </ul>
    </div>
    <div class="map-container">
        <p style="text-align: center; padding-top: 100px;">
            🗺️ Mapa Interativo (Mock)<br>
            Zoom: {self.zoom}
        </p>
    </div>
</body>
</html>"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"  💾 HTML gerado: {filename}")
        return filename


class MockGeeMap:
    """Mock do módulo geemap"""
    
    @staticmethod
    def Map():
        return MockMap()
