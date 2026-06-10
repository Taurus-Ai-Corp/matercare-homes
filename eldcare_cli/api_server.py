"""API Server entry point."""

import uvicorn


def main():
    """Run API server."""
    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


if __name__ == "__main__":
    main()
