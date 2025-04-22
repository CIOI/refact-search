import uvicorn

if __name__ == "__main__":
    """
    Run the AI API server.

    Args:
    - --env: The environment to run the server in. Default is "dev".
    """
    host = "0.0.0.0"
    port = 8100

    uvicorn.run(
        "src.app:app",  # app.py 파일의 app 변수를 가리킴
        host=host,
        port=port,
        reload=True,
        log_level="info",
    )
