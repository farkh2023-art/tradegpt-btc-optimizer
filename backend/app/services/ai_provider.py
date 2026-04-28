"""Abstraction du fournisseur IA — OpenAI / Anthropic / Mock local."""
from abc import ABC, abstractmethod
from typing import Optional
from app.core.config import settings
from app.core.logging import logger
import app.templates.sma as sma_tpl
import app.templates.rsi as rsi_tpl
import app.templates.adx as adx_tpl
import app.templates.supertrend as st_tpl
import app.templates.combined as combo_tpl


class AIProvider(ABC):
    @abstractmethod
    async def generate_strategy(self, prompt: str, template: Optional[str], risk_profile: str) -> dict:
        pass

    @abstractmethod
    async def debug_script(self, script: str) -> dict:
        pass

    @abstractmethod
    async def get_recommendations(self, metrics: dict, params: dict, template: str) -> dict:
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass


# ---------------------------------------------------------------------------
# Mock Provider — toujours fonctionnel, aucune clé API requise
# ---------------------------------------------------------------------------

_TEMPLATE_MAP = {
    "sma": sma_tpl,
    "supertrend": st_tpl,
    "rsi": rsi_tpl,
    "adx": adx_tpl,
    "combined": combo_tpl,
}

_KEYWORD_MAP = {
    "supertrend": "supertrend",
    "rsi": "rsi",
    "adx": "adx",
    "combiné": "combined",
    "combined": "combined",
    "multi": "combined",
    "sma": "sma",
    "moyenne mobile": "sma",
    "moving average": "sma",
}


def _detect_template(prompt: str) -> str:
    p = prompt.lower()
    for kw, tpl in _KEYWORD_MAP.items():
        if kw in p:
            return tpl
    return "sma"


class MockProvider(AIProvider):
    @property
    def is_available(self) -> bool:
        return True

    @property
    def provider_name(self) -> str:
        return "mock"

    async def generate_strategy(self, prompt: str, template: Optional[str], risk_profile: str) -> dict:
        tpl_key = template or _detect_template(prompt)
        tpl = _TEMPLATE_MAP.get(tpl_key, sma_tpl)

        risk_params: dict = {}
        if risk_profile == "conservative":
            risk_params = {"stop_loss_pct": 1.5, "take_profit_pct": 3.0}
        elif risk_profile == "aggressive":
            risk_params = {"stop_loss_pct": 3.0, "take_profit_pct": 8.0}

        pine = tpl.generate(**risk_params)
        return {
            "name": f"Stratégie {tpl_key.upper()} — {risk_profile.capitalize()}",
            "description": tpl.DESCRIPTION,
            "pine_script": pine,
            "parameters": tpl.PARAMS_SCHEMA,
            "indicators": tpl.INDICATORS,
            "explanation": (
                f"[Mode Mock] Stratégie générée à partir du template {tpl_key.upper()}.\n"
                f"Profil de risque : {risk_profile}.\n"
                f"Indicateurs utilisés : {', '.join(tpl.INDICATORS)}.\n"
                "Pour une génération IA avancée, configurez OPENAI_API_KEY ou ANTHROPIC_API_KEY dans le fichier .env."
            ),
        }

    async def debug_script(self, script: str) -> dict:
        issues = []
        corrections = script

        # Vérifications basiques Pine Script v5
        if "//@version=5" not in script:
            issues.append("⚠️ En-tête manquant : ajoutez `//@version=5` en première ligne.")
            corrections = "//@version=5\n" + corrections

        if "strategy(" not in script and "indicator(" not in script:
            issues.append("⚠️ Ni `strategy()` ni `indicator()` trouvé — requis en Pine Script v5.")

        if "var " in script and "series" in script:
            issues.append("ℹ️ Vérifiez l'usage de `var` avec des séries — peut causer des comportements inattendus.")

        if "study(" in script:
            issues.append("❌ `study()` est obsolète en v5, remplacez par `indicator()`.")
            corrections = corrections.replace("study(", "indicator(")

        if not issues:
            issues.append("✅ Aucun problème syntaxique évident détecté.")

        return {
            "issues": issues,
            "corrected_script": corrections,
            "explanation": (
                "[Mode Mock] Analyse statique basique effectuée. "
                "Pour une analyse IA approfondie, configurez une clé API."
            ),
            "severity": "warning" if len(issues) > 1 else "ok",
        }

    async def get_recommendations(self, metrics: dict, params: dict, template: str) -> dict:
        recs = []
        win_rate = metrics.get("win_rate", 0)
        return_pct = metrics.get("return_pct", 0)
        max_dd = metrics.get("max_drawdown", 0)

        if win_rate < 40:
            recs.append("Win rate faible (<40%) : essayez d'augmenter le seuil ADX ou de filtrer les tendances latérales.")
        if max_dd > 20:
            recs.append("Drawdown élevé (>20%) : réduisez la taille de position ou resserrez le stop loss.")
        if return_pct < 0:
            recs.append("Rendement négatif : revoyez les paramètres d'entrée/sortie ou changez de template.")
        if return_pct > 50:
            recs.append("Excellent rendement : attention à la sur-optimisation (overfitting).")
        if not recs:
            recs.append("Performance acceptable. Testez sur d'autres périodes pour valider la robustesse.")

        return {
            "recommendations": recs,
            "suggested_params": {},
            "analysis": "[Mode Mock] Recommandations basées sur les métriques de simulation.",
        }


