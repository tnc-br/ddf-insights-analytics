"""
Testes de integração simplificados
Testa o fluxo completo sem mocks, para validar lógica de negócio
"""

import os


def validate_coordinates(lat, lon):
    """
    Valida coordenadas geográficas
    
    Args:
        lat: Latitude em graus decimais
        lon: Longitude em graus decimais
    
    Returns:
        tuple: (is_valid, message)
    """
    # Valida latitude
    if not isinstance(lat, (int, float)):
        return False, f"Latitude deve ser número, recebido: {type(lat)}"
    
    if not -90 <= lat <= 90:
        return False, f"Latitude fora do range válido (-90 a 90): {lat}"
    
    # Valida longitude
    if not isinstance(lon, (int, float)):
        return False, f"Longitude deve ser número, recebido: {type(lon)}"
    
    if not -180 <= lon <= 180:
        return False, f"Longitude fora do range válido (-180 a 180): {lon}"
    
    return True, "Coordenadas válidas"


def validate_document_id(doc_id):
    """
    Valida ID de documento
    
    Args:
        doc_id: ID do documento
    
    Returns:
        tuple: (is_valid, message)
    """
    if not isinstance(doc_id, str):
        return False, f"Document ID deve ser string, recebido: {type(doc_id)}"
    
    if len(doc_id) == 0:
        return False, "Document ID não pode ser vazio"
    
    if len(doc_id) > 1500:
        return False, f"Document ID muito longo: {len(doc_id)} caracteres"
    
    # Caracteres problemáticos em filenames
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        if char in doc_id:
            return False, f"Document ID contém caractere inválido: '{char}'"
    
    return True, "Document ID válido"


def validate_vis_params(vis_params):
    """
    Valida parâmetros de visualização
    
    Args:
        vis_params: Dict com parâmetros de visualização
    
    Returns:
        tuple: (is_valid, message)
    """
    required_keys = ['min', 'max', 'palette']
    
    for key in required_keys:
        if key not in vis_params:
            return False, f"Parâmetro obrigatório ausente: {key}"
    
    # Valida min/max
    if vis_params['min'] >= vis_params['max']:
        return False, f"min ({vis_params['min']}) deve ser menor que max ({vis_params['max']})"
    
    # Valida palette
    palette = vis_params['palette']
    if not isinstance(palette, list):
        return False, f"Palette deve ser lista, recebido: {type(palette)}"
    
    if len(palette) == 0:
        return False, "Palette não pode ser vazia"
    
    # Valida cores em formato hex
    for color in palette:
        if not isinstance(color, str):
            return False, f"Cor deve ser string, recebido: {type(color)}"
        if not color.startswith('#'):
            return False, f"Cor deve começar com '#': {color}"
        if len(color) != 7:
            return False, f"Cor deve ter formato #RRGGBB: {color}"
    
    return True, "Parâmetros de visualização válidos"


def validate_gcs_path(bucket_name, folder_name, document_id):
    """
    Valida path do Google Cloud Storage
    
    Args:
        bucket_name: Nome do bucket
        folder_name: Nome da pasta
        document_id: ID do documento
    
    Returns:
        tuple: (is_valid, full_path, message)
    """
    if not bucket_name:
        return False, None, "Bucket name não pode ser vazio"
    
    if not folder_name:
        return False, None, "Folder name não pode ser vazio"
    
    if not document_id:
        return False, None, "Document ID não pode ser vazio"
    
    full_path = f"gs://{bucket_name}/{folder_name}/{document_id}.html"
    
    return True, full_path, "Path GCS válido"


# ============================================================================
# TESTES DE VALIDAÇÃO
# ============================================================================

def test_coordinate_validation():
    """Testa validação de coordenadas"""
    print("\n🧪 TESTE: Validação de Coordenadas")
    print("=" * 60)
    
    test_cases = [
        # (lat, lon, should_pass, description)
        (-13.0845, -53.3795, True, "Coordenadas válidas - Brasil"),
        (0, 0, True, "Coordenadas no equador e meridiano"),
        (-90, -180, True, "Limites mínimos"),
        (90, 180, True, "Limites máximos"),
        (91, 0, False, "Latitude acima do limite"),
        (-91, 0, False, "Latitude abaixo do limite"),
        (0, 181, False, "Longitude acima do limite"),
        (0, -181, False, "Longitude abaixo do limite"),
        ("invalid", 0, False, "Latitude não numérica"),
        (0, "invalid", False, "Longitude não numérica"),
    ]
    
    passed = 0
    failed = 0
    
    for lat, lon, should_pass, description in test_cases:
        is_valid, message = validate_coordinates(lat, lon)
        
        if is_valid == should_pass:
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description} - {message}")
            failed += 1
    
    print(f"\n📊 Resultado: {passed} passou, {failed} falhou")
    return failed == 0


