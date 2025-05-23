from fastapi import FastAPI, APIRouter


async def get_routes(application: FastAPI | APIRouter, path=True, tags=True, methods=True, deps=False, desc=False):
    routes_info = []
    for route in application.routes:
        route_dict = {}
        if path:
            route_dict['path'] = route.path
        if tags:
            route_dict['tags'] = route.tags if hasattr(route, "tags") else []
        if methods:
            route_dict['methods'] = route.methods if hasattr(route, "methods") else []
        if deps:
            dependencies = route.dependencies if hasattr(route, 'dependencies') else []
            route_dict['dependencies'] = [str(dep) for dep in dependencies]
        if desc:
            route_dict['description'] = route.description if hasattr(route, 'description') else None
        routes_info.append(route_dict)
    return routes_info
