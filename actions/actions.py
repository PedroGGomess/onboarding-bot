"""
Custom Actions para o Bot de Onboarding da The100s.

Implementa todas as ações personalizadas necessárias para o processo de onboarding
dos novos colaboradores da The100s.
"""

import logging
from typing import Any, Dict, List, Optional, Text

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dados do Quiz (MVP — hardcoded; substituir por base de dados no futuro)
# ---------------------------------------------------------------------------

QUIZ_PERGUNTAS = [
    {
        "id": 1,
        "pergunta": (
            "❓ **Pergunta 1/3:** Qual é a missão da The100s?\n\n"
            "A) Ser a maior empresa do mundo\n"
            "B) Proporcionar soluções de qualidade superior, mantendo um ambiente positivo e inclusivo\n"
            "C) Maximizar o lucro a qualquer custo\n"
            "D) Reduzir custos operacionais"
        ),
        "resposta_correta": "b",
        "explicacao": (
            "✅ A missão da The100s é proporcionar soluções de qualidade superior "
            "aos nossos clientes, mantendo um ambiente de trabalho positivo e inclusivo."
        ),
    },
    {
        "id": 2,
        "pergunta": (
            "❓ **Pergunta 2/3:** Qual dos seguintes NÃO é um valor da The100s?\n\n"
            "A) Integridade\n"
            "B) Competição interna\n"
            "C) Inovação\n"
            "D) Trabalho em Equipa"
        ),
        "resposta_correta": "b",
        "explicacao": (
            "✅ Os valores da The100s são: Integridade, Inovação, Excelência, "
            "Trabalho em Equipa e Respeito. A 'Competição interna' não faz parte dos nossos valores."
        ),
    },
    {
        "id": 3,
        "pergunta": (
            "❓ **Pergunta 3/3:** Quantos dias úteis de férias tem um colaborador da The100s por ano?\n\n"
            "A) 20 dias\n"
            "B) 25 dias\n"
            "C) 22 dias\n"
            "D) 30 dias"
        ),
        "resposta_correta": "c",
        "explicacao": (
            "✅ Os colaboradores da The100s têm direito a 22 dias úteis de férias "
            "por ano, conforme a legislação laboral portuguesa."
        ),
    },
]


def _obter_nome_formatado(tracker: Tracker) -> str:
    """Obtém o nome do colaborador formatado para uso nas mensagens."""
    nome = tracker.get_slot("nome_colaborador")
    return f", {nome}" if nome else ""


# ---------------------------------------------------------------------------
# Actions
# ---------------------------------------------------------------------------


class ActionBoasVindasPersonalizada(Action):
    """Saúda o colaborador pelo nome e apresenta as etapas do onboarding."""

    def name(self) -> Text:
        return "action_boas_vindas_personalizada"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        nome = _obter_nome_formatado(tracker)

        mensagem = (
            f"👋 Olá{nome}! Bem-vindo(a) à **The100s**!\n\n"
            "Sou o seu assistente virtual de onboarding e estou aqui para o/a ajudar "
            "a integrar-se na nossa equipa. 🎉\n\n"
            "**As etapas do seu onboarding são:**\n\n"
            "1. 📋 **Pré-onboarding** — Leitura de documentos e preparação\n"
            "2. 🏢 **Primeiro dia** — Apresentações e configuração do posto de trabalho\n"
            "3. 📅 **Primeira semana** — Reuniões com a equipa e formações iniciais\n\n"
            "Posso ajudá-lo/a com:\n"
            "• 🏢 Informações sobre a empresa\n"
            "• 🎁 Benefícios\n"
            "• 📄 Documentos de onboarding\n"
            "• 🎬 Vídeo de boas-vindas\n"
            "• 📝 Quiz de conhecimento\n"
            "• 📅 Agendamento de reuniões\n"
            "• 🖥️ Suporte TI\n"
            "• ❓ Perguntas frequentes\n\n"
            "Como posso ajudá-lo/a hoje?"
        )

        dispatcher.utter_message(text=mensagem)
        return []


