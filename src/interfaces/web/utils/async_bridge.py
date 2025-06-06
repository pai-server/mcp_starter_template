"""AsyncBridge for Streamlit to handle MCP async operations."""

import asyncio
import logging
from threading import Thread


class AsyncBridge:
    """Bridge between Streamlit's synchronous execution and MCP's async operations."""
    
    def __init__(self):
        self.loop = None
        self.thread = None
        self._start_loop()
    
    def _start_loop(self):
        """Start the async event loop in a separate thread."""
        self.loop = asyncio.new_event_loop()
        self.thread = Thread(target=self._run_loop, daemon=True)
        self.thread.start()
    
    def _run_loop(self):
        """Run the event loop."""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
    
    def run_async(self, coro):
        """Execute a coroutine and return the result."""
        if not self.loop or not self.thread.is_alive():
            self._start_loop()
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result(timeout=30)  # 30 second timeout
    
    def cleanup(self):
        """Clean up the event loop."""
        if self.loop and self.loop.is_running():
            logging.info("AsyncBridge: Stopping event loop...")
            self.loop.call_soon_threadsafe(self.loop.stop)
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=5)
                if self.thread.is_alive():
                    logging.warning("AsyncBridge: Thread did not join in time.")
            self.loop.close()
            logging.info("AsyncBridge: Event loop stopped and closed.")
        self.loop = None
        self.thread = None 