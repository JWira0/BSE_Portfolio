import asyncio
import threading
import websockets
from tkinter import *

async def hello(websocket):
    name = await websocket.recv()
    print(f"Server Received: {name}")
    greeting = f"Hello {name}!"
    await websocket.send(greeting)
    print(f"Server Sent: {greeting}")

async def main():
    async with websockets.serve(hello, "localhost", 8765):
        await asyncio.Future()  # runs forever

def run_tk():
    root = Tk()
    root.title('RC Car Control')
    def forward():
        return
    
    forwardButton = Button(root, text="Forward").grid(row=1, column=1)
    backwardButton = Button(root, text="Backward").grid(row=1,column=2)
    leftButton = Button(root, text="Left").grid(row=1, column=3)
    rightButton = Button(root, text="Right").grid(row=1,column=4)
    stopButton = Button(root, text="Stop").grid(row=1,column=5)
    root.mainloop()

if __name__ == "__main__":
    # Start Tkinter in a separate thread
    threading.Thread(target=run_tk, daemon=True).start()

    # Run websocket server
    asyncio.run(main())
