'''
    App streamlit de formulário para agariar as opniões do estudantes
    
    ---Objetivo:
        -Criar um formulário dinâmico e de fácil acesso para os alunos
        -Enteder as necessidades para desenvolver de forma rápida e coesa
                    
        *Solução:
            Criar um formulário no streamlit com API da googlesheets.
'''
# importando bibliotecas

import pandas as pd 
import streamlit as st
import json
from streamlit_gsheets import GSheetsConnection

# Variáveis globais

OPCOES = [
    'Muito bom',
    'Bom',
    'Regular',
    'Ruim',
    'Muito Ruim'
]

# Conectando com o Google Sheets
conn = st.connection('gsheets', type=GSheetsConnection)

# Lendo cursos e disciplinas
with open('data/filtro_curso_disciplinas.json') as f:
    filtro = json.load(f)

# Estanciando uma cópia do formulário
ava_data = conn.read(worksheet='AVA', usecol=list(range(3)), ttl=5)
disciplina_data = conn.read(worksheet='Disciplina', usecol=list(range(7)), ttl=5)

# Removendo linhas completamente vazias
ava_data = ava_data.dropna(how='all')
disciplina_data = disciplina_data.dropna(how='all')

# Inicializando session_state
if 'curso' not in st.session_state:
    st.session_state.curso = None
if 'disciplina' not in st.session_state:
    st.session_state.disciplina = None

# Título
st.title("Formulário de Opiniões dos Estudantes")

st.write('### Formulário anônimo')

# Seleção de curso (fora do form)
curso = st.selectbox(
    "Selecione o seu curso:",
    options=filtro,
    key='curso'
)

if curso:
    q4 = st.multiselect(
        "Selecione a(s) disciplina(s) que está realizando:",
        options=filtro[st.session_state.curso]
    )

if curso and len(q4) > 0:
    with st.form("student_form"):
        st.write('O AVA (Ambiente Virtual de Aprendizagem) é uma plataforma virtual de aprendizagem e é de fácil navegação e uso.')

        q1 = st.radio("Como você avalia a **usabilidade** do AVA?", OPCOES , horizontal=True)
        q2 = st.radio("Os recursos e funcionalidades do AVA (fóruns, envio de atividades," \
                        "acesso ao conteúdo, etc.) atendem às necessidades da disciplina.", OPCOES, horizontal=True)
        q3 = st.radio("Os tutores e professores estão disponíveis e prestam suporte adequado quando solicitado.", OPCOES, horizontal=True)

        # Mostra o curso selecionado dentro do form
        st.write(f"Curso selecionado: {curso}")
        
        for disciplina in q4:
            st.write(f"## {disciplina}")
            disc_q1 = st.radio('## As atividades e avaliações propostas contribuem para o meu aprendizado.', OPCOES , key=f"disc_q1_{disciplina}", horizontal=True) # definindo keys(id) para as questoes
            disc_q2 = st.radio('## Recebo retorno adequado e em tempo hábil das atividades avaliativas.',  OPCOES, key=f"disc_q2_{disciplina}", horizontal=True)
            disc_q3 = st.radio('## Os conteúdos das disciplinas são atualizados e relevantes para minha formação.', OPCOES, key=f"disc_q3_{disciplina}", horizontal=True)
            disc_q4 = st.radio('## O material didático(vídeo, apostilas, slides, etc.) é claro, bem elaborado e de fácil compreensão', OPCOES, key=f"disc_q4_{disciplina}", horizontal=True)
            disc_q5 = st.radio('## As aulas síncronas contribuem para o meu aprendizado nas disciplinas EAD.', OPCOES, key=f"disc_q5_{disciplina}", horizontal=True)

        submitted = st.form_submit_button('Enviar')

        if submitted:

            disc_respostas = pd.DataFrame() #estanciando variável para concatenação

            #preenchendo a primeira sheet do formulário
            ava_respostas = pd.DataFrame({
                "primeiraQuestao": [q1],
                "segundaQuestao": [q2],
                "terceiraQuestao": [q3],

            })
            
            #Criando um auxiliar para receber os valores das respostas do 2º sheet e depois concatenar na variavel estanciada            
            for disciplina in q4:
                aux = pd.DataFrame({
                    "curso": [curso],
                    "disciplina": [disciplina],
                    "disc_qst_um": [st.session_state[f"disc_q1_{disciplina}"]], #Passando a resposta com o parametro key da questao
                    "disc_qst_dois": [st.session_state[f"disc_q2_{disciplina}"]],
                    "disc_qst_tres": [st.session_state[f"disc_q3_{disciplina}"]],
                    "disc_qst_quatro": [st.session_state[f"disc_q4_{disciplina}"]],
                    "disc_qst_cinco": [st.session_state[f"disc_q5_{disciplina}"]]
                })
                #concatenando as respostas para cada laço do for
                disc_respostas = pd.concat([disc_respostas, aux], ignore_index=True)
                
            #atualiazando as variáveis estanciadas das disciplinas
            updated_ava = pd.concat([ava_data, ava_respostas], ignore_index=True)
            updated_disciplina = pd.concat([disciplina_data, disc_respostas], ignore_index=True)

            #Escrevendo no formulário
            conn.update(worksheet='AVA', data=updated_ava)
            conn.update(worksheet='Disciplina', data=updated_disciplina)

            st.success('Formulário enviado com sucesso!')