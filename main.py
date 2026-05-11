from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta, time

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SALAS_DISPONIVEIS = 1 
DURACAO_SERVICO = 60
agendamentos = []

@app.post("/api/agendamentos")
def salvar_agendamento(dados: dict):
    novo_inicio = datetime.fromisoformat(dados['horario'])
    novo_fim = novo_inicio + timedelta(minutes=DURACAO_SERVICO)
    
    # Algoritmo de Particionamento (Conflitos)
    conflitos = sum(1 for ag in agendamentos if not (novo_fim <= datetime.fromisoformat(ag['horario']) or novo_inicio >= datetime.fromisoformat(ag['horario']) + timedelta(minutes=DURACAO_SERVICO)))
            
    if conflitos >= SALAS_DISPONIVEIS:
        raise HTTPException(status_code=400, detail="Capacidade máxima atingida para este horário.")

    agendamentos.append(dados)
    agendamentos.sort(key=lambda x: x['horario'])
    return {"status": "sucesso", "mensagem": "Registro confirmado!", "finalizacao": novo_fim.strftime('%H:%M')}

@app.get("/api/agendamentos")
def listar_tudo():
    agora = datetime.now()
    # Criamos categorias baseadas no tempo (Lógica de Escalonamento)
    resultado = {
        "aguardando": [],
        "em_atendimento": [],
        "concluidos": []
    }
    
    for ag in agendamentos:
        inicio = datetime.fromisoformat(ag['horario'])
        fim = inicio + timedelta(minutes=DURACAO_SERVICO)
        
        if agora < inicio:
            resultado["aguardando"].append(ag)
        elif inicio <= agora <= fim:
            resultado["em_atendimento"].append(ag)
        else:
            resultado["concluidos"].append(ag)
            
    return resultado

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)