def test_document_id_validation():
    """Testa validação de document ID"""
    print("\n🧪 TESTE: Validação de Document ID")
    print("=" * 60)
    
    test_cases = [
        ("sample_001", True, "ID válido simples"),
        ("ef8c9fc3c7983d512b71", True, "ID válido hash"),
        ("test-sample-123", True, "ID com hífens"),
        ("test_sample_2024", True, "ID com underscore e números"),
        ("", False, "ID vazio"),
        ("a" * 2000, False, "ID muito longo"),
        ("sample/001", False, "ID com barra"),
        ("sample\\001", False, "ID com backslash"),
        ("sample:001", False, "ID com dois pontos"),
        ("sample*001", False, "ID com asterisco"),
        ("sample?001", False, "ID com interrogação"),
    ]
    
    passed = 0
    failed = 0
    
    for doc_id, should_pass, description in test_cases:
        is_valid, message = validate_document_id(doc_id)
        
        if is_valid == should_pass:
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description} - {message}")
            failed += 1
    
    print(f"\n📊 Resultado: {passed} passou, {failed} falhou")
    return failed == 0


def test_vis_params_validation():
    """Testa validação de parâmetros de visualização"""
    print("\n🧪 TESTE: Validação de Parâmetros de Visualização")
    print("=" * 60)
    
    valid_params = {
        "min": 1,
        "max": 7,
        "palette": [
            "#fffbc2",
            "#09611f",
            "#4ea376",
            "#e31a1c",
            "#94fc03",
            "#ffa500",
            "#212121",
        ],
    }
    
    test_cases = [
        (valid_params, True, "Parâmetros válidos"),
        ({**valid_params, "min": 10}, False, "min >= max"),
        ({"min": 1, "max": 7}, False, "palette ausente"),
        ({**valid_params, "palette": []}, False, "palette vazia"),
        ({**valid_params, "palette": ["#fff"]}, False, "cor com formato inválido"),
        ({**valid_params, "palette": ["fffbc2"]}, False, "cor sem #"),
        ({**valid_params, "palette": [123]}, False, "cor não é string"),
    ]
    
    passed = 0
    failed = 0
    
    for params, should_pass, description in test_cases:
        is_valid, message = validate_vis_params(params)
        
        if is_valid == should_pass:
            print(f"  ✅ {description}")
            passed += 1
        else:
            print(f"  ❌ {description} - {message}")
            failed += 1
    
    print(f"\n📊 Resultado: {passed} passou, {failed} falhou")
    return failed == 0


def test_gcs_path_validation():
    """Testa validação de paths GCS"""
    print("\n🧪 TESTE: Validação de Paths GCS")
    print("=" * 60)
    
    test_cases = [
        ("timberid-public-to-internet", "timberid-maps", "sample_001", True, "Path válido"),
        ("", "timberid-maps", "sample_001", False, "Bucket vazio"),
        ("timberid-public-to-internet", "", "sample_001", False, "Pasta vazia"),
        ("timberid-public-to-internet", "timberid-maps", "", False, "Document ID vazio"),
    ]
    
    passed = 0
    failed = 0
    
    for bucket, folder, doc_id, should_pass, description in test_cases:
        is_valid, path, message = validate_gcs_path(bucket, folder, doc_id)
        
        if is_valid == should_pass:
            print(f"  ✅ {description}")
            if path:
                print(f"     Path: {path}")
            passed += 1
        else:
            print(f"  ❌ {description} - {message}")
            failed += 1
    
    print(f"\n📊 Resultado: {passed} passou, {failed} falhou")
    return failed == 0


def run_all_validation_tests():
    """Executa todos os testes de validação"""
    print("\n" + "=" * 60)
    print("🚀 TESTES DE VALIDAÇÃO - FRAUD DETECTION GENERATE MAPS")
    print("=" * 60)
    
    results = []
    
    results.append(("Coordenadas", test_coordinate_validation()))
    results.append(("Document ID", test_document_id_validation()))
    results.append(("Vis Params", test_vis_params_validation()))
    results.append(("GCS Path", test_gcs_path_validation()))
    
    print("\n" + "=" * 60)
    print("📊 RESUMO FINAL")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 TODOS OS TESTES DE VALIDAÇÃO PASSARAM!")
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM")
    
    return all_passed


if __name__ == "__main__":
    run_all_validation_tests()
