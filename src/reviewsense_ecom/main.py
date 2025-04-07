from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router.routes import router


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    Returns:
        FastAPI: Configured application instance.
    """
    app_instance = FastAPI(  # Changed variable name to avoid shadowing
        title="ReviewSense",
        description="AI-powered Product Review Analysis Platform"
    )

    # Include routes
    app_instance.include_router(router)

    # Add CORS middleware
    app_instance.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app_instance  # Return the instance


# Initialize FastAPI app
app = create_app()

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=8002)
