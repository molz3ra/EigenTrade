# 🧠 SynapseQuant: AI-Driven Trading Intelligence

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Machine Learning](https://img.shields.io/badge/XGBoost-EE4C2C?style=for-the-badge&logo=xgboost&logoColor=white)
![Trading](https://img.shields.io/badge/Backtrader-008000?style=for-the-badge&logo=chartdotjs&logoColor=white)
![Dashboard](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge)

**SynapseQuant** é uma plataforma de negociação quantitativa de ponta a ponta que utiliza Machine Learning para prever movimentos de ativos no mercado de criptomoedas. O sistema integra coleta de dados em tempo real, engenharia de recursos (features), backtesting estatístico rigoroso e uma interface visual de alta performance.

---

## 🏗️ Arquitetura do Sistema

O projeto foi construído seguindo os princípios **S.O.L.I.D.** e **Clean Code**, garantindo modularidade e escalabilidade.

### ⚙️ Engine de Dados (`index.py`)
- **Data Pipeline:** Consumo de dados OHLCV via API da Binance utilizando a biblioteca `CCXT`.
- **Feature Engineering:** Cálculo vetorizado de indicadores técnicos através da `Pandas_TA`.
    - *Features:* RSI (Relative Strength Index), EMA (Exponential Moving Averages), Bollinger Bands (Volatility) e Volume Profiling.
- **Machine Learning Engine:** Implementação do classificador `XGBoost` com validação Out-of-Sample (OOT) e divisão temporal rigorosa para eliminar o *Look-ahead Bias*.

### 📊 Simulador & Backtest
- **Risk Management:** Implementação de *Position Sizing* dinâmico (alocação percentual de capital por trade), Stop Loss e Take Profit paramétricos.
- **Backtrader Logic:** Motor de simulação realista que desconta taxas de corretagem e slippage, fornecendo KPIs reais como ROI, Win Rate e Drawdown Máximo.

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Função |
| :--- | :--- |
| **Python 3.10+** | Linguagem Base |
| **CCXT** | Integração com Exchanges (Binance) |
| **XGBoost** | Algoritmo de Gradient Boosting para Predição |
| **Pandas & NumPy** | Manipulação e Processamento de Dados |
| **Backtrader** | Engine de Backtesting e Simulação |
| **Streamlit** | Interface Web Reativa |
| **Plotly** | Gráficos Financeiros Interativos |

---

## 🚀 Como Executar o Projeto

### 1. Clonar o Repositório
```bash
git clone [https://github.com/SEU_USUARIO/synapse-quant.git](https://github.com/SEU_USUARIO/synapse-quant.git)
cd synapse-quant
2. Configurar o Ambiente
Recomenda-se o uso de um ambiente virtual (venv):

Bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
3. Iniciar o Terminal Visual
Bash
streamlit run dashboard.py
🗺️ Roadmap de Desenvolvimento
[x] v1.0: Core Engine, IA Preditora e Dashboard Streamlit.

[ ] v2.0 (Próxima): Containerização com Docker e Deploy na AWS (EC2).

[ ] v2.1: Implementação de Autenticação e Gestão de Chaves de API (Vault).

[ ] v3.0: Módulo de Análise de Sentimento via Processamento de Linguagem Natural (NLP).

⚖️ Licença & Aviso Legal
Este projeto está licenciado sob a GNU General Public License v3.0.

AVISO: Este software tem fins puramente educacionais e de pesquisa. Negociar ativos financeiros envolve riscos significativos. O desenvolvedor não se responsabiliza por quaisquer perdas financeiras. Backtests passados não garantem lucros futuros.

Desenvolvido com ☕ e Python por [Seu Nome ou User]