# ---------------------------------------------------------------------------
# OpenAI Provider
# ---------------------------------------------------------------------------

class OpenAIProvider(AIProvider):
    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client

    @property
    def is_available(self) -> bool:
        return bool(settings.OPENAI_API_KEY)

    @property
    def provider_name(self) -> str:
        return "openai"

    async def generate_strategy(self, prompt: str, template: Optional[str], risk_profile: str) -> dict:
        client = self._get_client()
        system = (
            "Tu es un expert en trading algorithmique et Pine Script v5 pour TradingView. "
            "Tu génères des stratégies Bitcoin claires, commentées et paramétrables. "
            "Réponds toujours en JSON valide avec les champs: name, description, pine_script, parameters (dict), indicators (list), explanation."
        )
        user_msg = (
            f"Génère une stratégie de trading Bitcoin en Pine Script v5.\n"
            f"Description: {prompt}\n"
            f"Template préféré: {template or 'libre'}\n"
            f"Profil de risque: {risk_profile}\n"
            "La stratégie doit inclure stop loss, take profit, alertcondition et commentaires pédagogiques."
        )
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user_msg}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        import json
        data = json.loads(response.choices[0].message.content)
        return data

    async def debug_script(self, script: str) -> dict:
        client = self._get_client()
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un expert Pine Script v5. Analyse le script et retourne un JSON avec: issues (list), corrected_script (string), explanation (string), severity (ok|warning|error)."},
                {"role": "user", "content": f"Analyse ce script Pine Script:\n\n```pine\n{script}\n```"},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        import json
        return json.loads(response.choices[0].message.content)

    async def get_recommendations(self, metrics: dict, params: dict, template: str) -> dict:
        client = self._get_client()
        import json
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un expert en optimisation de stratégies de trading. Retourne un JSON avec: recommendations (list), suggested_params (dict), analysis (string)."},
                {"role": "user", "content": f"Métriques: {json.dumps(metrics)}\nParamètres actuels: {json.dumps(params)}\nTemplate: {template}"},
            ],
            response_format={"type": "json_object"},
            temperature=0.5,
        )
        return json.loads(response.choices[0].message.content)


# ---------------------------------------------------------------------------
# Anthropic Provider
# ---------------------------------------------------------------------------

class AnthropicProvider(AIProvider):
    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        return self._client

    @property
    def is_available(self) -> bool:
        return bool(settings.ANTHROPIC_API_KEY)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    async def generate_strategy(self, prompt: str, template: Optional[str], risk_profile: str) -> dict:
        client = self._get_client()
        import json
        msg = await client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=4096,
            system=(
                "Tu es un expert en trading algorithmique et Pine Script v5 pour TradingView. "
                "Réponds toujours en JSON valide avec les champs: name, description, pine_script, parameters (dict), indicators (list), explanation."
            ),
            messages=[{"role": "user", "content": (
                f"Génère une stratégie Bitcoin Pine Script v5.\nDescription: {prompt}\n"
                f"Template: {template or 'libre'}\nRisque: {risk_profile}"
            )}],
        )
        return json.loads(msg.content[0].text)

    async def debug_script(self, script: str) -> dict:
        client = self._get_client()
        import json
        msg = await client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=4096,
            system="Tu es un expert Pine Script v5. Retourne un JSON avec: issues (list), corrected_script (string), explanation (string), severity (ok|warning|error).",
            messages=[{"role": "user", "content": f"Analyse ce script:\n\n```pine\n{script}\n```"}],
        )
        return json.loads(msg.content[0].text)

    async def get_recommendations(self, metrics: dict, params: dict, template: str) -> dict:
        client = self._get_client()
        import json
        msg = await client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=2048,
            system="Expert en optimisation trading. Retourne un JSON avec: recommendations (list), suggested_params (dict), analysis (string).",
            messages=[{"role": "user", "content": f"Métriques: {json.dumps(metrics)}\nParams: {json.dumps(params)}\nTemplate: {template}"}],
        )
        return json.loads(msg.content[0].text)


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def get_ai_provider() -> AIProvider:
    prov = settings.AI_PROVIDER.lower()

    if prov == "openai" and settings.OPENAI_API_KEY:
        logger.info("Fournisseur IA: OpenAI")
        return OpenAIProvider()

    if prov == "anthropic" and settings.ANTHROPIC_API_KEY:
        logger.info("Fournisseur IA: Anthropic")
        return AnthropicProvider()

    logger.info("Fournisseur IA: Mock (aucune clé API détectée)")
    return MockProvider()
