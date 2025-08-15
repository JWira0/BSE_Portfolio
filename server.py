import asyncio
import threading
import websockets
from tkinter import *

root = Tk()


async def hello(websocket):
    name = await websocket.recv()
    print(f"Server Received: {name}")
    greeting = f"Hello {name}!"
    await websocket.send(greeting)
    print(f"Server Sent: {greeting}")

async def main():
    async with websockets.serve(hello, "localhost", 8765):
        asyncio.create_task(tk_loop())  # schedule tk_loop()
        await asyncio.Future()          # keep the program running forever


def run_tk():
    root.title('RC Car Control')
    def forward():
        
        return
    forwardButton = Button(root, text="Forward", command=forward).grid(row=1, column=1)
    backwardButton = Button(root, text="Backward").grid(row=1,column=2)
    leftButton = Button(root, text="Left").grid(row=1, column=3)
    rightButton = Button(root, text="Right").grid(row=1,column=4)
    stopButton = Button(root, text="Stop").grid(row=1,column=5)
    
async def tk_loop():
    while True:
        root.update()
        await asyncio.sleep(0.02)
    
    

if __name__ == "__main__":
    run_tk()
    # Run websocket server
    asyncio.run(main())
