from api.endpoints import init_fastapi, router

app = init_fastapi()
app.include_router(router)



