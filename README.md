# ATENA Framework

**Automated Task Environment for Networked Automation**

Framework de automação em Python para gerenciamento de tarefas de desenvolvimento.

---

## 📁 Estrutura do Projeto

```
project/
├── core/                    # Módulos centrais do framework
│   ├── __init__.py
│   ├── config.py           # Configurações globais
│   └── logger.py           # Sistema de logging
├── modules/                 # Módulos funcionais
│   ├── __init__.py
│   ├── code_analyzer.py    # Análise de código
│   └── doc_fetcher.py      # Consulta de documentação
├── logs/                    # Arquivos de log
│   └── atena.log
├── manager.py              # CLI principal
├── requirements.txt        # Dependências
└── README.md
```

---

## 🚀 Instalação

```bash
# Clone o repositório
git clone <repository-url>
cd project

# Instale as dependências
python manager.py install

# Ou com upgrade
python manager.py install --upgrade
```

---

## 📋 Funcionalidades

### 1. Gerenciamento de Dependências

O `manager.py` permite instalar e gerenciar dependências do projeto.

```bash
# Instalar todas as dependências do requirements.txt
python manager.py install

# Instalar com upgrade
python manager.py install --upgrade

# Instalar pacote específico
python manager.py install --package requests
```

### 2. Execução de Comandos

Execute comandos shell com logging automático.

```bash
python manager.py run "ls -la"
python manager.py run "pytest tests/"
```

### 3. Análise de Código

Analisa arquivos Python e sugere melhorias de código limpo.

```bash
# Analisar diretório atual
python manager.py analyze

# Analisar arquivo específico
python manager.py analyze core/config.py

# Analisar diretório específico
python manager.py analyze modules/
```

**Verificações realizadas:**
- ✅ Funções muito longas (> 50 linhas)
- ✅ Alta complexidade ciclomática (> 10)
- ✅ Muitos parâmetros em funções (> 5)
- ✅ Docstrings ausentes
- ✅ Linhas muito longas (> 120 caracteres)
- ✅ Uso de `except:` genérico
- ✅ Uso de `print()` ao invés de logging
- ✅ Marcadores TODO/FIXME pendentes
- ✅ Classes muito grandes (> 20 métodos)

### 4. Assistente de Documentação

Quando ocorrem erros, o sistema sugere documentação relevante.

```python
from modules.doc_fetcher import DocAssistant

assistant = DocAssistant()
assistant.print_help("ModuleNotFoundError: No module named 'requests'")
```

**Saída:**
```
============================================================
🔍 ATENA ERROR ANALYSIS
============================================================

❌ Error Type: IMPORT
   Message: ModuleNotFoundError: No module named 'requests'

💡 Suggestion:
   Try: pip install requests
   Or check if the module name is spelled correctly.

📚 Documentation:
   Module Import Errors
   🔗 https://docs.python.org/3/tutorial/modules.html
   Guide on Python modules and import system

   Related: pip install, virtual environments, PYTHONPATH
============================================================
```

---

## 🔧 Uso Programático

### DependencyManager

```python
from manager import DependencyManager

dm = DependencyManager()

# Instalar dependências
dm.install_dependencies()

# Instalar pacote específico
dm.install_package("flask")

# Listar pacotes instalados
packages = dm.list_installed()
```

### CommandExecutor

```python
from manager import CommandExecutor

executor = CommandExecutor()

# Executar comando
success, stdout, stderr = executor.run("python --version")
```

### CodeAnalyzer

```python
from modules.code_analyzer import CodeAnalyzer

analyzer = CodeAnalyzer()

# Analisar arquivo
result = analyzer.analyze_file("meu_script.py")

# Analisar diretório
results = analyzer.analyze_path("src/")

# Imprimir relatório
analyzer.print_report(results)
```

### DocAssistant

```python
from modules.doc_fetcher import DocAssistant

assistant = DocAssistant()

# Analisar erro e obter ajuda
result = assistant.analyze_error("TypeError: unsupported operand type(s)")
print(result["suggestion"])
print(result["documentation"]["url"])
```

---

## 📊 Sistema de Logging

Todas as operações são registradas em `logs/atena.log`.

```python
from core.logger import log_operation, log_error

# Registrar operação
log_operation("minha_operacao", "SUCCESS", "Detalhes aqui")

# Registrar erro
try:
    # código
except Exception as e:
    log_error("minha_operacao", e)
```

---

## ⚙️ Configuração

Edite `core/config.py` para personalizar:

```python
# Extensões de código suportadas
CODE_EXTENSIONS = [".py", ".js", ".ts"]

# Limites de análise
MAX_FUNCTION_LENGTH = 50  # linhas
MAX_COMPLEXITY = 10       # complexidade ciclomática

# Nível de log
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
```

---

## 🛠️ Desenvolvimento

### Adicionar novo analisador de linguagem

```python
# Em modules/code_analyzer.py

class JavaScriptAnalyzer:
    def analyze(self, file_path: Path) -> AnalysisResult:
        # Implementar análise
        pass

# Registrar no CodeAnalyzer
self.analyzers[".js"] = JavaScriptAnalyzer()
```

### Adicionar nova fonte de documentação

```python
# Em modules/doc_fetcher.py

DOC_MAPPINGS["nova_lib"] = {
    "base_url": "https://docs.nova-lib.io/",
    "topics": {
        "SomeError": "errors/#some-error",
        "default": "",
    }
}
```

---

## 🐳 Deploy com Docker

### Build local

```bash
# Build da imagem
docker build -t atena-bot .

# Executar container
docker run -p 8080:8080 atena-bot
```

### Deploy no Render

1. Conecte seu repositório ao [Render](https://render.com)
2. Selecione "New Web Service"
3. Escolha "Docker" como ambiente
4. O arquivo `render.yaml` será detectado automaticamente

Ou use o botão de deploy:
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Deploy no Railway

1. Conecte seu repositório ao [Railway](https://railway.app)
2. O arquivo `railway.json` será detectado automaticamente
3. Configure as variáveis de ambiente se necessário

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

### Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `PORT` | Porta do servidor HTTP | `8080` |
| `BOT_NAME` | Nome do bot | `ATENA` |
| `HEALTH_CHECK_INTERVAL` | Intervalo de heartbeat (segundos) | `60` |

---

## 🌐 API Endpoints

O bot expõe uma API HTTP para monitoramento e interação:

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check para load balancers |
| GET | `/status` | Status detalhado do bot |
| GET | `/analyze` | Analisa o projeto atual |
| GET | `/analyze/{path}` | Analisa um caminho específico |
| GET | `/logs` | Últimas 50 linhas de log |
| POST | `/error-help` | Obtém ajuda para um erro |

### Exemplos de uso

```bash
# Health check
curl http://localhost:8080/health

# Status do bot
curl http://localhost:8080/status

# Analisar projeto
curl http://localhost:8080/analyze

# Obter ajuda para erro
curl -X POST http://localhost:8080/error-help \
  -H "Content-Type: application/json" \
  -d '{"error": "ModuleNotFoundError: No module named requests"}'
```

---

## 📝 Roadmap

- [ ] Suporte a análise de JavaScript/TypeScript
- [ ] Integração com APIs de IA para sugestões avançadas
- [ ] Interface web para visualização de relatórios
- [ ] Integração com CI/CD pipelines
- [ ] Suporte a múltiplos idiomas na documentação
- [ ] Webhooks para notificações
- [ ] Integração com Discord/Slack

---

## 📄 Licença

MIT License - Veja o arquivo LICENSE para detalhes.

---

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, abra uma issue ou pull request.

---

*ATENA Framework v1.0.0*
