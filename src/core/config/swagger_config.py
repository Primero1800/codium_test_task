from fastapi import FastAPI, Request
from fastapi.openapi.docs import (
    get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html, get_redoc_html
)
from fastapi import status

from src.core.settings import settings


class SwaggerConfigurer:

    @staticmethod
    async def get_routes(application: FastAPI):
        from src.scripts.get_routes import get_routes as scrypt_get_routes
        return await scrypt_get_routes(
            application=application,
            path=True,
            tags=False,
            methods=True,
        )

    @staticmethod
    def delete_router_tag(application: FastAPI):
        for route in application.routes:
            if hasattr(route, "tags"):
                if isinstance(route.tags, list) and len(route.tags) > 1:
                    del route.tags[0]

    @staticmethod
    def config_swagger(app: FastAPI, app_title='Unknown application'):

        @app.get(
            '/docs',
            status_code=status.HTTP_200_OK,
            tags=[settings.tags.SWAGGER_TAG],
        )
        async def custom_swagger_ui_html(
                request: Request,
        ):
            return get_swagger_ui_html(
                openapi_url=app.openapi_url,
                title=app_title + ' Swagger UI',
                oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
                # swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
                swagger_js_url=f"/static/swagger/js/swagger-ui-bundle.js",
                # swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
                swagger_css_url=f"/static/swagger/css/swagger-ui.css"
            )

        @app.get(
            app.swagger_ui_oauth2_redirect_url,
            include_in_schema=False
        )
        async def swagger_ui_redirect(
                request: Request
        ):
            return get_swagger_ui_oauth2_redirect_html()

        @app.get(
            "/redoc",
            status_code=status.HTTP_200_OK,
            tags=[settings.tags.SWAGGER_TAG]
        )
        async def redoc_html(
                request: Request
        ):
            return get_redoc_html(
                openapi_url=app.openapi_url,
                title=app.title + " - ReDoc",
                # redoc_js_url="https://unpkg.com/redoc@next/bundles/redoc.standalone.js",
                redoc_js_url=f"/static/swagger/js/redoc.standalone.js"
            )
