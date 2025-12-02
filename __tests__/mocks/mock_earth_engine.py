"""
Mock do Google Earth Engine para testes locais
Simula as principais classes e métodos do Earth Engine sem precisar de autenticação
"""

class MockGeometry:
    """Mock de ee.Geometry"""
    
    def __init__(self, coords):
        self.coords = coords
        self.type = "Point"
    
    def buffer(self, distance):
        """Simula criação de buffer"""
        print(f"  📍 Buffer de {distance}m criado ao redor de {self.coords}")
        return MockGeometry(self.coords)
    
    def difference(self, other):
        """Simula diferença entre geometrias"""
        print(f"  🔺 Aplicando diferença entre geometrias")
        return self


class MockPoint:
    """Mock de ee.Geometry.Point"""
    
    def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat
        self.coords = [lon, lat]
        print(f"  📌 Ponto criado: ({lat}, {lon})")
    
    def buffer(self, distance):
        return MockGeometry(self.coords).buffer(distance)


class MockImage:
    """Mock de ee.Image"""
    
    def __init__(self, image_id):
        self.image_id = image_id
        self.selected_band = None
        print(f"  🗺️  Carregando imagem: {image_id}")
    
    def select(self, band):
        """Seleciona banda da imagem"""
        print(f"  🎯 Banda selecionada: {band}")
        self.selected_band = band
        return self
    
    def divide(self, value):
        """Divide valores da imagem"""
        print(f"  ➗ Dividindo por {value}")
        return self
    
    def floor(self):
        """Arredonda valores para baixo"""
        print(f"  ⬇️  Aplicando floor()")
        return self
    
    def mask(self):
        """Retorna máscara da imagem"""
        print(f"  🎭 Obtendo máscara da imagem")
        return self
    
    def geometry(self):
        """Retorna geometria da imagem"""
        print(f"  🌍 Obtendo geometria da imagem")
        return MockGeometry([0, 0])


class MockGeometryClass:
    """Mock de ee.Geometry (classe)"""
    
    @staticmethod
    def Point(lon, lat):
        return MockPoint(lon, lat)


class MockEarthEngine:
    """Mock completo do Earth Engine"""
    
    def __init__(self):
        self.Geometry = MockGeometryClass()
        self.Image = MockImage
        self.initialized = False
    
    def Initialize(self, credentials=None):
        """Simula inicialização do Earth Engine"""
        print("✅ Earth Engine inicializado (MOCK)")
        self.initialized = True


# Instância global do mock
ee_mock = MockEarthEngine()
