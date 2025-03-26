import asyncio
from typing import List, Optional
import chainlit as cl

async def send_message(content:str, actions:Optional[List[cl.Action]] = None):
    if actions:
        await cl.Message(content = content, actions = actions).send()
        return
    await cl.Message(content = content).send()
    return

async def send_animated_message(
    base_msg: str, 
    frames: List[str], 
    interval: float = 0.8, 
    timeout: float = None
) -> None:
    """
    Enhanced generic animated message display
    
    Args:
        base_msg (str): Base message to display
        frames (List[str]): Animation frames
        interval (float): Time between frame updates
        timeout (float, optional): Maximum animation duration
    """
    msg = cl.Message(content=base_msg)
    await msg.send()
    
    start_time = asyncio.get_event_loop().time()
    progress = 0
    
    try:
        while timeout is None or (asyncio.get_event_loop().time() - start_time) < timeout:
            current_frame = frames[progress % len(frames)]
            msg.content = f"{current_frame} {base_msg}"
            await msg.update()
            
            progress += 1
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        msg.content = base_msg
        await msg.update()
