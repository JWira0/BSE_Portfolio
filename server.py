import asyncio
import websockets
from tkinter import *

root = Tk(None,None)
myLabel = Label(root, text="Hello World!")

myLabel.pack()

root.mainloop()
async def hello(websocket):
    name = await websocket.recv()
    print(f'Server Received: {name}')
    greeting = f'Hello {name}!'
    
    await websocket.send(greeting)
    print(f'Server Sent: {greeting}')
    
    
async def main():
    async with websockets.serve(hello, "localhost", 8765):
        await asyncio.Future() #runs forever
        
if __name__ == "__main__":
    asyncio.run(main())