# Projeto 8 - Dorothy, Bot Transformer Para Atendimento ao Cliente

# Pacote para manipulação dos dados em formato JSON
import json

# Pacote para requisições
import requests

# Framework para criação de aplicações web
import streamlit as st  

# Para criação e execução de agentes conversacionais
from langchain.agents import ConversationalChatAgent, AgentExecutor  

# Callback para interação com a interface do Streamlit
from langchain_community.callbacks import StreamlitCallbackHandler  

# Integração com o modelo de linguagem da OpenAI
from langchain_openai import ChatOpenAI  

# Memória para armazenar o histórico de conversa
from langchain.memory import ConversationBufferMemory  

# Histórico de mensagens para o Streamlit
from langchain_community.chat_message_histories import StreamlitChatMessageHistory 

# Ferramenta de busca DuckDuckGo para o agente 
from langchain_community.tools import DuckDuckGoSearchRun  

# Remove warnings
import warnings
warnings.filterwarnings('ignore')

# Configuração do título da página
st.set_page_config(page_title = "Dorothy")

# Criação de colunas para layout da página
# Define a proporção das colunas
col1, col4 = st.columns([4, 1])  

# Configuração da primeira coluna para exibir o título do projeto
with col1:
    st.title("Dorothy - Bot Transformer Para Atendimento ao Cliente")

# Campo para entrada da chave de API da OpenAI
openai_api_key = st.sidebar.text_input("OpenAI API Key", type = "password")

# Inicialização do histórico de mensagens
# https://python.langchain.com/docs/integrations/memory/streamlit_chat_message_history/
msgs = StreamlitChatMessageHistory()

# Configuração da memória do chat
# https://python.langchain.com/docs/modules/memory/types/buffer/
memory = ConversationBufferMemory(chat_memory = msgs, 
                                  return_messages = True, 
                                  memory_key = "chat_history", 
                                  output_key = "output")

# Verificação para limpar o histórico de mensagens ou iniciar a conversa
if len(msgs.messages) == 0 or st.sidebar.button("Reset"):
    msgs.clear()
    msgs.add_ai_message("Como eu posso ajudar você?")
    st.session_state.steps = {}

# Definição de avatares para os participantes da conversa
avatars = {"human": "user", "ai": "assistant"}

# Loop para exibir mensagens no chat
# Itera sobre cada mensagem no histórico de mensagens
for idx, msg in enumerate(msgs.messages):  

    # Cria uma mensagem no chat com o avatar correspondente ao tipo de usuário (humano ou IA)
    with st.chat_message(avatars[msg.type]):  

        # Itera sobre os passos armazenados para cada mensagem, se houver
        for step in st.session_state.steps.get(str(idx), []):  

            # Se o passo atual indica uma exceção, pula para o próximo passo
            if step[0].tool == "_Exception":  
                continue

            # Cria um expander para cada ferramenta usada na resposta, mostrando o input
            with st.expander(f"✅ **{step[0].tool}**: {step[0].tool_input}"): 

                # Exibe o log de execução da ferramenta 
                st.write(step[0].log)  

                # Exibe o resultado da execução da ferramenta
                st.write(f"**{step[1]}**")  

        # Exibe o conteúdo da mensagem no chat
        st.write(msg.content)  

# Campo de entrada para novas mensagens do usuário
if prompt := st.chat_input(placeholder = "Digite uma pergunta para começar!"):
    st.chat_message("user").write(prompt)

    # Verificação da chave de API
    if not openai_api_key:
        st.info("Adicione sua OpenAI API key para continuar.")
        st.stop()

    # Configuração do modelo de linguagem da OpenAI
    # https://python.langchain.com/docs/integrations/chat/openai/
    llm_dsa = ChatOpenAI(openai_api_key = openai_api_key, streaming = True)
    
    # Configuração da ferramenta de busca do agente
    # https://api.python.langchain.com/en/latest/tools/langchain_community.tools.ddg_search.tool.DuckDuckGoSearchRun.html
    mecanismo_busca = [DuckDuckGoSearchRun(name = "Search")]
    
    # Criação do agente conversacional com a ferramenta de busca
    # https://api.python.langchain.com/en/latest/agents/langchain.agents.conversational_chat.base.ConversationalChatAgent.html
    chat_dsa_agent = ConversationalChatAgent.from_llm_and_tools(llm = llm_dsa, tools = mecanismo_busca)
    
    # Executor para o agente, incluindo memória e tratamento de erros
    # https://api.python.langchain.com/en/latest/agents/langchain.agents.agent.AgentExecutor.html
    executor = AgentExecutor.from_agent_and_tools(agent = chat_dsa_agent,
                                                  tools = mecanismo_busca,
                                                  memory = memory,
                                                  return_intermediate_steps = True,
                                                  handle_parsing_errors = True)

    # Exibição da resposta do assistente
    with st.chat_message("assistant"):

        # Callback para o Streamlit
        # https://api.python.langchain.com/en/latest/callbacks/langchain_community.callbacks.streamlit.streamlit_callback_handler.StreamlitCallbackHandler.html
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts = False)  
        response = executor(prompt, callbacks = [st_cb])
        st.write(response["output"])

        # Armazenamento dos passos intermediários
        st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]  

# Fim

