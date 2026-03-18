import ccxt
import pandas as pd
import pandas_ta as ta
import numpy as np
import logging
import time
import requests
from typing import Tuple, List
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score
import backtrader as bt
import warnings

# Configuração de Log e Supressão de Avisos
warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==========================================
# FASE 1 & 2: PIPELINE DE DADOS (BLINDADO)
# ==========================================
class DataPipeline:
    def __init__(self, symbol: str = 'BTC/USDT', timeframe: str = '1h'):
        self.exchange = ccxt.binance({'enableRateLimit': True})
        self.symbol = symbol
        self.timeframe = timeframe
        self.features = ['RSI_14', 'EMA_20', 'EMA_50', 'BB_LOWER', 'BB_MID', 'BB_UPPER', 'volume']

    def fetch_data(self, days_back: int = 730) -> pd.DataFrame:
        logging.info(f"Fase 1: Extraindo histórico de {self.symbol}...")
        since = self.exchange.milliseconds() - (days_back * 24 * 60 * 60 * 1000)
        all_ohlcv = []

        while since < self.exchange.milliseconds():
            try:
                ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.timeframe, since)
                if not ohlcv: break
                since = ohlcv[-1][0] + 1
                all_ohlcv.extend(ohlcv)
            except Exception as e:
                logging.error(f"Erro na API: {e}")
                break

        df = pd.DataFrame(all_ohlcv, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
        df.set_index('datetime', inplace=True)
        
        for col in df.columns:
            df[col] = df[col].astype(float)
        return df

    def create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        logging.info("Fase 2: Engenharia de Recursos (Features)...")
        df = df.copy()

        df['RSI_14'] = ta.rsi(df['close'], length=14)
        df['EMA_20'] = ta.ema(df['close'], length=20)
        df['EMA_50'] = ta.ema(df['close'], length=50)

        bb = ta.bbands(df['close'], length=20, std=2.0)
        df['BB_LOWER'] = bb.iloc[:, 0]
        df['BB_MID'] = bb.iloc[:, 1]
        df['BB_UPPER'] = bb.iloc[:, 2]

        df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
        df.dropna(inplace=True)
        return df

# ==========================================
# FASE 3: INTELIGÊNCIA ARTIFICIAL
# ==========================================
class MLEngine:
    def __init__(self):
        self.model = XGBClassifier(
            n_estimators=150,
            learning_rate=0.03,
            max_depth=4,
            subsample=0.8,
            colsample_bytree=0.8,
            eval_metric='logloss',
            random_state=42
        )

    def train_and_evaluate(self, df: pd.DataFrame, features: List[str]) -> Tuple[XGBClassifier, pd.DataFrame]:
        logging.info("Fase 3: Treinando Cérebro (XGBoost)...")
        
        split = int(len(df) * 0.8)
        train, test = df.iloc[:split], df.iloc[split:]

        self.model.fit(train[features], train['target'])
        
        y_pred = self.model.predict(test[features])
        acc = accuracy_score(test['target'], y_pred)
        logging.info(f"Acurácia Validada (OOT): {acc * 100:.2f}%")
        
        df['prediction'] = np.nan
        df.iloc[split:, df.columns.get_loc('prediction')] = y_pred
        return self.model, df

# ==========================================
# FASE 4: SIMULAÇÃO COM POSITION SIZING
# ==========================================
class SignalFeed(bt.feeds.PandasData):
    lines = ('prediction',)
    params = (('prediction', -1),)

class MLStrategy(bt.Strategy):
    # Parâmetros de Gestão de Risco
    params = (('sl', 0.02), ('tp', 0.04)) # Stop Loss de 2%, Take Profit de 4%

    def __init__(self):
        self.signal = self.datas[0].prediction

    def next(self):
        if not self.position: # Se não estou comprado
            if self.signal[0] == 1:
                self.buy() # O sizer cuida da quantidade automaticamente
        else:
            # Lógica segura e à prova de falhas para zerar a posição
            cost = self.position.price
            current_price = self.datas[0].close[0]
            
            if current_price >= cost * (1 + self.p.tp): # Atingiu o Lucro
                self.close()
            elif current_price <= cost * (1 - self.p.sl): # Bateu no Stop Loss
                self.close()

def run_backtest(df: pd.DataFrame):
    logging.info("Fase 4: Simulador Realista de Mercado Iniciado...")
    cerebro = bt.Cerebro()
    cerebro.addstrategy(MLStrategy)

    test_df = df.dropna(subset=['prediction'])
    data = SignalFeed(dataname=test_df)
    
    cerebro.adddata(data)
    
    # 🏦 GESTÃO DE CAPITAL E POSITION SIZING
    cerebro.broker.setcash(10000.0)
    cerebro.broker.setcommission(commission=0.001) # Taxa Binance
    
    # A MÁGICA ACONTECE AQUI: Aloca apenas 20% do capital disponível por trade
    cerebro.addsizer(bt.sizers.PercentSizer, percents=20)
    
    start_val = cerebro.broker.getvalue()
    cerebro.run()
    end_val = cerebro.broker.getvalue()
    
    logging.info(f"Capital Inicial: ${start_val:.2f}")
    logging.info(f"Capital Final (Realista): ${end_val:.2f} (ROI: {((end_val-start_val)/start_val)*100:.2f}%)")

# ==========================================
# FASE 5: BOT OPERACIONAL (TEMPO REAL)
# ==========================================
class LiveBot:
    def __init__(self, pipeline: DataPipeline, model: XGBClassifier):
        self.pipeline = pipeline
        self.model = model

    def monitor(self):
        logging.info("Sincronizando com a Exchange (Live Mode)...")
        live_data = self.pipeline.fetch_data(days_back=5)
        live_features = self.pipeline.create_features(live_data)
        
        last = live_features.iloc[-1:]
        X = last[self.pipeline.features]
        
        pred = self.model.predict(X)[0]
        prob = self.model.predict_proba(X)[0][1] * 100
        
        price = last['close'].values[0]
        
        if pred == 1 and prob > 60:
            logging.info(f"🟢 SINAL DE COMPRA: {self.pipeline.symbol} | Preço: ${price:.2f} | Confiança: {prob:.1f}%")
        else:
            logging.info(f"😴 Mercado em espera... (Confiança Compra: {prob:.1f}%)")

# ==========================================
# ORQUESTRAÇÃO FINAL
# ==========================================
if __name__ == "__main__":
    pipe = DataPipeline(symbol='BTC/USDT', timeframe='1h')
    brain = MLEngine()
    
    raw = pipe.fetch_data(days_back=730)
    processed = pipe.create_features(raw)
    model, df_results = brain.train_and_evaluate(processed, pipe.features)
    
    run_backtest(df_results)
    
    bot = LiveBot(pipe, model)
    logging.info("Iniciando monitoramento contínuo. Pressione Ctrl+C para parar.")
    try:
        while True:
            bot.monitor()
            time.sleep(3600)
    except KeyboardInterrupt:
        logging.info("Bot desligado com segurança.")