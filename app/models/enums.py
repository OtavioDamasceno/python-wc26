from enum import Enum

class StatusUsuario(str, Enum):
    ativo = "ativo"
    inativo = "inativo"
 
 
class StatusAposta(str, Enum):
    pendente = "pendente"   
    ganha = "ganha"         
    perdida = "perdida"     
    devolvida = "devolvida" 
 
 
class StatusPartida(str, Enum):
    agendada = "agendada"  
    em_andamento = "em_andamento"
    finalizada = "finalizada"
 
 
class Palpite(str, Enum):
    time_a = "time_a"   
    time_b = "time_b"  
    empate = "empate"   
 
 
class ResultadoPartida(str, Enum):
    time_a = "time_a"
    time_b = "time_b"
    empate = "empate"