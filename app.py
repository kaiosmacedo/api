from fastapi import FastAPI

app = FastAPI()

@app.get('/pessoas')
async def index():
    return {'Olá': 'Mundo'} 

@app.post('/pessoas')
async def index():
    return {'Olá': 'Mundo'} 

@app.patch('/pessoas')
async def index():
    return {'Olá': 'Mundo'} 

@app.delete('/pessoas')
async def index():
    return {'Olá': 'Mundo'} 

@app.put('/pessoas')
async def index():
    return {'Olá': 'Mundo'} 
