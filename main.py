from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, Field
import json  # salvar os pokémons num arquivo json

app = FastAPI()

pokemon_db = {
    1: {"nome": "Pikachu", "tipo": "Elétrico", "nivel": 25},
    2: {"nome": "Bulbasaur", "tipo": "Grama/Veneno", "nivel": 15},
    3: {"nome": "Charmander", "tipo": "Fogo", "nivel": 18},
    4: {"nome": "Squirtle", "tipo": "Água", "nivel": 20},
    5: {"nome": "Gengar", "tipo": "Fantasma/Veneno", "nivel": 35}
}

class Pokemon(BaseModel):
    nome: str
    tipo: str
    nivel: int = Field(..., ge=1, description="Nível do Pokémon deve ser maior ou igual a 1")

# Listar todos os pokémons na lista, com filtros opcionais e validação de texto
@app.get("/pokemons/")
async def get_all_pokemons(
    nome: str | None = Query(None, min_length=2, max_length=50, description="Filtra pelo nome do Pokémon"),
    tipo: str | None = Query(None, min_length=3, max_length=50, description="Filtra pelo tipo do Pokémon")
):
    resultados = {}
    for id_pokemon, pokemon in pokemon_db.items():
        if nome and nome.lower() not in pokemon["nome"].lower():
            continue
        if tipo and tipo.lower() not in pokemon["tipo"].lower():
            continue
        resultados[id_pokemon] = pokemon
    return resultados

# Buscar pokémon por id com validação do parâmetro de rota
@app.get("/pokemons/{pokemon_id}")
async def read_pokemon(
    pokemon_id: int = Path(..., ge=1, description="ID do Pokémon deve ser maior ou igual a 1")
):
    pokemon = pokemon_db.get(pokemon_id)
    if pokemon:
        return pokemon
    raise HTTPException(status_code=404, detail="Pokémon não encontrado")

# Criar um novo pokémon
@app.post("/pokemons/", status_code=201)
async def create_pokemon(pokemon: Pokemon):
    novo_id = max(pokemon_db.keys()) + 1 if pokemon_db else 1
    pokemon_db[novo_id] = pokemon.dict()
    salvar_pokemons(pokemon_db)
    return {"id": novo_id, **pokemon.dict()}

# Deletar um pokémon com validação do parâmetro de rota
@app.delete("/pokemons/deletar/{pokemon_id}")
async def delete_pokemon(
    pokemon_id: int = Path(..., ge=1, description="ID do Pokémon deve ser maior ou igual a 1")
):
    if pokemon_id not in pokemon_db:
        raise HTTPException(status_code=404, detail="Pokémon que você quer excluir não existe")
    del pokemon_db[pokemon_id]
    salvar_pokemons(pokemon_db)
    return {"mensagem": "Pokémon deletado com sucesso"}

# Atualizar pokémon pela chave primária com validação do parâmetro de rota
@app.put("/pokemons/atualizar/{pokemon_id}")
async def update_pokemon(
    pokemon_id: int = Path(..., ge=1, description="ID do Pokémon deve ser maior ou igual a 1"),
    pokemon: Pokemon = ...
):
    if pokemon_id in pokemon_db:
        pokemon_db[pokemon_id] = pokemon.dict()
        salvar_pokemons(pokemon_db)
        return {"mensagem": "Pokémon atualizado com sucesso", "pokemon": pokemon_db[pokemon_id]}
    raise HTTPException(status_code=404, detail="Pokémon não encontrado")

# +++++++++++++++++++++++++++++++

arquivo_db = 'pokemons.json'

def carregar_pokemons():
    try:
        with open(arquivo_db, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def salvar_pokemons(db):
    with open(arquivo_db, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)
