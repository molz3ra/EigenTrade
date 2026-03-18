import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import backtrader as bt
import time

# Importando o motor do nosso backend (index.py)
from index import DataPipeline, MLEngine, SignalFeed, MLStrategy

st.set_page_config(page_title="Quant Desk Setup", layout="wide", page_icon="📈")

# --- BARRA LATERAL (CONTROLES DO USUÁRIO) ---
st.sidebar.header("⚙️ Parâmetros do Robô")
symbol = st.sidebar.selectbox("Ativo", ["BTC/USDT", "ETH/USDT", "SOL/USDT"])
timeframe = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d"])
days_back = st.sidebar.slider("Dias de Histórico (Treino)", 30, 1000, 365)

st.sidebar.divider()
st.sidebar.header("💰 Gestão de Risco e Capital")
initial_cash = st.sidebar.number_input("Capital Inicial ($)", min_value=100.0, value=10000.0, step=100.0)
risk_per_trade = st.sidebar.slider("Uso da Banca por Trade (%)", 1, 100, 20)
stop_loss = st.sidebar.number_input("Stop Loss (%)", min_value=0.1, value=2.0, step=0.1) / 100
take_profit = st.sidebar.number_input("Take Profit (%)", min_value=0.1, value=4.0, step=0.1) / 100

st.title("🖥️ Terminal Quantitativo - IA")

# --- ABAS DA INTERFACE ---
tab1, tab2, tab3 = st.tabs(["📊 Backtest & Estatísticas", "📈 Gráficos Interativos", "📡 Scanner Ao Vivo"])

# Instanciando o Pipeline
pipeline = DataPipeline(symbol=symbol, timeframe=timeframe)
brain = MLEngine()

with tab1:
    st.markdown("### Simulação de Desempenho Histórico")
    if st.button("🚀 Iniciar Treinamento e Backtest", use_container_width=True):
        with st.spinner("Extraindo dados, treinando modelo e simulando operações..."):
            try:
                # 1. Pipeline e Treino (Com verificação de segurança)
                raw = pipeline.fetch_data(days_back=days_back)
                if raw is None or raw.empty:
                    st.error("Falha na coleta de dados. Verifique sua conexão ou tente outro ativo.")
                    st.stop()
                    
                features = pipeline.create_features(raw)
                if len(features) < 50:
                    st.warning("Poucos dados para treinar. Aumente os 'Dias de Histórico'.")
                    st.stop()

                model, df_results = brain.train_and_evaluate(features, pipeline.features)
                
                # Salva no estado para usar nas outras abas
                st.session_state['df'] = df_results
                st.session_state['model'] = model
                
                # 2. Orquestração do Backtrader
                cerebro = bt.Cerebro()
                cerebro.addstrategy(MLStrategy, sl=stop_loss, tp=take_profit)
                
                data = SignalFeed(dataname=df_results.dropna(subset=['prediction']))
                cerebro.adddata(data)
                
                # Capital e Taxas
                cerebro.broker.setcash(initial_cash)
                cerebro.broker.setcommission(commission=0.001)
                cerebro.addsizer(bt.sizers.PercentSizer, percents=risk_per_trade)
                
                # Analisadores
                cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
                cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
                
                results = cerebro.run()
                strat = results[0]
                
                # 3. Extração Segura de Métricas (À prova de quebras se houver 0 trades)
                end_cash = cerebro.broker.getvalue()
                roi = ((end_cash - initial_cash) / initial_cash) * 100
                
                trade_stats = strat.analyzers.trades.get_analysis()
                # Usando .get() para evitar KeyError caso o dicionário esteja vazio
                total_trades = trade_stats.get('total', {}).get('closed', 0)
                won_trades = trade_stats.get('won', {}).get('total', 0)
                win_rate = (won_trades / total_trades * 100) if total_trades > 0 else 0.0
                
                dd_info = strat.analyzers.drawdown.get_analysis()
                max_dd = dd_info.get('max', {}).get('drawdown', 0.0)
                
                # 4. Exibição Profissional dos KPIs
                st.success("Simulação Concluída com Sucesso!")
                st.divider()
                
                col1, col2, col3, col4 = st.columns(4)
                
                # Lógica visual de cores para o ROI
                roi_color = "normal" if roi >= 0 else "inverse"
                col1.metric("Capital Final", f"${end_cash:.2f}", f"{roi:.2f}% ROI", delta_color=roi_color)
                
                col2.metric("Taxa de Acerto (Win Rate)", f"{win_rate:.1f}%")
                col3.metric("Total de Operações Fechadas", total_trades)
                col4.metric("Risco Máximo (Drawdown)", f"-{max_dd:.2f}%")

                if total_trades == 0:
                    st.warning("⚠️ O robô não realizou nenhuma operação. A IA considerou o mercado muito arriscado ou os parâmetros estão muito restritos.")

            except Exception as e:
                st.error(f"Ocorreu um erro interno durante a simulação: {e}")

with tab2:
    if 'df' in st.session_state:
        st.markdown("### Análise Técnica e Sinais")
        df = st.session_state['df']
        
        fig = go.Figure()
        
        # Velas (Candlesticks)
        fig.add_trace(go.Candlestick(x=df.index, open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Preço'))
        
        # Médias e Bandas
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='orange', width=1.5), name='EMA 20'))
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_UPPER'], line=dict(color='gray', width=1, dash='dot'), name='BB Superior'))
        fig.add_trace(go.Scatter(x=df.index, y=df['BB_LOWER'], line=dict(color='gray', width=1, dash='dot'), fill='tonexty', fillcolor='rgba(128,128,128,0.1)', name='BB Inferior'))
        
        # Plotando os Sinais de Compra (Triângulos Verdes)
        buy_signals = df[df['prediction'] == 1]
        fig.add_trace(go.Scatter(x=buy_signals.index, y=buy_signals['low'] * 0.99, mode='markers', marker=dict(symbol='triangle-up', color='lime', size=10), name='Sinal Compra IA'))
        
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=600, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Execute o Backtest na aba 'Backtest & Estatísticas' para gerar os gráficos.")

with tab3:
    st.markdown("### Radar de Sinais em Tempo Real")
    if st.button("📡 Escanear Mercado Agora", use_container_width=True):
        if 'model' not in st.session_state:
            st.error("Treine a IA no Backtest primeiro para habilitar o Scanner Ao Vivo!")
        else:
            with st.spinner(f"Buscando últimos dados de {symbol}..."):
                try:
                    live_data = pipeline.fetch_data(days_back=5)
                    live_features = pipeline.create_features(live_data)
                    
                    if not live_features.empty:
                        last = live_features.iloc[-1:]
                        X = last[pipeline.features]
                        
                        pred = st.session_state['model'].predict(X)[0]
                        prob = st.session_state['model'].predict_proba(X)[0][1] * 100
                        price = last['close'].values[0]

                        st.divider()
                        st.subheader(f"Leitura Atual: {symbol}")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Preço de Fechamento Atual", f"${price:.2f}")
                        
                        if pred == 1 and prob > 60:
                            c2.metric("Decisão do Robô", "🟢 COMPRAR", "Sinal Forte de Alta")
                        else:
                            c2.metric("Decisão do Robô", "🟡 AGUARDAR", "Sem viés claro ou Risco Alto", delta_color="off")
                            
                        c3.metric("Confiança da IA", f"{prob:.1f}%", help="Acima de 60% = Sinal de Compra Válido.")
                    else:
                        st.error("Não foi possível gerar indicadores com os dados atuais.")
                except Exception as e:
                    st.error(f"Falha ao escanear mercado: {e}")