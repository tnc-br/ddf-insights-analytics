"""
Script simplificado para testar localmente sem dependências do Google Cloud
"""

import numpy as np
from typing import Sequence

# ============================================================================
# DADOS DE TESTE
# ============================================================================

sample_test_1 = {
    "sample_name": "Teste Local 1",
    "lat": -13.0845,
    "lon": -53.3795,
    "d18O_cel": [23.5, 24.1, 23.8],
    "species": "Hymenaea courbaril"
}

sample_test_2 = {
    "sample_name": "Teste Local 2 - Inválido",
    "lat": -10.5,
    "lon": -55.3,
    "d18O_cel": [23.5],  # Apenas 1 medição - INVÁLIDO
}

sample_test_3 = {
    "sample_name": "Teste Local 3 - Sem dados",
    "lat": -10.5,
    "lon": -55.3,
    "d18O_cel": None,  # Sem medições - INVÁLIDO
}

# ============================================================================
# FUNÇÕES DE VALIDAÇÃO (SIMPLIFICADAS)
# ============================================================================

def validate_measurements(measurements, element_name):
    """
    Valida se as medições são válidas
    Similar ao que o isinstance faz no código original
    """
    print(f"\n{'='*60}")
    print(f"Validando medições de {element_name}")
    print(f"{'='*60}")
    
    print(f"Valor recebido: {measurements}")
    print(f"Tipo: {type(measurements)}")
    
    # Verificação 1: É uma Sequence?
    is_sequence = isinstance(measurements, Sequence)
    print(f"É uma Sequence? {is_sequence}")
    
    if not is_sequence:
        print("❌ FALHOU: Não é uma sequência (lista, tupla, etc.)")
        return False
    
    # Verificação 2: Tem pelo menos 2 elementos?
    has_min_length = len(measurements) >= 2
    print(f"Tem >= 2 medições? {has_min_length} (quantidade: {len(measurements)})")
    
    if not has_min_length:
        print("❌ FALHOU: Precisa de pelo menos 2 medições")
        return False
    
    print("✅ PASSOU: Medições válidas!")
    return True

def validate_coordinates(lat, lon):
    """Valida coordenadas"""
    print(f"\n{'='*60}")
    print(f"Validando coordenadas")
    print(f"{'='*60}")
    
    print(f"Latitude: {lat} (tipo: {type(lat)})")
    print(f"Longitude: {lon} (tipo: {type(lon)})")
    
    try:
        lat_float = float(lat)
        lon_float = float(lon)
        print(f"✅ Coordenadas convertidas para float: ({lat_float}, {lon_float})")
        
        # Validar ranges
        if -90 <= lat_float <= 90 and -180 <= lon_float <= 180:
            print("✅ Coordenadas dentro do range válido")
            return True
        else:
            print("❌ Coordenadas fora do range válido")
            return False
            
    except Exception as e:
        print(f"❌ ERRO ao converter coordenadas: {e}")
        return False

def calculate_statistics(measurements):
    """Calcula estatísticas básicas das medições"""
    print(f"\n{'='*60}")
    print(f"Calculando estatísticas")
    print(f"{'='*60}")
    
    measurements_array = np.array(measurements, dtype=float)
    
    mean = np.mean(measurements_array)
    std = np.std(measurements_array)
    variance = std ** 2
    
    print(f"Medições: {measurements}")
    print(f"Média: {mean:.4f}")
    print(f"Desvio Padrão: {std:.4f}")
    print(f"Variância: {variance:.4f}")
    print(f"Quantidade: {len(measurements)}")
    
    return {
        'mean': mean,
        'std': std,
        'variance': variance,
        'count': len(measurements)
    }

def test_sample(sample):
    """
    Testa uma sample completa
    Simula o que fraud_detection_process_sample faz
    """
    print("\n" + "="*80)
    print(f"TESTANDO: {sample.get('sample_name', 'Sample sem nome')}")
    print("="*80)
    
    # 1. Validar coordenadas
    if not validate_coordinates(sample.get('lat'), sample.get('lon')):
        print("\n❌ TESTE FALHOU: Coordenadas inválidas")
        return False
    
    # 2. Validar medições de oxigênio
    d18O_cel = sample.get('d18O_cel')
    if not validate_measurements(d18O_cel, "Oxigênio-18"):
        print("\n❌ TESTE FALHOU: Medições de O-18 inválidas")
        print("⚠️  Função retornaria a sample sem processar")
        return False
    
    # 3. Calcular estatísticas
    stats = calculate_statistics(d18O_cel)
    
    print("\n" + "="*80)
    print("✅ TESTE PASSOU: Sample é válida e seria processada!")
    print("="*80)
    print(f"Estatísticas calculadas:")
    print(f"  - Média: {stats['mean']:.4f}")
    print(f"  - Variância: {stats['variance']:.4f}")
    print(f"  - Quantidade de medições: {stats['count']}")
    
    return True