class ActionEnviarDocumentos(Action):
    """Envia links para os documentos importantes de onboarding."""

    def name(self) -> Text:
        return "action_enviar_documentos"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        nome = _obter_nome_formatado(tracker)

        mensagem = (
            f"📄 Claro{nome}! Aqui estão os documentos essenciais para o seu onboarding:\n\n"
            "1. 📋 **Manual do Colaborador**\n"
            "   👉 [Aceder ao Manual](https://the100s.sharepoint.com/manual-colaborador)\n\n"
            "2. ⚖️ **Código de Conduta**\n"
            "   👉 [Aceder ao Código de Conduta](https://the100s.sharepoint.com/codigo-conduta)\n\n"
            "3. 📝 **Contrato de Trabalho**\n"
            "   📧 Enviado para o seu email pessoal — verifique a sua caixa de entrada\n\n"
            "4. 🔒 **Política de Privacidade e RGPD**\n"
            "   👉 [Aceder à Política](https://the100s.sharepoint.com/politica-privacidade)\n\n"
            "5. 🖥️ **Política de Uso de TI**\n"
            "   👉 [Aceder à Política TI](https://the100s.sharepoint.com/politica-ti)\n\n"
            "⚠️ Por favor, leia todos os documentos com atenção e assine os que requerem assinatura.\n"
            "Se tiver dúvidas sobre algum documento, não hesite em perguntar ou contactar os RH."
        )

        dispatcher.utter_message(text=mensagem)
        return []


class ActionIniciarQuiz(Action):
    """Inicia o quiz de conhecimento sobre a empresa."""

    def name(self) -> Text:
        return "action_iniciar_quiz"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        pontuacao_atual = tracker.get_slot("quiz_pontuacao") or 0.0
        nome = _obter_nome_formatado(tracker)

        # Determina qual pergunta apresentar com base na pontuação atual
        pergunta_idx = int(pontuacao_atual) % len(QUIZ_PERGUNTAS)

        if int(pontuacao_atual) == 0:
            introducao = (
                f"📝 Ótimo{nome}! Vamos começar o **Quiz de Conhecimento da The100s**!\n\n"
                f"Este quiz tem **{len(QUIZ_PERGUNTAS)} perguntas** sobre a empresa.\n"
                "Tente responder com a letra da opção correta (A, B, C ou D).\n\n"
            )
        else:
            introducao = ""

        pergunta = QUIZ_PERGUNTAS[pergunta_idx]
        dispatcher.utter_message(text=introducao + pergunta["pergunta"])

        return [SlotSet("quiz_pontuacao", pontuacao_atual)]


class ActionVerificarRespostaQuiz(Action):
    """Verifica a resposta do utilizador ao quiz e atualiza a pontuação."""

    def name(self) -> Text:
        return "action_verificar_resposta_quiz"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        pontuacao_atual = tracker.get_slot("quiz_pontuacao") or 0.0
        pergunta_idx = int(pontuacao_atual) % len(QUIZ_PERGUNTAS)
        pergunta = QUIZ_PERGUNTAS[pergunta_idx]

        # Extrair a resposta do utilizador a partir da última mensagem
        ultima_mensagem = (tracker.latest_message.get("text") or "").lower().strip()
        resposta_correta = pergunta["resposta_correta"].lower()

        acertou = resposta_correta in ultima_mensagem

        if acertou:
            nova_pontuacao = pontuacao_atual + 1
            feedback = f"✅ **Correto!** Muito bem!\n\n{pergunta['explicacao']}\n\n"
        else:
            nova_pontuacao = pontuacao_atual
            feedback = (
                f"❌ **Incorreto.** A resposta correta era a opção **{resposta_correta.upper()}**.\n\n"
                f"{pergunta['explicacao']}\n\n"
            )

        proxima_pergunta_idx = int(nova_pontuacao) % len(QUIZ_PERGUNTAS)
        perguntas_respondidas = pergunta_idx + 1

        if perguntas_respondidas >= len(QUIZ_PERGUNTAS):
            # Quiz concluído
            percentagem = (nova_pontuacao / len(QUIZ_PERGUNTAS)) * 100
            resumo = (
                f"🏆 **Quiz concluído!**\n\n"
                f"Pontuação final: **{int(nova_pontuacao)}/{len(QUIZ_PERGUNTAS)}** ({percentagem:.0f}%)\n\n"
            )
            if percentagem >= 80:
                resumo += "🌟 Excelente! Tem um ótimo conhecimento sobre a The100s!"
            elif percentagem >= 60:
                resumo += "👍 Bom trabalho! Continue a aprender sobre a empresa."
            else:
                resumo += (
                    "📚 Recomendamos que leia o Manual do Colaborador para aprofundar "
                    "o seu conhecimento sobre a The100s."
                )

            dispatcher.utter_message(text=feedback + resumo)
            return [SlotSet("quiz_pontuacao", nova_pontuacao)]

        # Há mais perguntas
        proxima = QUIZ_PERGUNTAS[proxima_pergunta_idx]
        dispatcher.utter_message(text=feedback + proxima["pergunta"])

        return [SlotSet("quiz_pontuacao", nova_pontuacao)]


