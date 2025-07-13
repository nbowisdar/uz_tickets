import asyncio


async def do_smth():
    try:
        print("Task started...")
        await asyncio.sleep(10)  # Simulate some work
        print("Task finished.")
    except asyncio.CancelledError:
        print("Task was cancelled!")
    finally:
        print("Task cleanup (e.g., closing resources).")

async def main():
    parsing_task = asyncio.create_task(do_smth())
    
    # Let the task run for a short while
    await asyncio.sleep(1) 
    
    print("Attempting to cancel the task...")
    parsing_task.cancel()
    
    # Wait for the task to actually complete its cancellation or finish
    # It's important to await the task even after cancelling to handle CancelledError
    try:
        await parsing_task
    except asyncio.CancelledError:
        print("Main caught CancelledError from the task (this is normal).")

if __name__ == "__main__":
    asyncio.run(main())