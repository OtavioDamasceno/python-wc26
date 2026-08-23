# ⚽ API de Apostas Esportivas — Copa do Mundo 2026

API REST desenvolvida em **Python** para gerenciamento de uma plataforma de apostas esportivas baseada na Copa do Mundo de 2026.

O projeto foi desenvolvido como projeto prático durante o programa **Bolsa Futuro Digital**, com o objetivo de aplicar conceitos de desenvolvimento backend, construção de APIs REST, autenticação, persistência de dados, regras de negócio e integração com APIs externas.

---

## 📋 Sumário

- [Sobre o projeto](#-sobre-o-projeto)
- [Objetivos](#-objetivos)
- [Funcionalidades](#-funcionalidades)
- [Tecnologias](#️-tecnologias)
- [Arquitetura](#️-arquitetura)
- [Autenticação](#-autenticação)
- [Usuários](#-usuários)
- [Partidas](#️-partidas)
- [Odds](#-odds)
- [Sistema de apostas](#-sistema-de-apostas)
- [Saldo](#-saldo)
- [Multiplicação de apostas](#-multiplicação-de-apostas)
- [Ranking](#-ranking)
- [Banco de dados](#️-banco-de-dados)
- [Validações e regras de negócio](#-validações-e-regras-de-negócio)
- [Principais endpoints](#-principais-endpoints)
- [Histórias de usuário](#-histórias-de-usuário)
- [Histórias administrativas](#-histórias-administrativas)
- [Documentação da API](#-documentação-da-api)
- [Instalação](#-instalação)
- [Configuração do banco](#️-configuração-do-banco)
- [Variáveis de ambiente](#-variáveis-de-ambiente)
- [Executando o projeto](#️-executando-o-projeto)
- [Testando a API](#-testando-a-api)
- [Tratamento de erros](#️-tratamento-de-erros)
- [Segurança](#-segurança)
- [Solução de problemas](#-solução-de-problemas)
- [Possíveis melhorias](#-possíveis-melhorias)
- [Contexto acadêmico](#-contexto-acadêmico)
- [Autor](#-autor)

---

# 📋 Sobre o projeto

O projeto consiste em uma API REST de uma plataforma de apostas esportivas.

Os usuários possuem um saldo em pontos que pode ser utilizado para realizar apostas em partidas de futebol.

A aplicação possui diferentes níveis de acesso:

- **Usuário comum**
- **Administrador**

O usuário comum pode consultar partidas, realizar apostas, acompanhar seus resultados, consultar saldo e visualizar o ranking.

O administrador possui funcionalidades adicionais para gerenciamento de usuários, partidas e apostas.

Além disso, a aplicação possui integração com uma fonte externa para importação de partidas.

---

# 🎯 Objetivos

O principal objetivo do projeto é desenvolver uma aplicação backend completa utilizando Python, aplicando conceitos aprendidos durante a formação.

Entre os principais objetivos estão:

- Desenvolver uma API REST;
- Implementar autenticação utilizando JWT;
- Criar regras de autorização;
- Trabalhar com banco de dados relacional;
- Utilizar ORM;
- Criar relacionamentos entre entidades;
- Implementar validação de dados;
- Desenvolver regras de negócio;
- Implementar sistema de apostas;
- Trabalhar com saldo e pontos;
- Implementar cálculo de odds;
- Integrar a aplicação com uma API externa;
- Documentar a API;
- Utilizar Git para versionamento.

---

# 🚀 Funcionalidades

## 👤 Usuários

- Criar conta;
- Fazer login;
- Alterar senha;
- Consultar informações;
- Inativar conta;
- Consultar saldo;
- Consultar suas apostas.

## ⚽ Partidas

- Listar partidas;
- Consultar detalhes de uma partida;
- Consultar partidas disponíveis;
- Importar partidas;
- Encerrar partidas;
- Consultar odds.

## 🎲 Apostas

- Registrar apostas;
- Consultar apostas;
- Consultar status da aposta;
- Multiplicar apostas;
- Processar resultados;
- Atualizar saldo de acordo com os resultados.

## 🏆 Ranking

- Consultar classificação dos usuários;
- Ordenar usuários de acordo com seus resultados.

## 👨‍💼 Administração

- Listar usuários;
- Pesquisar usuários por CPF;
- Consultar apostas de uma partida;
- Importar partidas;
- Consultar detalhes das partidas;
- Consultar odds;
- Gerenciar partidas.

---

# 🛠️ Tecnologias

| Tecnologia | Utilização |
|---|---|
| **Python** | Linguagem principal |
| **FastAPI** | Framework para desenvolvimento da API |
| **SQLModel** | ORM e modelagem das entidades |
| **Pydantic** | Validação e serialização dos dados |
| **MySQL** | Banco de dados relacional |
| **JWT** | Autenticação |
| **Uvicorn** | Servidor ASGI |
| **Swagger / OpenAPI** | Documentação e testes da API |
| **Git / GitHub** | Versionamento |

---

# 🏗️ Arquitetura

A aplicação foi organizada de forma a separar responsabilidades entre as diferentes partes do sistema.

Fluxo simplificado:

```text
                         CLIENTE
                            │
                            ▼
                   ┌─────────────────┐
                   │      Routes     │
                   │   Endpoints API │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │     Services    │
                   │ Regras de negócio│
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │     Models      │
                   │    SQLModel     │
                   └────────┬────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │      MySQL      │
                   │ Banco de dados  │
                   └─────────────────┘
```

Também existe uma integração externa para importação das partidas:

```text
        API externa
             │
             ▼
       Requisição HTTP
             │
             ▼
      Processamento
             │
             ▼
      Validação dos dados
             │
             ▼
       Banco de dados
```

---

# 🔐 Autenticação

A API utiliza **JWT (JSON Web Token)** para autenticação.

O usuário realiza login e recebe um token.

Esse token deve ser enviado nas requisições protegidas:

```http
Authorization: Bearer SEU_TOKEN
```

Exemplo:

```http
GET /apostas/
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

O sistema utiliza o token para identificar o usuário que está realizando a operação.

---

# 👥 Controle de acesso

A aplicação possui diferentes níveis de permissão.

### Usuário comum

Possui acesso às funcionalidades relacionadas à própria conta e às apostas.

### Administrador

Possui permissões adicionais para gerenciamento da plataforma.

```text
Usuário
 ├── Consultar partidas
 ├── Realizar aposta
 ├── Consultar apostas
 ├── Consultar saldo
 └── Consultar ranking

Administrador
 ├── Todas as funcionalidades do usuário
 ├── Gerenciar usuários
 ├── Importar partidas
 ├── Consultar apostas de partidas
 └── Gerenciar partidas
```

---

# ⚽ Partidas

As partidas representam os eventos esportivos nos quais os usuários podem realizar apostas.

Uma partida possui informações como:

- Times participantes;
- Data da partida;
- Status;
- Odds;
- Resultado;
- Disponibilidade para apostas.

## Status da partida

O sistema utiliza estados para controlar o ciclo de vida de uma partida.

```text
AGENDADA
   │
   ▼
EM ANDAMENTO
   │
   ▼
ENCERRADA
   │
   ▼
PROCESSADA
```

As regras de negócio determinam em qual momento uma aposta pode ser realizada.

---

# 📥 Importação de partidas

Administradores podem importar partidas de uma API externa.

Endpoint:

```http
POST /partidas/importar
```

Processo:

```text
API externa
     │
     ▼
Busca das partidas
     │
     ▼
Validação
     │
     ▼
Verificação de duplicidade
     │
     ▼
Persistência no banco
```

A aplicação também possui mecanismo de fallback para permitir o funcionamento da importação quando a fonte externa principal não estiver disponível.

---

# 📊 Odds

As odds representam o multiplicador associado aos possíveis resultados de uma partida.

Exemplo:

```text
Time A vence → Odd 2.00
Empate       → Odd 3.50
Time B vence → Odd 2.80
```

De maneira simplificada:

```text
Aposta: 50 pontos
Odd:    2.00

Retorno potencial:
50 × 2.00 = 100 pontos
```

As odds podem ser influenciadas pela distribuição das apostas entre os resultados.

Quanto maior a concentração de apostas em determinado resultado, menor tende a ser sua odd.

---

# 🎲 Sistema de apostas

Uma aposta possui relação com:

```text
Usuário
   │
   │ 1:N
   ▼
Aposta
   │
   │ N:1
   ▼
Partida
```

Ao registrar uma aposta, a API valida:

- Se o usuário está autenticado;
- Se a partida existe;
- Se a partida permite apostas;
- Se o palpite é válido;
- Se o valor apostado é maior que zero;
- Se o usuário possui saldo suficiente.

Somente depois das validações a aposta é registrada.

## Exemplo de aposta

```json
{
  "id_partida": 1,
  "palpite": "time_a",
  "pontos_apostados": 50
}
```

Endpoint:

```http
POST /apostas/
```

---

# 💰 Saldo

Cada usuário possui um saldo em pontos.

Exemplo:

```text
Saldo inicial:       500 pontos
Aposta:               50 pontos
------------------------------
Saldo restante:      450 pontos
```

O sistema impede que o usuário realize uma aposta superior ao saldo disponível.

---

# ✖️ Multiplicação de apostas

A aplicação possui uma funcionalidade que permite multiplicar uma aposta.

O sistema calcula o custo adicional necessário para aumentar o multiplicador e verifica se o usuário possui saldo suficiente.

Exemplo:

```text
Aposta inicial:       50 pontos
Multiplicador:        1x

Novo multiplicador:   2x
```

---

# 🏆 Ranking

A aplicação possui um ranking dos usuários.

O ranking pode utilizar informações como:

- Pontuação;
- Resultados das apostas;
- Saldo;
- Desempenho.

O objetivo é apresentar uma classificação entre os participantes da plataforma.

---

# 🗄️ Banco de dados

O banco de dados utilizado é o **MySQL**.

A aplicação utiliza o **SQLModel** para realizar o mapeamento entre as entidades Python e as tabelas do banco.

Modelo simplificado:

```text
┌───────────────┐
│    Usuário    │
└───────┬───────┘
        │
        │ 1:N
        ▼
┌───────────────┐
│     Aposta    │
└───────┬───────┘
        │
        │ N:1
        ▼
┌───────────────┐
│    Partida    │
└───────────────┘
```

---

# 🧩 Validações e regras de negócio

A API possui validações para evitar operações inválidas.

### Aposta

- Partida precisa existir;
- Partida precisa estar em estado permitido;
- Partida não pode ter iniciado quando a regra de aposta exige que esteja agendada;
- Valor da aposta deve ser maior que zero;
- Usuário precisa possuir saldo suficiente;
- Palpite deve ser válido.

### Usuário

- Dados obrigatórios devem ser preenchidos;
- CPF deve obedecer às regras definidas pela aplicação;
- Senha deve ser validada;
- Usuário precisa estar ativo para realizar determinadas operações.

### Administrador

Endpoints administrativos exigem autenticação e perfil adequado.

---

# ⚠️ Tratamento de erros

A API utiliza códigos HTTP para representar diferentes situações.

| Código | Significado |
|---|---|
| `200` | Operação realizada com sucesso |
| `201` | Recurso criado |
| `400` | Requisição inválida |
| `401` | Não autenticado |
| `403` | Sem permissão |
| `404` | Recurso não encontrado |
| `409` | Conflito / regra de negócio |
| `422` | Dados inválidos |

Exemplo:

```json
{
  "detail": "Esta partida não está disponível para apostas."
}
```

---

# 📚 Principais endpoints

## 🔑 Autenticação

```http
POST /auth/login
```

## 👤 Usuários

```http
POST /usuarios/
GET /usuarios/
GET /usuarios/{id}
PUT /usuarios/{id}
```

## ⚽ Partidas

```http
GET /partidas/
GET /partidas/ativas
POST /partidas/
POST /partidas/importar
```

### Listar partidas disponíveis

```http
GET /partidas/ativas
```

### Importar partidas

```http
POST /partidas/importar
```

## 🎲 Apostas

```http
POST /apostas/
GET /apostas/
```

### Criar aposta

```http
POST /apostas/
```

Exemplo:

```json
{
  "id_partida": 1,
  "palpite": "time_a",
  "pontos_apostados": 50
}
```

### Multiplicar aposta

```http
POST /apostas/{id}/multiplicar
```

---

# 📖 Documentação da API

Depois de iniciar o servidor:

### Swagger UI

```text
http://localhost:8000/docs
```

### ReDoc

```text
http://localhost:8000/redoc
```

O Swagger permite testar os endpoints diretamente pelo navegador.

---

# 🚀 Instalação

## Pré-requisitos

- Python 3.11 ou superior;
- MySQL;
- Git.

## 1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DO_PROJETO>
```

## 2. Criar ambiente virtual

### Windows

```bash
python -m venv venv
venv\Scriptsctivate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Instalar dependências

```bash
pip install -r requirements.txt
```

---

# 🗄️ Configuração do banco de dados

Abra o MySQL e execute:

```sql
CREATE DATABASE apostas_esportivas;
```

---

# 🔐 Variáveis de ambiente

Crie um arquivo `.env` na raiz:

```env
DATABASE_URL=mysql+pymysql://root:SUA_SENHA@localhost:3306/apostas_esportivas
SECRET_KEY=sua_chave_secreta
```

Substitua `SUA_SENHA` pela senha do banco.

> Nunca envie o arquivo `.env` para o GitHub. Ele deve estar incluído no `.gitignore`.

---

# ▶️ Executando o projeto

Com o ambiente virtual ativado:

```bash
uvicorn app.main:app --reload
```

A API estará disponível em:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

---

# 🧪 Testando a API

Fluxo recomendado:

```text
1. Criar usuário
        ↓
2. Fazer login
        ↓
3. Copiar token JWT
        ↓
4. Autorizar no Swagger
        ↓
5. Consultar partidas
        ↓
6. Consultar partidas disponíveis
        ↓
7. Realizar aposta
        ↓
8. Consultar aposta
        ↓
9. Consultar saldo
        ↓
10. Multiplicar aposta
        ↓
11. Consultar ranking
```

Para funcionalidades administrativas:

```text
1. Autenticar como administrador
        ↓
2. Importar partidas
        ↓
3. Consultar usuários
        ↓
4. Consultar apostas
        ↓
5. Consultar partidas
```

---

# 🔑 Autorização no Swagger

Depois do login, copie o token retornado.

No Swagger:

```text
Authorize
```

Informe:

```text
Bearer SEU_TOKEN
```

Depois clique em `Authorize`.

---


> A estrutura acima representa a organização conceitual do projeto. Ajuste os nomes caso sejam diferentes na implementação atual.

---

# 📌 Histórias de usuário

| Código | Funcionalidade |
|---|---|
| **HU1** | Criar conta |
| **HU2** | Registrar aposta |
| **HU3** | Consultar status da aposta |
| **HU4** | Multiplicar aposta |
| **HU5** | Inativar conta |
| **HU6** | Trocar senha |
| **HU7** | Consultar resultados anteriores |
| **HU8** | Visualizar partidas disponíveis |
| **HU9** | Consultar saldo |
| **HU10** | Consultar ranking |

---

# 👨‍💼 Histórias administrativas

| Código | Funcionalidade |
|---|---|
| **HA1** | Listar usuários |
| **HA2** | Pesquisar usuário por CPF |
| **HA3** | Pesquisar apostas de uma partida |
| **HA4** | Importar partidas através de API |
| **HA5** | Consultar detalhes e odds da partida |

---

# 🔄 Fluxo geral da aplicação

```text
                    ┌───────────────┐
                    │    Usuário    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │     Login     │
                    └───────┬───────┘
                            │
                         JWT Token
                            │
                            ▼
                    ┌───────────────┐
                    │    Partidas   │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    Apostas    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    Saldo      │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    Resultado  │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    Ranking    │
                    └───────────────┘
```

---

# 🧠 Conceitos aplicados

- Python;
- Programação orientada a objetos;
- APIs REST;
- FastAPI;
- HTTP;
- JSON;
- JWT;
- Autenticação;
- Autorização;
- ORM;
- SQLModel;
- MySQL;
- Relacionamentos entre tabelas;
- CRUD;
- Pydantic;
- Validação de dados;
- Regras de negócio;
- Tratamento de exceções;
- Integração com APIs externas;
- Controle de saldo;
- Cálculo de odds;
- Git;
- GitHub;
- Documentação de APIs.

---

# 🔒 Segurança

A aplicação utiliza:

- Autenticação baseada em JWT;
- Controle de acesso por perfil;
- Validação das requisições;
- Proteção dos endpoints administrativos;
- Variáveis de ambiente;
- Validação das regras de negócio;
- Controle de saldo;
- Verificação da disponibilidade das partidas.

Informações sensíveis, como senhas e chaves secretas, não devem ser armazenadas diretamente no código-fonte.

---

# 🐛 Solução de problemas

## Erro ao instalar dependências

```bash
venv\Scriptsctivate
pip install -r requirements.txt
```

## Erro de conexão com MySQL

Verifique:

- Se o MySQL está executando;
- Usuário;
- Senha;
- Porta;
- Nome do banco;
- `DATABASE_URL`.

## Porta 8000 ocupada

```bash
uvicorn app.main:app --reload --port 8001
```

Acesse:

```text
http://localhost:8001/docs
```

## ModuleNotFoundError

```bash
pip install -r requirements.txt
```

Confirme também que o comando está sendo executado na raiz do projeto.

---

# 🛑 Encerrando o servidor

Para parar a aplicação:

```text
CTRL + C
```

Para sair do ambiente virtual:

```bash
deactivate
```

---

# 📈 Possíveis melhorias futuras

- Interface frontend;
- Testes unitários;
- Testes de integração;
- Testes automatizados dos endpoints;
- Sistema de migrations;
- Logs estruturados;
- Monitoramento;
- Cache;
- Melhorias no sistema de odds;
- Integração com API esportiva em produção;
- Deploy em ambiente cloud;
- CI/CD;
- Docker;
- Docker Compose;
- Sistema de notificações;
- Histórico detalhado de apostas;
- Dashboard administrativo.

---

# 🎓 Contexto acadêmico

Este projeto foi desenvolvido como projeto prático durante o programa **Bolsa Futuro Digital**, com foco na formação e capacitação para atuação como desenvolvedor backend utilizando Python.

A proposta foi aplicar os conhecimentos adquiridos durante a formação em um sistema completo, envolvendo:

- Desenvolvimento de API;
- Banco de dados;
- Autenticação;
- Regras de negócio;
- Integração externa;
- Documentação;
- Organização de código.

---

# 👨‍💻 Autor

## Otávio Damasceno

Desenvolvedor em formação com foco em **Backend e desenvolvimento de APIs utilizando Python**.

Este projeto representa uma aplicação prática dos conhecimentos adquiridos durante a formação em desenvolvimento backend.

---

# 📄 Licença

Projeto desenvolvido para fins **educacionais e de demonstração**.

---

# ⭐ Considerações finais

Este projeto foi desenvolvido com o objetivo de demonstrar, na prática, a construção de uma API backend completa utilizando Python e tecnologias modernas do ecossistema.

A aplicação reúne autenticação, usuários, partidas, apostas, odds, saldo, ranking, banco de dados, regras de negócio e integração com serviços externos em um único projeto.
