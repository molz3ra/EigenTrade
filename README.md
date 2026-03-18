# 🤖 Quant Trading AI & Dashboard

Um sistema de trading quantitativo de ponta a ponta construído com Python, Machine Learning e Streamlit.

## 🚀 Arquitetura do Projeto
- **Coleta de Dados:** `ccxt` (Integração direta com a Binance).
- **Engenharia de Recursos:** `pandas_ta` (RSI, Bandas de Bollinger, Médias Móveis).
- **Cérebro (IA):** `XGBoost` otimizado para séries temporais.
- **Backtesting Realista:** `Backtrader` com Position Sizing, Stop Loss e Take Profit reais.
- **Frontend / Dashboard:** `Streamlit` e `Plotly` para visualização de estatísticas e sinais em tempo real.

## 🛠️ Como Rodar Localmente
1. Instale as dependências: `pip install -r requirements.txt`
2. Inicie o Dashboard: `streamlit run dashboard.py`

## 🔜 Próximas Atualizações (Roadmap)
- [ ] Deploy na AWS (EC2/Docker) para operação 24/7.
- [ ] Integração de chaves de API para ordens de compra/venda automáticas.