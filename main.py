from fasthtml.common import *

app, rt = fast_app()

@rt('/')
def get():
    return "sondaggi nazionali - testing"

serve()
