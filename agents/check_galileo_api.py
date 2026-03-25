try:
    from galileo import galileo_context
    from galileo.handlers.langchain import GalileoAsyncCallback
    print("SUCCESS: galileo_context and GalileoAsyncCallback are available!")
except ImportError as e:
    print(f"FAILED: {e}")
