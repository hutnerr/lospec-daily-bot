import sys
import time
from colorama import Fore, Style, Back, init

init(autoreset=True) # initalize colorama

class Clogger:
    debug_enabled = True
    disabled = False
    use_timestamps = True
    
    @staticmethod
    def _get_timestamp():
        """Get formatted timestamp."""
        if Clogger.use_timestamps:
            return Back.BLACK + Fore.GREEN + time.strftime("%Y-%m-%d %H:%M:%S EST", time.localtime()) + Back.RESET + " "
        return ""
    
    @staticmethod
    def _log(tag: str, msg: str, color: str = ""):
        """Internal logging method."""
        if not Clogger.disabled:
            timestamp = Clogger._get_timestamp()
            print(f"{timestamp}{color}{tag:<8}{Style.RESET_ALL} | {msg}")
    
    @staticmethod
    def log(tag: str, msg: str):
        """Log with custom tag."""
        formatted_tag = f"[{tag.upper()}]"
        Clogger._log(formatted_tag, msg, Fore.CYAN)
    
    @staticmethod
    def error(msg: str):
        """Log error message."""
        Clogger._log("[ERROR]", msg, Fore.RED)
    
    @staticmethod
    def debug(msg: str):
        """Log debug message (only if debug_enabled)."""
        if Clogger.debug_enabled:
            Clogger._log("[DEBUG]", msg, Fore.MAGENTA)
    
    @staticmethod
    def action(msg: str):
        """Log action message."""
        Clogger._log("[ACTION]", msg, Fore.GREEN)
    
    @staticmethod
    def info(msg: str):
        """Log info message."""
        Clogger._log("[INFO]", msg, Fore.BLUE)


# USAGE EXAMPLE
if __name__ == "__main__":
    Clogger.info("Initialized Clogger")
    Clogger.log("state", "Player changed state")
    Clogger.error("X went wrong")
    Clogger.debug("This is a debug message")
    Clogger.action("User clicked button")