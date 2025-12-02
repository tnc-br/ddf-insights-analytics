# 🐍 Comandos úteis - ddf-insights-analytics

## Ativar ambiente virtual Python (timberid-env)

```bash
# A partir de qualquer diretório:
source ~/job/Be220/ddf-insights-analytics/timberid-env/bin/activate

# Ou se já estiver na pasta do projeto:
cd ~/job/Be220/ddf-insights-analytics
source timberid-env/bin/activate
```

## Verificar se ambiente está ativo

```bash
# Ver qual Python está sendo usado
which python3
# Esperado: ~/job/Be220/ddf-insights-analytics/timberid-env/bin/python3

# Verificar variável de ambiente
echo $VIRTUAL_ENV
# Esperado: /home/daniel/job/Be220/ddf-insights-analytics/timberid-env

# Quando ativado, o prompt mostra:
# (timberid-env) daniel@daniel-System-Product-Name:~$
```

## Desativar ambiente virtual

```bash
deactivate
```

## Criar alias (opcional - facilita muito!)

```bash
# Adicionar ao ~/.bashrc
echo "alias timberid='cd ~/job/Be220/ddf-insights-analytics && source timberid-env/bin/activate'" >> ~/.bashrc
source ~/.bashrc

# Agora basta digitar de qualquer lugar:
timberid
```

---

## 📦 Comandos úteis do projeto

### Gerar mapas isotópicos

```bash
# Ativar ambiente primeiro
source ~/job/Be220/ddf-insights-analytics/timberid-env/bin/activate

# Navegar para pasta de mapas
cd ~/job/Be220/ddf-insights-analytics/fraud-detection-generate-maps

# Gerar mapa para documento específico
python run_generate_mapa_auto.py 6ed0ffa36587c49f5b54

# Gerar mapa com valor isotópico manual
python run_generate_mapa_auto.py test_sample -15.2

# Ver ajuda
python run_generate_mapa_auto.py --help
```

### Criar isoscapes de exemplo

```bash
cd ~/job/Be220/ddf-insights-analytics/fraud-detection-generate-maps
python create_example_isoscapes.py
```

### Testar Cloud Function localmente

```bash
cd ~/job/Be220/ddf-insights-analytics/fraud-detection-generate-maps
python firebase_manual_executor.py <document_id>
```
