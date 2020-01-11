import statsapp

app = statsapp.create_app()
app.app_context().__enter__()
