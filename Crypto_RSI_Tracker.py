import time
from datetime import datetime
from tradingview_ta import TA_Handler, Interval
from tkinter import *
from tkinter.scrolledtext import ScrolledText
import threading
from plyer import notification
import tkinter as tk


class RSI_Crypto_Tracker:
    def __init__(self, root):
        self.root = root
        self.root.configure(background='gray50')
        root.overrideredirect(True)

        self.stop_flag = False  
        self.previous_rsi_values = {}  

        def start_move(event):
            root._offset_x = event.x_root - root.winfo_x()
            root._offset_y = event.y_root - root.winfo_y()

        def do_move(event):
            root.geometry(f"+{event.x_root - root._offset_x}+{event.y_root - root._offset_y}")

        root.bind("<Button-1>", start_move)
        root.bind("<B1-Motion>", do_move)

        self.root.title("RSI Tracker by EinfacheEnte")

        #gui layout
        self.console_frame1 = Frame(root, bg="black")
        self.console_frame1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.console_frame2 = Frame(root, bg="black")
        self.console_frame2.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.rsi_console = ScrolledText(self.console_frame1, bg="gray11", fg="white", font=("Courier", 10))
        self.rsi_console.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.progress_console = ScrolledText(self.console_frame2, bg="gray11", fg="white", font=("Courier", 10))
        self.progress_console.pack(fill=BOTH, expand=True, padx=5, pady=5)

     
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        #call loop
        self.loop()

    def send_notification(self, title, message):
        #notification
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="RSI Tracker",
                timeout=5
            )
        except Exception as e:
            self.log_to_progress_console(f"Error sending notification: {str(e)}", "red")

    def log_to_rsi_console(self, message, color):
        #rsi trigger value consol
        self.rsi_console.tag_configure(color, foreground=color)
        self.rsi_console.insert(END, message, color)
        self.rsi_console.insert(END, "\n")
        self.rsi_console.see(END)

    def log_to_progress_console(self, message, color="white"):
        #progress consol showing log of received data
        self.progress_console.tag_configure(color, foreground=color)
        self.progress_console.insert(END, message, color)
        self.progress_console.insert(END, "\n")
        self.progress_console.see(END)

    def track_rsi(self, symbol, interval, color):
        #coin
        try:
            now = datetime.now().strftime('%H:%M:%S')
            asset = TA_Handler(
                symbol=symbol,
                screener="crypto",
                exchange="Bitget",
                interval=interval
            )
            data = asset.get_analysis()
            rsi = data.indicators["RSI"]

            # rsi movement algorithim
            previous_rsi = self.previous_rsi_values.get(symbol, rsi)
            rsi_direction_color = "green" if rsi > previous_rsi else "red" if rsi < previous_rsi else "white"
            self.previous_rsi_values[symbol] = rsi

            self.log_to_progress_console(f"RSI: {symbol} {round(rsi, 2)} ({'▲' if rsi > previous_rsi else '▼' if rsi < previous_rsi else '='}) at {now}", rsi_direction_color)

            if rsi <= 37 or rsi >= 70:  # schwellen gränzen
                condition = "oversold" if rsi <= 37 else "overbought"
                message = f"{symbol} RSI ({interval}): {round(rsi, 2)} ({condition.upper()}) at {now}"
                self.log_to_rsi_console(message, color)

                # notification
                threading.Thread(
                    target=lambda: self.send_notification(
                        title=f"RSI Alert: {symbol}",
                        message=message
                    ),
                    daemon=True
                ).start()
        except Exception as e:
            self.log_to_progress_console(f"Error tracking {symbol}: {str(e)}", "red")

    def loop(self):
        #loop to run tracking function of rsi
        if self.stop_flag:  
            return

        self.track_rsi("BTCUSDT.P", Interval.INTERVAL_5_MINUTES, "orange")
        self.track_rsi("ETHUSDT.P", Interval.INTERVAL_5_MINUTES, "cyan")
        self.track_rsi("XRPUSDT.P", Interval.INTERVAL_1_MINUTE, "gray")
        self.track_rsi("SOLUSDT.P", Interval.INTERVAL_5_MINUTES, "DarkOrchid3")
        self.track_rsi("LTCUSDT.P", Interval.INTERVAL_5_MINUTES, "cyan")
        self.track_rsi("SHIBUSDT.P", Interval.INTERVAL_5_MINUTES, "red")
        self.track_rsi("DOGEUSDT.P", Interval.INTERVAL_5_MINUTES, "orange")

        #sleep zzZZZZzzzZZZZzzzz
        self.root.after(10000, self.loop)

    def on_close(self):
        
        self.stop_flag = True
        self.root.destroy()


if __name__ == "__main__":
    root = Tk()
    app = RSI_Crypto_Tracker(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)  # close application :C
    root.mainloop()
