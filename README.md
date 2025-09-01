# 🚀 Metamorph Trading Bot

Bot automatizado para trading de criptomoedas na Binance Spot baseado em sinais de grupo do Telegram.

**⚠️ AVISO**: Trading de criptomoedas envolve riscos. Nunca invista mais do que pode perder.

## 📋 Funcionalidades

- ✅ **Monitoramento automático** de grupos do Telegram
- ✅ **Execução automática** de ordens na Binance Spot
- ✅ **Ordens OCO** (Take Profit + Stop Loss)
- ✅ **Percentual adaptativo** baseado no tamanho da conta
- ✅ **Interface gráfica** profissional
- ✅ **Registro para IR** (Receita Federal do Brasil)
- ✅ **Modo simulação** para testes
- ✅ **Monitor de sinais** em tempo real

## 🛠️ Instalação

### Windows

#### 1. Instalar Python
- Baixe Python 3.8+ em [python.org](https://python.org)
- ✅ Marque "Add Python to PATH" durante instalação

#### 2. Baixar o Bot
```cmd
git clone https://github.com/seu-usuario/metamorph-trading-bot.git
cd metamorph-trading-bot
```

#### 3. Instalar Dependências
```cmd
pip install -r requirements.txt
```

#### 4. Configurar .env
```cmd
copy .envexample .env
notepad .env
```

### Linux

#### 1. Instalar Python e Git
```bash
sudo apt update
sudo apt install python3 python3-pip git
```

#### 2. Baixar o Bot
```bash
git clone https://github.com/GinetonSantos/metamorph-trading-bot.git
cd metamorph-trading-bot
```

#### 3. Instalar Dependências
```bash
pip3 install -r requirements.txt
```

#### 4. Configurar .env
```bash
cp .envexample .env
nano .env
```

## ⚙️ Configuração

### 1. Telegram API
1. Acesse [my.telegram.org/apps](https://my.telegram.org/apps)
2. Crie uma aplicação
3. Anote `API_ID` e `API_HASH`

### 2. Binance API
1. Acesse [binance.com](https://binance.com) → Perfil → API Management
2. Crie nova API Key
3. **Permissões necessárias:**
   - ✅ Enable Spot & Margin Trading
   - ❌ Enable Futures (desabilitar)
   - ❌ Enable Withdrawals (NUNCA habilitar)
4. Configure **restrição de IP** (recomendado)

### 3. Arquivo .env
```env
# TELEGRAM CONFIG
TELEGRAM_API_ID=seu_api_id
TELEGRAM_API_HASH=seu_api_hash
TELEGRAM_PHONE=+5511999999999
TELEGRAM_GROUP=@seu_grupo_de_sinais

# BINANCE CONFIG
BINANCE_API_KEY=sua_api_key
BINANCE_API_SECRET=sua_secret_key

# SIMULAÇÃO (True = teste, False = real)
SIMULATION_MODE=True
```

## 🚀 Execução

### Interface Gráfica (Recomendado)
<img width="1364" height="639" alt="image" src="https://github.com/user-attachments/assets/dbb85646-b511-46e5-a17d-06e56dbd24bc" />

#### Windows (Sem Console):
```cmd
# Método 1: Duplo clique no arquivo
Metamorph_Bot.bat

# Método 2: Via PowerShell
pythonw start_gui_improved.pyw

# Método 3: Tradicional (com console)
python start_gui_improved.py
```

#### Linux:
```bash
python3 start_gui_improved.py
```

### Modo Console

#### Windows:
```cmd
python main.py
```

#### Linux:
```bash
python3 main.py
```

## 🖥️ Interface Gráfica

### Controles Principais
- **Iniciar Bot**: Inicia monitoramento (só disponível quando parado)
- **Parar Bot**: Para execução (só disponível quando rodando)
- **Atualizar Saldos**: Refresh manual dos saldos

### Monitor de Sinais
- **Último Sinal**: Mostra par da última operação
- **Status**: Estado atual (sucesso/erro/aguardando)

### Saldos da Conta
- **Conversão USD**: Valores em dólar americano
- **Saldo Bloqueado**: Mostra ordens ativas (0 = sem ordens)

### Botões de Ação
- **📊 Ver Logs**: Abre janela com logs detalhados
- **📈 Relatório IR**: Resumo mensal para declaração
- **💾 Exportar Operações**: Arquivo CSV para contabilidade

## 💰 Sistema de Percentuais

O bot adapta automaticamente o percentual de investimento:

| Saldo da Conta | Categoria | Percentual | Justificativa |
|----------------|-----------|------------|---------------|
| ≤ 50 USDT | PEQUENA | 85% | Maximizar oportunidades |
| 51-200 USDT | MÉDIA | 65% | Equilibrar risco/retorno |
| > 200 USDT | GRANDE | 50% | Conservador e seguro |

## 📊 Declaração de IR

### Arquivo Gerado
- **operacoes_ir.csv**: Todas as operações registradas
- **Campos**: Data, Tipo, Par, Quantidade, Preços, Taxas, Valores
- **Compatível** com legislação brasileira

### Relatório Mensal
- Acesse via botão "📈 Relatório IR"
- Resumo de compras, vendas e taxas
- Cálculo automático de resultado

## 🔒 Segurança

### ⚠️ IMPORTANTE
- **NUNCA** habilite withdrawals na API
- **SEMPRE** use restrição de IP
- **TESTE** primeiro em modo simulação
- **MONITORE** as primeiras operações

### Modo Simulação
```env
SIMULATION_MODE=True
```
- Saldo fictício de 1000 USDT
- Todas as validações funcionam
- Nenhuma ordem real é enviada
- Logs completos para análise

## 🐛 Solução de Problemas

### Erro de Encoding (Windows)
```
UnicodeEncodeError: 'charmap' codec can't encode
```
**Solução**: Arquivo `logger.py` já corrigido com `encoding="utf-8"`

### Erro de Parsing
```
'NoneType' object has no attribute 'group'
```
**Causa**: Mensagem não segue formato esperado
**Solução**: Bot ignora automaticamente

### Saldo Insuficiente
```
Valor disponível: 4.36 USDT | Mínimo necessário: 5.00 USDT
```
**Solução**: Depositar mais USDT ou aguardar par com menor mínimo

### API Key Inválida
```
API-key format invalid
```
**Solução**: Verificar chaves no arquivo `.env`

## 📁 Estrutura de Arquivos

```
metamorph-bot/
├── main.py                 # Entrada principal
├── start_gui_improved.py   # Interface gráfica
├── binance_handler.py      # Lógica da Binance
├── telegram_handler.py     # Cliente Telegram
├── tax_reporter.py         # Sistema de IR
├── signal_monitor.py       # Comunicação GUI
├── logger.py              # Sistema de logs
├── gui_improved.py        # Interface melhorada
├── requirements.txt       # Dependências
├── .env                   # Configurações (criar)
├── .envexample           # Exemplo de configuração
├── trading_bot.log       # Logs do sistema
└── operacoes_ir.csv      # Registro para IR
```

## 📞 Suporte

### Logs Importantes
- **trading_bot.log**: Logs completos do sistema
- **Console**: Saída em tempo real
- **GUI Logs**: Visualização na interface

### 🔧 Personalização de Sinais

O bot usa **expressões regulares (regex)** para capturar informações dos sinais. Para adaptar a diferentes formatos de grupo, edite o arquivo `telegram_handler.py`:

#### Padrões Atuais (linhas 32-37):
```python
pair = re.search(r"#(\w+USDT)", msg).group(1)           # Par: #BTCUSDT
buy_price = float(re.search(r"Compra: ([0-9.]+)", msg).group(1))  # Preço
targets = re.findall(r"Alvo \d+: ([0-9.]+)", msg)      # Alvos
stop = float(re.search(r"StopLoss: ([0-9.]+)", msg).group(1))    # Stop
signal_id = re.search(r"ID: (#[A-Za-z0-9]+)", msg).group(1)     # ID
```

#### Exemplos de Personalização:

**Para sinais em inglês:**
```python
buy_price = float(re.search(r"Buy: ([0-9.]+)", msg).group(1))
targets = re.findall(r"Target \d+: ([0-9.]+)", msg)
stop = float(re.search(r"Stop: ([0-9.]+)", msg).group(1))
```

**Para formato diferente de alvos:**
```python
# Se alvos estão como "TP1: 0.8461"
targets = re.findall(r"TP\d+: ([0-9.]+)", msg)

# Se alvos estão como "🎯 0.8461"
targets = re.findall(r"🎯 ([0-9.]+)", msg)
```

**Para diferentes identificadores:**
```python
# Se usa "Signal ID: 123"
signal_id = re.search(r"Signal ID: ([A-Za-z0-9]+)", msg).group(1)

# Se usa apenas números
signal_id = re.search(r"ID: (\d+)", msg).group(1)
```

#### 📝 Como Testar:
1. Ative modo simulação: `SIMULATION_MODE=True`
2. Monitore os logs para ver se captura corretamente
3. Ajuste os regex conforme necessário
4. Teste com sinais reais do seu grupo

## 📄 Licença

Este projeto é fornecido "como está" para fins educacionais. Use por sua própria conta e risco.

**⚠️ AVISO**: Trading de criptomoedas envolve riscos. Nunca invista mais do que pode perder.
