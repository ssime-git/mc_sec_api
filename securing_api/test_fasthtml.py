from fasthtml.common import *

app, rt = fast_app()

@rt('/')
def get(): 
    return Div(P('Hello World!'), hx_get="/change")

@rt('/change')
def change():
    return P('Nice to be here!')

if __name__ == "__main__":
    serve(port=5001)
