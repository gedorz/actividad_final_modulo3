from endpoints.endpoints import init_fastapi, router

app = init_fastapi()
app.include_router(router)


@app.get("/api/openapi.json", include_in_schema=False)
def openapi_proxy_alias():
	return app.openapi()



