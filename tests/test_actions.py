"""
Testes básicos para as custom actions do Bot de Onboarding da The100s.
"""

from unittest.mock import MagicMock, patch

import pytest

from actions.actions import (
    QUIZ_PERGUNTAS,
    ActionAgendarReuniao,
    ActionBoasVindasPersonalizada,
    ActionEnviarDocumentos,
    ActionIniciarQuiz,
    ActionRegistarFeedback,
    ActionVerificarEtapaOnboarding,
    ActionVerificarRespostaQuiz,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_tracker(slots=None, latest_message=None):
    """Cria um mock do Tracker do Rasa para testes."""
    tracker = MagicMock()
    slots = slots or {}
    tracker.get_slot.side_effect = lambda key: slots.get(key)
    tracker.latest_message = latest_message or {"text": ""}
    return tracker


def _make_dispatcher():
    """Cria um mock do CollectingDispatcher do Rasa para testes."""
    dispatcher = MagicMock()
    dispatcher.utter_message = MagicMock()
    return dispatcher


# ---------------------------------------------------------------------------
# Testes de nomes das actions
# ---------------------------------------------------------------------------


def test_action_boas_vindas_personalizada_name():
    assert ActionBoasVindasPersonalizada().name() == "action_boas_vindas_personalizada"


def test_action_enviar_documentos_name():
    assert ActionEnviarDocumentos().name() == "action_enviar_documentos"


def test_action_iniciar_quiz_name():
    assert ActionIniciarQuiz().name() == "action_iniciar_quiz"


def test_action_verificar_resposta_quiz_name():
    assert ActionVerificarRespostaQuiz().name() == "action_verificar_resposta_quiz"


def test_action_agendar_reuniao_name():
    assert ActionAgendarReuniao().name() == "action_agendar_reuniao"


def test_action_registar_feedback_name():
    assert ActionRegistarFeedback().name() == "action_registar_feedback"


def test_action_verificar_etapa_onboarding_name():
    assert ActionVerificarEtapaOnboarding().name() == "action_verificar_etapa_onboarding"


# ---------------------------------------------------------------------------
# Testes de ActionBoasVindasPersonalizada
# ---------------------------------------------------------------------------


def test_boas_vindas_sem_nome():
    action = ActionBoasVindasPersonalizada()
    dispatcher = _make_dispatcher()
    tracker = _make_tracker(slots={"nome_colaborador": None})
    domain = {}

    events = action.run(dispatcher, tracker, domain)

    dispatcher.utter_message.assert_called_once()
    call_kwargs = dispatcher.utter_message.call_args
    message = call_kwargs[1].get("text") or call_kwargs[0][0]
    assert "The100s" in message
    assert events == []


def test_boas_vindas_com_nome():
    action = ActionBoasVindasPersonalizada()
    dispatcher = _make_dispatcher()
    tracker = _make_tracker(slots={"nome_colaborador": "Ana"})
    domain = {}

    action.run(dispatcher, tracker, domain)

    call_kwargs = dispatcher.utter_message.call_args
    message = call_kwargs[1].get("text") or call_kwargs[0][0]
    assert "Ana" in message


# ---------------------------------------------------------------------------
# Testes de ActionEnviarDocumentos
# ---------------------------------------------------------------------------


def test_enviar_documentos_contem_links():
    action = ActionEnviarDocumentos()
    dispatcher = _make_dispatcher()
    tracker = _make_tracker()
    domain = {}

    action.run(dispatcher, tracker, domain)

    call_kwargs = dispatcher.utter_message.call_args
    message = call_kwargs[1].get("text") or call_kwargs[0][0]
    assert "Manual do Colaborador" in message
    assert "Código de Conduta" in message
    assert "the100s.sharepoint.com" in message


# ---------------------------------------------------------------------------
# Testes de ActionIniciarQuiz
# ---------------------------------------------------------------------------


def test_iniciar_quiz_primeira_pergunta():
    action = ActionIniciarQuiz()
    dispatcher = _make_dispatcher()
    tracker = _make_tracker(slots={"quiz_pontuacao": 0.0})
    domain = {}

    events = action.run(dispatcher, tracker, domain)

    dispatcher.utter_message.assert_called_once()
    call_kwargs = dispatcher.utter_message.call_args
    message = call_kwargs[1].get("text") or call_kwargs[0][0]
    assert "Pergunta 1" in message or "pergunta" in message.lower() or "?" in message


def test_quiz_tem_tres_perguntas():
    assert len(QUIZ_PERGUNTAS) == 3


def test_quiz_perguntas_tem_campos_obrigatorios():
    for pergunta in QUIZ_PERGUNTAS:
        assert "id" in pergunta
        assert "pergunta" in pergunta
        assert "resposta_correta" in pergunta
        assert "explicacao" in pergunta


# ---------------------------------------------------------------------------
# Testes de ActionVerificarRespostaQuiz
# ---------------------------------------------------------------------------


def test_verificar_resposta_correta():
    action = ActionVerificarRespostaQuiz()
    dispatcher = _make_dispatcher()
    # A resposta correta da primeira pergunta é "b"
    resposta_correta = QUIZ_PERGUNTAS[0]["resposta_correta"]
    tracker = _make_tracker(
        slots={"quiz_pontuacao": 0.0},
        latest_message={"text": f"opção {resposta_correta}"},
    )
    domain = {}

    events = action.run(dispatcher, tracker, domain)

    call_kwargs = dispatcher.utter_message.call_args
    message = call_kwargs[1].get("text") or call_kwargs[0][0]
    assert "Correto" in message or "correto" in message.lower()

    # Verifica que a pontuação foi incrementada
    slot_events = [e for e in events if isinstance(e, dict) and e.get("event") == "slot"]
    assert any(
        e.get("name") == "quiz_pontuacao" and e.get("value") == 1.0
        for e in slot_events
    )


def test_verificar_resposta_incorreta():
    action = ActionVerificarRespostaQuiz()
    dispatcher = _make_dispatcher()
    tracker = _make_tracker(
        slots={"quiz_pontuacao": 0.0},
        latest_message={"text": "opção z"},  # resposta inexistente
    )
    domain = {}

    events = action.run(dispatcher, tracker, domain)

    call_kwargs = dispatcher.utter_message.call_args
    message = call_kwargs[1].get("text") or call_kwargs[0][0]
    assert "Incorreto" in message or "incorreto" in message.lower()

    # Verifica que a pontuação NÃO foi incrementada
    slot_events = [e for e in events if isinstance(e, dict) and e.get("event") == "slot"]
    assert any(
        e.get("name") == "quiz_pontuacao" and e.get("value") == 0.0
        for e in slot_events
    )


# ---------------------------------------------------------------------------
# Testes de ActionAgendarReuniao
# ---------------------------------------------------------------------------


def test_agendar_reuniao_sem_gestor():
    action = ActionAgendarReuniao()
    dispatcher = _make_dispatcher()
    tracker = _make_tracker(slots={"gestor": None})
    domain = {}

    action.run(dispatcher, tracker, domain)

    call_kwargs = dispatcher.utter_message.call_args
    message = call_kwargs[1].get("text") or call_kwargs[0][0]
    assert "reunião" in message.lower() or "Outlook" in message or "Teams" in message


def test_agendar_reuniao_com_gestor():
    action = ActionAgendarReuniao()
    dispatcher = _make_dispatcher()
    tracker = _make_tracker(slots={"gestor": "João Silva"})
    domain = {}

    action.run(dispatcher, tracker, domain)

    call_kwargs = dispatcher.utter_message.call_args
    message = call_kwargs[1].get("text") or call_kwargs[0][0]
    assert "João Silva" in message


# ---------------------------------------------------------------------------
# Testes de ActionRegistarFeedback
# ---------------------------------------------------------------------------


def test_registar_feedback():
    action = ActionRegistarFeedback()
    dispatcher = _make_dispatcher()
    tracker = _make_tracker(
        slots={"nome_colaborador": "Maria"},
        latest_message={"text": "O processo foi muito bom!"},
    )
    domain = {}

    action.run(dispatcher, tracker, domain)

    call_kwargs = dispatcher.utter_message.call_args
    message = call_kwargs[1].get("text") or call_kwargs[0][0]
    assert "feedback" in message.lower() or "obrigado" in message.lower()


# ---------------------------------------------------------------------------
# Testes de ActionVerificarEtapaOnboarding
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "etapa,palavra_esperada",
    [
        ("pre_onboarding", "Pré-onboarding"),
        ("primeiro_dia", "Primeiro Dia"),
        ("primeira_semana", "Primeira Semana"),
        (None, "onboarding"),
    ],
)
def test_verificar_etapa_onboarding(etapa, palavra_esperada):
    action = ActionVerificarEtapaOnboarding()
    dispatcher = _make_dispatcher()
    tracker = _make_tracker(slots={"etapa_onboarding": etapa, "nome_colaborador": None})
    domain = {}

    action.run(dispatcher, tracker, domain)

    call_kwargs = dispatcher.utter_message.call_args
    message = call_kwargs[1].get("text") or call_kwargs[0][0]
    assert palavra_esperada.lower() in message.lower()
