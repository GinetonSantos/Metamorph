# gui_improved.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import asyncio
import os
from datetime import datetime
from binance_handler import BinanceHandler
from logger import log_action
from tax_reporter import TaxReporter

class TradingBotGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Metamorph Trading Bot")
        self.root.geometry("900x500")
        self.root.resizable(True, True)
        
        # Variáveis de controle
        self.bot_running = False
        self.bot_thread = None
        self.binance_handler = None
        self.tax_reporter = TaxReporter()
        self.log_window = None
        self.signal_window = None
        self.last_signal_data = {}
        
        self.setup_ui()
        self.load_config()
        self.create_signal_monitor()
        
    def setup_ui(self):
        """Interface principal otimizada"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid configuration
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Status e controles
        self.setup_control_frame(main_frame)
        
        # Monitor de sinais
        self.setup_signal_frame(main_frame)
        
        # Saldos
        self.setup_balance_frame(main_frame)
        
        # Botões de ação
        self.setup_action_buttons(main_frame)
        
    def setup_control_frame(self, parent):
        """Frame de controle do bot"""
        control_frame = ttk.LabelFrame(parent, text="Controle do Bot", padding="5")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_label = ttk.Label(control_frame, text="Bot Parado", foreground="red")
        self.status_label.grid(row=0, column=0, padx=(0, 10))
        
        # Botões com controle de estado
        self.start_btn = ttk.Button(control_frame, text="Iniciar Bot", command=self.start_bot)
        self.start_btn.grid(row=0, column=1, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="Parar Bot", command=self.stop_bot, state="disabled")
        self.stop_btn.grid(row=0, column=2, padx=5)
        
        ttk.Button(control_frame, text="Atualizar Saldos", command=self.refresh_balances).grid(row=0, column=3, padx=5)
        
    def setup_signal_frame(self, parent):
        """Frame de monitoramento de sinais integrado"""
        signal_frame = ttk.LabelFrame(parent, text="Monitor de Sinais", padding="5")
        signal_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        signal_frame.columnconfigure(1, weight=1)
        
        # Labels de informação
        ttk.Label(signal_frame, text="Último Sinal:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.signal_pair_label = ttk.Label(signal_frame, text="Nenhum sinal recebido", font=("Arial", 10))
        self.signal_pair_label.grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(signal_frame, text="Status:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        
        self.signal_status_label = ttk.Label(signal_frame, text="Aguardando sinais...", foreground="orange")
        self.signal_status_label.grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
    
    def setup_balance_frame(self, parent):
        """Frame de saldos com conversão USD"""
        balance_frame = ttk.LabelFrame(parent, text="Saldos da Conta", padding="5")
        balance_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        balance_frame.columnconfigure(0, weight=1)
        balance_frame.rowconfigure(0, weight=1)
        
        # Treeview melhorado
        columns = ("Moeda", "Saldo Livre", "Saldo Bloqueado", "Total", "Valor USD")
        self.balance_tree = ttk.Treeview(balance_frame, columns=columns, show="headings", height=8)
        
        # Configurar colunas
        widths = [80, 120, 120, 120, 100]
        for i, (col, width) in enumerate(zip(columns, widths)):
            self.balance_tree.heading(col, text=col)
            self.balance_tree.column(col, width=width, anchor="center")
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(balance_frame, orient="vertical", command=self.balance_tree.yview)
        h_scroll = ttk.Scrollbar(balance_frame, orient="horizontal", command=self.balance_tree.xview)
        self.balance_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.balance_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
    def setup_action_buttons(self, parent):
        """Botões de ação"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(action_frame, text="📊 Ver Logs", command=self.show_log_window).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="📈 Relatório IR", command=self.show_tax_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="💾 Exportar Operações", command=self.export_operations).pack(side=tk.LEFT, padx=5)
        
    def create_signal_monitor(self):
        """Cria monitor de sinais integrado"""
        # Será criado no setup_ui como parte da interface principal
        pass
        
    def load_config(self):
        """Carrega configurações"""
        from dotenv import load_dotenv
        load_dotenv()
        
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        self.simulation_mode = os.getenv("SIMULATION_MODE", "False").lower() == "true"
        
        if self.api_key and self.api_secret:
            self.binance_handler = BinanceHandler(self.api_key, self.api_secret, self.simulation_mode)
            self.refresh_balances()
            
        # Configurar callback do signal monitor
        from signal_monitor import signal_monitor
        signal_monitor.set_gui_callback(self.update_signal_monitor)
        
    def start_bot(self):
        """Inicia bot com controle de botões"""
        if not self.bot_running:
            self.bot_running = True
            self.status_label.config(text="Bot Executando", foreground="green")
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            
            self.bot_thread = threading.Thread(target=self.run_bot_async, daemon=True)
            self.bot_thread.start()
            
            self.update_signal_monitor("Bot iniciado", "Aguardando sinais...", "success")
    
    def stop_bot(self):
        """Para bot com controle de botões"""
        if self.bot_running:
            self.bot_running = False
            self.status_label.config(text="Bot Parado", foreground="red")
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            
            self.update_signal_monitor("Bot parado", "Bot parado pelo usuário", "error")
    
    def run_bot_async(self):
        """Executa bot com monitoramento"""
        try:
            from main import main
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(main())
        except Exception as e:
            self.update_signal_monitor("Erro no bot", f"Erro: {e}", "error")
        finally:
            self.bot_running = False
            self.root.after(0, lambda: (
                self.status_label.config(text="Bot Parado", foreground="red"),
                self.start_btn.config(state="normal"),
                self.stop_btn.config(state="disabled")
            ))
    
    def refresh_balances(self):
        """Atualiza saldos com conversão USD"""
        if not self.binance_handler:
            return
            
        try:
            # Limpar dados
            for item in self.balance_tree.get_children():
                self.balance_tree.delete(item)
            
            if self.simulation_mode:
                self.balance_tree.insert("", "end", values=("USDT", "1000.00", "0.00", "1000.00", "1000.00"))
            else:
                account = self.binance_handler.client.get_account()
                
                # Obter preços para conversão
                prices = {}
                try:
                    ticker_prices = self.binance_handler.client.get_all_tickers()
                    for ticker in ticker_prices:
                        if ticker['symbol'].endswith('USDT'):
                            prices[ticker['symbol'].replace('USDT', '')] = float(ticker['price'])
                except:
                    pass
                
                for balance in account['balances']:
                    free = float(balance['free'])
                    locked = float(balance['locked'])
                    
                    if free > 0 or locked > 0:
                        total = free + locked
                        asset = balance['asset']
                        
                        # Calcular valor USD
                        if asset == 'USDT':
                            usd_value = total
                        elif asset in prices:
                            usd_value = total * prices[asset]
                        else:
                            usd_value = 0
                        
                        self.balance_tree.insert("", "end", values=(
                            asset,
                            f"{free:.8f}".rstrip('0').rstrip('.'),
                            f"{locked:.8f}".rstrip('0').rstrip('.'),
                            f"{total:.8f}".rstrip('0').rstrip('.'),
                            f"{usd_value:.2f}" if usd_value > 0 else "N/A"
                        ))
                
        except Exception as e:
            print(f"Erro ao atualizar saldos: {e}")
    
    def update_signal_monitor(self, pair, details, status_type="info"):
        """Atualiza monitor de sinais integrado (thread-safe)"""
        def update_ui():
            colors = {"success": "green", "error": "red", "info": "blue", "warning": "orange"}
            
            self.signal_pair_label.config(text=pair)
            self.signal_status_label.config(text=details, foreground=colors.get(status_type, "black"))
            
            # Auto-atualizar saldos após operação
            if "executada" in details.lower() or "criadas" in details.lower():
                self.root.after(2000, self.refresh_balances)
        
        # Executar na thread principal da GUI
        self.root.after(0, update_ui)
    
    def show_log_window(self):
        """Mostra janela de logs"""
        if self.log_window and self.log_window.winfo_exists():
            self.log_window.lift()
            return
            
        self.log_window = tk.Toplevel(self.root)
        self.log_window.title("Logs do Sistema")
        self.log_window.geometry("800x400")
        
        # Frame principal
        log_frame = ttk.Frame(self.log_window, padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Área de logs
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Botões
        btn_frame = ttk.Frame(log_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="Carregar Logs", command=self.load_logs).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Limpar", command=self.clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Salvar", command=self.save_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Fechar", command=self.log_window.destroy).pack(side=tk.RIGHT)
        
        # Carregar logs automaticamente
        self.load_logs()
    
    def show_tax_report(self):
        """Mostra relatório para IR"""
        try:
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            summary = self.tax_reporter.get_monthly_summary(current_year, current_month)
            
            report = f"""RELATÓRIO MENSAL - {current_month:02d}/{current_year}
            
Operações Executadas: {summary.get('operacoes_executadas', 0)}
Operações Falhadas: {summary.get('operacoes_falhadas', 0)}

Total Compras: ${summary.get('total_compras', 0):.2f} USDT
Total Vendas: ${summary.get('total_vendas', 0):.2f} USDT
Total Taxas: ${summary.get('total_taxas', 0):.8f} USDT

Resultado: ${summary.get('total_vendas', 0) - summary.get('total_compras', 0):.2f} USDT

Arquivo CSV: operacoes_ir.csv"""
            
            messagebox.showinfo("Relatório IR", report)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
    
    def export_operations(self):
        """Exporta operações"""
        try:
            if os.path.exists("operacoes_ir.csv"):
                messagebox.showinfo("Exportação", "Arquivo 'operacoes_ir.csv' já existe na pasta do bot.\n\nEste arquivo contém todas as operações registradas e pode ser usado para declaração de IR.")
            else:
                messagebox.showwarning("Aviso", "Nenhuma operação registrada ainda.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro: {e}")
    
    def load_logs(self):
        """Carrega logs com múltiplos encodings"""
        if not hasattr(self, 'log_text'):
            return
            
        try:
            if os.path.exists("trading_bot.log"):
                encodings = ['utf-8', 'cp1252', 'latin1', 'iso-8859-1']
                
                for encoding in encodings:
                    try:
                        with open("trading_bot.log", "r", encoding=encoding) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    content = "Erro: Não foi possível decodificar o arquivo"
                
                self.log_text.delete("1.0", tk.END)
                self.log_text.insert("1.0", content)
                self.log_text.see(tk.END)
            else:
                self.log_text.delete("1.0", tk.END)
                self.log_text.insert("1.0", "Arquivo trading_bot.log não encontrado")
        except Exception as e:
            if hasattr(self, 'log_text'):
                self.log_text.delete("1.0", tk.END)
                self.log_text.insert("1.0", f"Erro ao carregar logs: {e}")
    
    def clear_logs(self):
        """Limpa logs"""
        if hasattr(self, 'log_text'):
            self.log_text.delete("1.0", tk.END)
    
    def save_logs(self):
        """Salva logs"""
        if not hasattr(self, 'log_text'):
            return
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"gui_logs_{timestamp}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(self.log_text.get("1.0", tk.END))
            messagebox.showinfo("Sucesso", f"Logs salvos em {filename}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar: {e}")
    
    def run(self):
        """Inicia interface"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Trata fechamento"""
        if self.bot_running:
            if messagebox.askokcancel("Fechar", "Bot está executando. Parar e fechar?"):
                self.stop_bot()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    app = TradingBotGUI()
    app.run()