# ============================================================================
# TESTES INTERATIVOS
# ============================================================================

def run_all_tests():
    """Executa todos os testes"""
    print("\n" + "🔬"*40)
    print("TESTES LOCAIS - FRAUD DETECTION")
    print("🔬"*40)
    
    samples = [sample_test_1, sample_test_2, sample_test_3]
    results = []
    
    for i, sample in enumerate(samples, 1):
        result = test_sample(sample)
        results.append((sample.get('sample_name'), result))
        
        if i < len(samples):
            input("\n⏸️  Pressione ENTER para próximo teste...")
    
    # Resumo
    print("\n" + "="*80)
    print("RESUMO DOS TESTES")
    print("="*80)
    passed = sum(1 for _, r in results if r)
    failed = len(results) - passed
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed} passou, {failed} falhou")

def test_isinstance_behavior():
    """Demonstra o comportamento do isinstance"""
    print("\n" + "="*80)
    print("DEMONSTRAÇÃO: Como isinstance funciona")
    print("="*80)
    
    test_values = [
        ([1, 2, 3], "Lista com 3 elementos"),
        ((1, 2), "Tupla com 2 elementos"),
        ([1], "Lista com 1 elemento"),
        ([], "Lista vazia"),
        (None, "None"),
        (123, "Número inteiro"),
        ("1,2,3", "String"),
        ({"a": 1}, "Dicionário"),
    ]
    
    for value, description in test_values:
        print(f"\n{'-'*60}")
        print(f"Testando: {description}")
        print(f"Valor: {value}")
        print(f"Tipo: {type(value)}")
        
        is_sequence = isinstance(value, Sequence)
        print(f"isinstance(value, Sequence): {is_sequence}")
        
        if is_sequence:
            try:
                length = len(value)
                has_min = length >= 2
                print(f"len(value): {length}")
                print(f"len >= 2: {has_min}")
                
                if is_sequence and has_min:
                    print("✅ Passaria na validação")
                else:
                    print("❌ Falharia na validação (menos de 2 elementos)")
            except:
                print("❌ Falharia ao tentar len()")
        else:
            print("❌ Falharia na validação (não é Sequence)")

# ============================================================================
# MENU INTERATIVO
# ============================================================================

def show_menu():
    """Mostra menu de opções"""
    print("\n" + "="*80)
    print("MENU DE TESTES LOCAIS")
    print("="*80)
    print("1. Executar todos os testes")
    print("2. Testar sample específica")
    print("3. Demonstrar comportamento do isinstance")
    print("4. Ver estrutura das samples de teste")
    print("5. Sair")
    print("="*80)

def main():
    """Função principal com menu interativo"""
    print("\n" + "🧪"*40)
    print("TESTE LOCAL DE FRAUD DETECTION - MODO SIMPLIFICADO")
    print("🧪"*40)
    print("\nEste script testa as validações SEM precisar do Google Earth Engine")
    
    while True:
        show_menu()
        try:
            choice = input("\nEscolha uma opção (1-5): ").strip()
            
            if choice == '1':
                run_all_tests()
            
            elif choice == '2':
                print("\n" + "="*80)
                print("SAMPLES DISPONÍVEIS:")
                print("="*80)
                print("1. Sample válida (3 medições)")
                print("2. Sample inválida (1 medição)")
                print("3. Sample inválida (sem medições)")
                
                sample_choice = input("\nEscolha uma sample (1-3): ").strip()
                samples = [sample_test_1, sample_test_2, sample_test_3]
                
                if sample_choice in ['1', '2', '3']:
                    test_sample(samples[int(sample_choice) - 1])
                else:
                    print("❌ Opção inválida")
            
            elif choice == '3':
                test_isinstance_behavior()
            
            elif choice == '4':
                print("\n" + "="*80)
                print("ESTRUTURA DAS SAMPLES DE TESTE")
                print("="*80)
                print("\nSample 1 (Válida):")
                print(sample_test_1)
                print("\nSample 2 (Inválida - 1 medição):")
                print(sample_test_2)
                print("\nSample 3 (Inválida - None):")
                print(sample_test_3)
            
            elif choice == '5':
                print("\n✅ Encerrando testes. Até logo!")
                break
            
            else:
                print("❌ Opção inválida. Escolha 1-5.")
        
        except KeyboardInterrupt:
            print("\n\n✅ Encerrando testes. Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            import traceback
            traceback.print_exc()

# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == "__main__":
    main()
