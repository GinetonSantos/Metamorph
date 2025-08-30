# telegram_handler.py
import re
from telethon import TelegramClient, events
from logger import log_action

class TelegramClientHandler:
    def __init__(self, api_id, api_hash, phone, group, binance_handler):
        self.client = TelegramClient('bot_session', api_id, api_hash)
        self.phone = phone
        self.group = group
        self.binance = binance_handler

    async def run(self):
        """Executa bot normalmente"""
        await self.run_with_stop_check(lambda: True)
    
    async def run_with_stop_check(self, should_continue_func):
        """Executa bot com verificação de parada externa"""
        import asyncio
        
        await self.client.start(phone=self.phone)

        @self.client.on(events.NewMessage(chats=self.group))
        async def handler(event):
            if not should_continue_func():
                return
                
            message = event.message.message
            if "NOVO SINAL" in message and "#" in message and "Compra:" in message:
                log_action(f"Sinal detectado: {message}")
                self.process_signal(message)
            elif "NOVO SINAL FREE" in message:
                log_action("Sinal FREE detectado - ignorando (sem dados de trading)")

        # Loop com verificação de parada
        while should_continue_func():
            try:
                await asyncio.sleep(1)  # Verificar a cada segundo
            except asyncio.CancelledError:
                break
        
        await self.client.disconnect()
        log_action("Cliente Telegram desconectado")

    def process_signal(self, msg: str):
        try:
            pair = re.search(r"#(\w+USDT)", msg).group(1)
            buy_price = float(re.search(r"Compra: ([0-9.]+)", msg).group(1))
            targets = re.findall(r"Alvo \d+: ([0-9.]+)", msg)
            targets = [float(t) for t in targets]
            stop = float(re.search(r"StopLoss: ([0-9.]+)", msg).group(1))
            signal_id = re.search(r"ID: (#[A-Za-z0-9]+)", msg).group(1)

            # Notificar GUI que sinal foi recebido
            from signal_monitor import signal_monitor
            signal_monitor.signal_received(pair, signal_id)
            
            self.binance.execute_trade(pair, buy_price, targets, stop, signal_id)
        except Exception as e:
            log_action(f"Erro ao processar sinal: {e}")
            # Notificar GUI sobre erro
            from signal_monitor import signal_monitor
            signal_monitor.operation_failed("Erro", f"Falha ao processar sinal: {e}")