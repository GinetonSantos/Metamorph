# binance_handler.py
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from logger import log_action
from tax_reporter import TaxReporter
from signal_monitor import signal_monitor
import math

class BinanceHandler:
    def __init__(self, api_key, api_secret, simulation_mode=False):
        self.simulation = simulation_mode
        self.symbol_info = {}
        self.tax_reporter = TaxReporter()
        if not simulation_mode:
            try:
                self.client = Client(api_key, api_secret)
                log_action("[REAL] Conectado à Binance API com sucesso")
            except Exception as e:
                log_action(f"[REAL] Erro ao conectar na Binance: {e}")
                self.client = None
        else:
            self.client = None
            log_action("[SIMULAÇÃO] Modo simulação ativo - não conectará na Binance")

    def get_symbol_info(self, symbol):
        """Obtém informações do par de moeda da Binance"""
        if symbol in self.symbol_info:
            return self.symbol_info[symbol]
        
        try:
            if not self.simulation and self.client:
                exchange_info = self.client.get_exchange_info()
                for s in exchange_info['symbols']:
                    if s['symbol'] == symbol:
                        info = {
                            'minQty': float(next(f['minQty'] for f in s['filters'] if f['filterType'] == 'LOT_SIZE')),
                            'stepSize': float(next(f['stepSize'] for f in s['filters'] if f['filterType'] == 'LOT_SIZE')),
                            'minNotional': float(next(f['minNotional'] for f in s['filters'] if f['filterType'] == 'NOTIONAL')),
                            'tickSize': float(next(f['tickSize'] for f in s['filters'] if f['filterType'] == 'PRICE_FILTER'))
                        }
                        self.symbol_info[symbol] = info
                        return info
            else:
                # Valores padrão para simulação
                info = {
                    'minQty': 0.001,
                    'stepSize': 0.001,
                    'minNotional': 10.0,
                    'tickSize': 0.0001
                }
                self.symbol_info[symbol] = info
                return info
        except Exception as e:
            log_action(f"Erro ao obter informações do símbolo {symbol}: {e}")
            # Valores padrão em caso de erro
            return {'minQty': 0.001, 'stepSize': 0.001, 'minNotional': 10.0, 'tickSize': 0.0001}
    
    def adjust_quantity(self, quantity, step_size):
        """Ajusta quantidade conforme step size da Binance"""
        precision = int(round(-math.log(step_size, 10), 0))
        return math.floor(quantity / step_size) * step_size
    
    def adjust_price(self, price, tick_size):
        """Ajusta preço conforme tick size da Binance"""
        if tick_size >= 1:
            return round(price)
        precision = int(round(-math.log(tick_size, 10), 0))
        return round(price, precision)

    def calculate_investment_percentage(self, balance: float) -> tuple[float, str]:
        """
        Calcula percentual de investimento baseado no tamanho da conta.
        
        Returns:
            tuple: (percentual, categoria_conta)
        """
        if balance <= 50:
            return 0.85, "PEQUENA"
        elif balance <= 200:
            return 0.65, "MÉDIA"
        else:
            return 0.50, "GRANDE"
    
    def execute_trade(self, symbol, buy_price, targets, stop, signal_id):
        try:
            # Obter informações do símbolo
            symbol_info = self.get_symbol_info(symbol)
            log_action(f"Informações do par {symbol}: MinQty={symbol_info['minQty']}, MinNotional={symbol_info['minNotional']}")
            
            if self.simulation:
                # Simulação com saldo fictício de 1000 USDT
                balance = 1000.0
                investment_percentage, account_category = self.calculate_investment_percentage(balance)
                invest_amount = balance * investment_percentage
                
                log_action(f"[SIMULAÇÃO] Conta {account_category}: {investment_percentage*100:.0f}% do saldo")
                
                # Validar valor mínimo
                if invest_amount < symbol_info['minNotional']:
                    required_balance = symbol_info['minNotional'] / investment_percentage
                    log_action(f"[SIMULAÇÃO] ❌ SALDO INSUFICIENTE para {symbol}")
                    log_action(f"[SIMULAÇÃO] Valor disponível: {invest_amount:.2f} USDT | Mínimo necessário: {symbol_info['minNotional']:.2f} USDT")
                    log_action(f"[SIMULAÇÃO] 💰 Saldo mínimo recomendado para conta {account_category}: {required_balance:.2f} USDT")
                    log_action(f"[SIMULAÇÃO] ⏳ Aguardando novos sinais para operar...")
                    return
                
                # Calcular e ajustar quantidade
                raw_quantity = invest_amount / buy_price
                quantity = self.adjust_quantity(raw_quantity, symbol_info['stepSize'])
                
                # Validar quantidade mínima
                if quantity < symbol_info['minQty']:
                    log_action(f"[SIMULAÇÃO] ERRO: Quantidade {quantity} menor que mínimo {symbol_info['minQty']}")
                    return
                
                # Validar valor notional final
                notional_value = quantity * buy_price
                if notional_value < symbol_info['minNotional']:
                    log_action(f"[SIMULAÇÃO] ERRO: Valor notional {notional_value} USDT menor que mínimo {symbol_info['minNotional']} USDT")
                    return
                
                log_action(f"[SIMULAÇÃO] === VALIDAÇÕES APROVADAS ===")
                log_action(f"[SIMULAÇÃO] Quantidade bruta: {raw_quantity} -> Ajustada: {quantity}")
                log_action(f"[SIMULAÇÃO] Valor notional: {notional_value} USDT (min: {symbol_info['minNotional']})")
                
                log_action(f"[SIMULAÇÃO] === ORDEM DE COMPRA ===")
                log_action(f"[SIMULAÇÃO] Symbol: {symbol}")
                log_action(f"[SIMULAÇÃO] Side: BUY")
                log_action(f"[SIMULAÇÃO] Type: MARKET")
                log_action(f"[SIMULAÇÃO] Quantity: {quantity}")
                log_action(f"[SIMULAÇÃO] Preço referência: {buy_price}")
                log_action(f"[SIMULAÇÃO] Valor investido: {invest_amount} USDT")
                log_action(f"[SIMULAÇÃO] ID do sinal: {signal_id}")
                
                # Lógica adaptativa para simulação
                def calculate_sim_targets_strategy(quantity, targets, min_notional):
                    part_qty_3 = self.adjust_quantity(quantity / 3, symbol_info['stepSize'])
                    test_value_3 = part_qty_3 * float(targets[0])
                    
                    if test_value_3 >= min_notional:
                        return [(part_qty_3, targets, "3 alvos")]
                    
                    part_qty_2 = self.adjust_quantity(quantity / 2, symbol_info['stepSize'])
                    test_value_2 = part_qty_2 * float(targets[0])
                    
                    if test_value_2 >= min_notional:
                        return [(part_qty_2, targets[:2], "2 alvos (maior ignorado)")]
                    
                    return [(quantity, [targets[0]], "1 alvo (concentrado)")]
                
                strategy = calculate_sim_targets_strategy(quantity, targets, symbol_info['minNotional'])
                sim_part_qty, sim_active_targets, sim_strategy_name = strategy[0]
                
                log_action(f"[SIMULAÇÃO] Estratégia escolhida: {sim_strategy_name}")
                # Removido - substituído por OCO acima
                
                adjusted_stop = self.adjust_price(float(stop), symbol_info['tickSize'])
                # Simular ordens OCO
                sim_adjusted_stop = self.adjust_price(float(stop), symbol_info['tickSize'])
                log_action(f"[SIMULAÇÃO] === ORDENS OCO (Take Profit + Stop Loss) ===")
                
                for i, target in enumerate(sim_active_targets):
                    sim_adjusted_target = self.adjust_price(float(target), symbol_info['tickSize'])
                    sim_part_notional = sim_part_qty * sim_adjusted_target
                    log_action(f"[SIMULAÇÃO] OCO Alvo {i+1}:")
                    log_action(f"[SIMULAÇÃO]   → Take Profit: {sim_adjusted_target} | Qtd: {sim_part_qty} | Valor: {sim_part_notional:.2f} USDT")
                    log_action(f"[SIMULAÇÃO]   → Stop Loss: {sim_adjusted_stop} | Qtd: {sim_part_qty}")
                return
            
            # Modo real - conecta na Binance
            if not self.client:
                log_action(f"[REAL] ERRO: Cliente Binance não conectado")
                return
                
            balance = float(self.client.get_asset_balance(asset='USDT')['free'])
            investment_percentage, account_category = self.calculate_investment_percentage(balance)
            invest_amount = balance * investment_percentage
            
            log_action(f"[REAL] Saldo disponível: {balance} USDT | Conta {account_category}")
            log_action(f"[REAL] Percentual de investimento: {investment_percentage*100:.0f}% | Valor a investir: {invest_amount:.2f} USDT")

            # Validar valor mínimo
            if invest_amount < symbol_info['minNotional']:
                # Calcular saldo mínimo baseado no percentual atual
                required_balance = symbol_info['minNotional'] / investment_percentage
                log_action(f"[REAL] ❌ SALDO INSUFICIENTE para {symbol}")
                log_action(f"[REAL] Valor disponível: {invest_amount:.2f} USDT | Mínimo necessário: {symbol_info['minNotional']:.2f} USDT")
                log_action(f"[REAL] 💰 Saldo mínimo recomendado para conta {account_category}: {required_balance:.2f} USDT")
                log_action(f"[REAL] ⏳ Aguardando novos sinais para operar...")
                return

            # Calcular e ajustar quantidade
            raw_quantity = invest_amount / buy_price
            quantity = self.adjust_quantity(raw_quantity, symbol_info['stepSize'])
            
            # Validar quantidade mínima
            if quantity < symbol_info['minQty']:
                log_action(f"[REAL] ERRO: Quantidade {quantity} menor que mínimo {symbol_info['minQty']}")
                return
            
            # Validar valor notional final
            notional_value = quantity * buy_price
            if notional_value < symbol_info['minNotional']:
                log_action(f"[REAL] ERRO: Valor notional {notional_value} USDT menor que mínimo {symbol_info['minNotional']} USDT")
                return
            
            log_action(f"[REAL] === VALIDAÇÕES APROVADAS ===")
            log_action(f"[REAL] Quantidade bruta: {raw_quantity} -> Ajustada: {quantity}")
            log_action(f"[REAL] Valor notional: {notional_value} USDT")

            # Executa compra real
            try:
                order = self.client.order_market_buy(
                    symbol=symbol,
                    quantity=quantity
                )
                
                # Registrar operação para IR
                executed_qty = float(order.get('executedQty', quantity))
                avg_price = float(order.get('fills', [{}])[0].get('price', buy_price)) if order.get('fills') else buy_price
                commission = sum(float(fill.get('commission', 0)) for fill in order.get('fills', []))
                total_value = executed_qty * avg_price
                
                self.tax_reporter.register_buy_operation(
                    symbol=symbol,
                    quantity=executed_qty,
                    price=avg_price,
                    total_value=total_value,
                    fee=commission,
                    signal_id=signal_id
                )
                
                log_action(f"[REAL] ✅ Compra executada | OrderID: {order['orderId']} | {symbol} | Qtd: {quantity} | ID: {signal_id}")
                log_action(f"[REAL] 📄 Operação registrada para IR")
            except BinanceAPIException as e:
                self.tax_reporter.register_failed_operation(symbol, signal_id, f"Erro na compra: {e.message}")
                log_action(f"[REAL] ❌ Erro na compra: {e.message} (Código: {e.code})")
                return
            except Exception as e:
                self.tax_reporter.register_failed_operation(symbol, signal_id, f"Erro inesperado: {str(e)}")
                log_action(f"[REAL] ❌ Erro inesperado na compra: {e}")
                return

            # Lógica adaptativa para alvos
            def calculate_targets_strategy(quantity, targets, min_notional):
                """Calcula estratégia de alvos baseada no valor mínimo"""
                # Testar com 3 alvos
                part_qty_3 = self.adjust_quantity(quantity / 3, symbol_info['stepSize'])
                test_value_3 = part_qty_3 * float(targets[0])  # Menor alvo
                
                if test_value_3 >= min_notional:
                    return [(part_qty_3, targets, "3 alvos")]
                
                # Testar com 2 alvos (ignora o maior)
                part_qty_2 = self.adjust_quantity(quantity / 2, symbol_info['stepSize'])
                test_value_2 = part_qty_2 * float(targets[0])
                
                if test_value_2 >= min_notional:
                    return [(part_qty_2, targets[:2], "2 alvos (maior ignorado)")]
                
                # Usar apenas 1 alvo (o primeiro)
                return [(quantity, [targets[0]], "1 alvo (concentrado)")]
            
            # Calcular estratégia de alvos
            strategy = calculate_targets_strategy(quantity, targets, symbol_info['minNotional'])
            part_qty, active_targets, strategy_name = strategy[0]
            
            log_action(f"[REAL] Estratégia escolhida: {strategy_name}")
            log_action(f"[REAL] Alvos ativos: {len(active_targets)} | Quantidade por alvo: {part_qty}")
            
            # Criar ordens OCO (Take Profit + Stop Loss) para cada alvo
            adjusted_stop = self.adjust_price(float(stop), symbol_info['tickSize'])
            successful_ocos = 0
            
            for i, target in enumerate(active_targets):
                try:
                    adjusted_target = self.adjust_price(float(target), symbol_info['tickSize'])
                    part_notional = part_qty * adjusted_target
                    
                    # Criar ordem OCO (One-Cancels-Other)
                    oco_order = self.client.create_oco_order(
                        symbol=symbol,
                        side='SELL',
                        quantity=part_qty,
                        price=adjusted_target,  # Take Profit (LIMIT)
                        stopPrice=adjusted_stop,  # Stop Loss trigger
                        stopLimitPrice=adjusted_stop,  # Stop Loss execution price
                        stopLimitTimeInForce='GTC'
                    )
                    
                    successful_ocos += 1
                    log_action(f"[REAL] ✅ OCO criada | OrderListID: {oco_order['orderListId']} | Alvo {i+1}")
                    log_action(f"[REAL]   → Take Profit: {adjusted_target} | Qtd: {part_qty} | Valor: {part_notional:.2f} USDT")
                    log_action(f"[REAL]   → Stop Loss: {adjusted_stop} | Qtd: {part_qty}")
                    
                except BinanceAPIException as e:
                    log_action(f"[REAL] ❌ Erro na OCO Alvo {i+1}: {e.message} (Código: {e.code})")
                except Exception as e:
                    log_action(f"[REAL] ❌ Erro inesperado na OCO Alvo {i+1}: {e}")
            
            log_action(f"[REAL] ✅ Resumo: {successful_ocos} ordens OCO criadas de {len(active_targets)} alvos")

            # OCO já inclui Take Profit + Stop Loss, não precisa de ordem separada

        except BinanceAPIException as e:
            mode = "SIMULAÇÃO" if self.simulation else "REAL"
            log_action(f"[{mode}] ❌ Erro da API Binance: {e.message} (Código: {e.code})")
        except Exception as e:
            mode = "SIMULAÇÃO" if self.simulation else "REAL"
            log_action(f"[{mode}] ❌ Erro inesperado na execução: {e}")





