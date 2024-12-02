import time
from datetime import datetime
from tradingview_ta import TA_Handler, Interval
from  tkinter import * 
from tkinter.scrolledtext import ScrolledText
import threading
from plyer import notification
import tkinter as tk


class RSI_Tracker_GUI:
    def __init__(self, root):
        self.root = root
        self.root.configure(background='gray50')
        root.overrideredirect(True) 


       
        def start_move(event):
           root._offset_x = event.x_root - root.winfo_x()
           root._offset_y = event.y_root - root.winfo_y()

        def do_move(event):
           root.geometry(f"+{event.x_root - root._offset_x}+{event.y_root - root._offset_y}")

        root.bind("<Button-1>", start_move)
        root.bind("<B1-Motion>", do_move)

        self.root.title("RSI Tracker by EinfacheEnte")
        

        self.console_frame1 = Frame(root, bg="black")
        self.console_frame1.pack(side=LEFT, fill=BOTH, expand=True, padx=5, pady=5)
        
        self.console_frame2 = Frame(root, bg="black")
        self.console_frame2.pack(side=RIGHT, fill=BOTH, expand=True, padx=5, pady=5)


        self.rsi_console = ScrolledText(self.console_frame1, bg="gray11", fg="white", font=("Courier", 10))
        self.rsi_console.pack(fill=BOTH, expand=True, padx=5, pady=5)

        self.progress_console = ScrolledText(self.console_frame2, bg="gray11", fg="white", font=("Courier", 10))
        self.progress_console.pack(fill=BOTH, expand=True, padx=5, pady=5)


        threading.Thread(target=self.loop, daemon=True).start()

    def send_notification(self, title, message):
        """Send a desktop notification."""
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
        """Log messages to the RSI console with a specific color."""
        self.rsi_console.tag_configure(color, foreground=color)
        self.rsi_console.insert(END, message, color)
        self.rsi_console.insert(END, "\n")  
        self.rsi_console.see(END)

    def log_to_progress_console(self, message, color="white"):
        """Log messages to the progress console with a specific color."""
        self.progress_console.tag_configure(color, foreground=color)
        self.progress_console.insert(END, message, color)
        self.progress_console.insert(END, "\n") 
        self.progress_console.see(END)

    def track_rsi(self, symbol, interval, color):
        """Track RSI values for a given symbol."""
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
            self.log_to_progress_console(f"Getting analysis for {symbol} {round(rsi, 2)} RSI at {now}", color)
            if rsi <= 37:
                now = datetime.now().strftime('%H:%M:%S')
                message = f"{symbol} RSI ({interval}): {round(rsi, 2)} at {now}"
                self.log_to_rsi_console(message, color)

                # Send desktop notification
                threading.Thread(
                    target=lambda: self.send_notification(
                        title=f"RSI Alert: {symbol}",
                        message=f"{symbol} RSI is {round(rsi, 2)} at {now}"
                    ),
                    daemon=True
                ).start()
        except Exception as e:
            self.log_to_progress_console(f"Error tracking {symbol}: {str(e)}", "red")

    def loop(self):
        """Continuously track RSI values."""
        while True:
            self.track_rsi("BTCUSDT.P", Interval.INTERVAL_5_MINUTES, "orange")
            self.track_rsi("ETHUSDT.P", Interval.INTERVAL_5_MINUTES, "cyan")
            self.track_rsi("XRPUSDT.P", Interval.INTERVAL_1_MINUTE, "gray")
            self.track_rsi("SOLUSDT.P", Interval.INTERVAL_5_MINUTES, "DarkOrchid3")
            self.track_rsi("LTCUSDT.P", Interval.INTERVAL_5_MINUTES, "cyan")
            self.track_rsi("SHIBUSDT.P", Interval.INTERVAL_5_MINUTES, "red")
            self.track_rsi("DOGEUSDT.P", Interval.INTERVAL_5_MINUTES, "orange")
            time.sleep(10)


if __name__ == "__main__":
    root = Tk()
    app = RSI_Tracker_GUI(root)
    root.mainloop()