class ActionAgendarReuniao(Action):
    """Placeholder para agendamento de reuniões via Microsoft Graph API."""

    def name(self) -> Text:
        return "action_agendar_reuniao"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        nome = _obter_nome_formatado(tracker)
        gestor = tracker.get_slot("gestor")
        gestor_info = f" com **{gestor}**" if gestor else " com o seu gestor"

        mensagem = (
            f"📅 Claro{nome}! Vou ajudá-lo/a a agendar uma reunião{gestor_info}.\n\n"
            "**Passos para agendar a reunião:**\n\n"
            "1. 📧 Verifique o convite de calendário que será enviado para o seu email\n"
            "2. 🗓️ Aceda ao **Outlook Calendar** para confirmar a disponibilidade\n"
            "3. ✅ Aceite o convite quando recebê-lo\n\n"
            "**Alternativamente, pode agendar diretamente:**\n"
            "• **Microsoft Teams:** Clique em 'Calendário' → 'Nova reunião'\n"
            "• **Outlook:** Clique em 'Nova reunião' e adicione os participantes\n\n"
            "⏰ A reunião de apresentação será normalmente agendada para os **primeiros 3 dias**.\n\n"
            "🔔 **Nota:** A integração automática com o Microsoft Calendar estará disponível em breve. "
            "Por agora, contacte diretamente o seu gestor ou os RH para agendar."
        )

        dispatcher.utter_message(text=mensagem)
        return []


class ActionRegistarFeedback(Action):
    """Regista o feedback do colaborador sobre o processo de onboarding."""

    def name(self) -> Text:
        return "action_registar_feedback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        nome = _obter_nome_formatado(tracker)
        ultima_mensagem = tracker.latest_message.get("text", "")

        # Regista o feedback nos logs (em produção, guardar em base de dados)
        logger.info(
            "Feedback recebido de colaborador%s: %s",
            nome,
            ultima_mensagem,
        )

        mensagem = (
            f"🙏 Obrigado pelo seu feedback{nome}!\n\n"
            "O seu comentário foi registado e será analisado pela equipa de RH "
            "para melhorar continuamente o processo de onboarding.\n\n"
            "✍️ Se tiver mais comentários ou sugestões, não hesite em partilhar!"
        )

        dispatcher.utter_message(text=mensagem)
        return []


class ActionVerificarEtapaOnboarding(Action):
    """Verifica em que etapa do onboarding o colaborador se encontra."""

    def name(self) -> Text:
        return "action_verificar_etapa_onboarding"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        etapa = tracker.get_slot("etapa_onboarding")
        nome = _obter_nome_formatado(tracker)

        etapas_info: Dict[Optional[str], str] = {
            "pre_onboarding": (
                f"📋 Olá{nome}! Encontra-se na fase de **Pré-onboarding**.\n\n"
                "**O que deve fazer agora:**\n"
                "• 📄 Ler os documentos enviados (manual, código de conduta, etc.)\n"
                "• ✍️ Assinar os documentos que requerem assinatura\n"
                "• 📧 Confirmar os detalhes do primeiro dia com os RH\n"
                "• 🖥️ Preparar o equipamento necessário"
            ),
            "primeiro_dia": (
                f"🏢 Olá{nome}! É o seu **Primeiro Dia** na The100s!\n\n"
                "**Agenda de hoje:**\n"
                "• 👋 Apresentações com a equipa\n"
                "• 🖥️ Configuração do posto de trabalho\n"
                "• 🔑 Receção das credenciais de acesso\n"
                "• 🍽️ Almoço com o gestor/equipa\n"
                "• 📋 Briefing inicial com o seu gestor"
            ),
            "primeira_semana": (
                f"📅 Olá{nome}! Está na sua **Primeira Semana** na The100s!\n\n"
                "**Objetivos desta semana:**\n"
                "• 🤝 Reuniões de apresentação com as equipas chave\n"
                "• 📚 Formações iniciais obrigatórias\n"
                "• 🎯 Definição de objetivos com o seu gestor\n"
                "• 🔧 Conclusão da configuração de todas as ferramentas\n"
                "• 📝 Realização do quiz de conhecimento"
            ),
        }

        mensagem = etapas_info.get(
            etapa,
            (
                f"👋 Olá{nome}! Bem-vindo(a) ao processo de onboarding da The100s!\n\n"
                "Não consegui determinar a sua etapa atual. "
                "Por favor, contacte os RH para verificar o seu estado de onboarding.\n\n"
                "📧 **RH:** rh@the100s.com"
            ),
        )

        dispatcher.utter_message(text=mensagem)
        return []
