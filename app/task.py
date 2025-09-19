import asyncio


async def write_notification(email: str, message=""):
    await asyncio.sleep(20)
    with open("log.txt", "a") as file:
        content = f"Notification for {email}: {message}\n"
        file.write(content)
