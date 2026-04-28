"""Génère des rapports Markdown pour une stratégie."""
import json
from datetime import datetime


def generate_report(strategy, version, backtest=None) -> str:
    params = {}
    if version:
        try:
            params = json.loads(version.parameters)
        except Exception:
            params = {}

    lines = [
        f"# Rapport — {strategy.name}",
        f"> Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
        "",
        "---",
        "",
        "## ⚠️ Avertissement",
        "",
        "> **Ce rapport est basé sur des simulations historiques.**",
        "> Les performances passées ne garantissent pas les performances futures.",
        "> Ce document ne constitue **pas** un conseil financier.",
        "> **Mode papier uniquement — aucun ordre réel n'est exécuté.**",
        "",
        "---",
        "",
        "## 1. Description de la stratégie",
        "",
        f"**Nom :** {strategy.name}",
        f"**Profil de risque :** {strategy.risk_profile}",
        f"**Template :** {strategy.template or 'Généré par IA'}",
        f"**Créée le :** {strategy.created_at.strftime('%d/%m/%Y')}",
        "",
        strategy.description or "_Aucune description._",
        "",
        "---",
        "",
        "## 2. Pine Script v5",
        "",
        "```pine",
        version.pine_script if version else "_Script non disponible_",
        "```",
        "",
        "---",
        "",
        "## 3. Paramètres",
        "",
    ]

    if params:
        lines.append("| Paramètre | Valeur |")
        lines.append("|-----------|--------|")
        for k, v in params.items():
            lines.append(f"| `{k}` | {v} |")
    else:
        lines.append("_Paramètres non définis._")

    lines += ["", "---", "", "## 4. Résultats de simulation", ""]

    if backtest:
        lines += [
            f"| Métrique | Valeur |",
            f"|----------|--------|",
            f"| Capital initial | {backtest.initial_capital:,.2f} $ |",
            f"| Capital final   | {backtest.final_capital:,.2f} $ |",
            f"| Rendement       | **{backtest.return_pct:+.2f} %** |",
            f"| Nombre de trades | {backtest.num_trades} |",
            f"| Win rate        | {backtest.win_rate:.1f} % |",
            f"| Drawdown max    | {backtest.max_drawdown:.1f} % |",
            f"| Profit Factor   | {backtest.profit_factor:.3f} |",
            f"| Ratio de Sharpe | {backtest.sharpe_ratio:.3f} |",
            f"| Source          | {backtest.source} |",
        ]
    else:
        lines.append("_Aucun backtest disponible pour cette stratégie._")

    lines += [
        "",
        "---",
        "",
        "## 5. Recommandations",
        "",
        "- Testez la stratégie sur plusieurs périodes (bull market, bear market, range).",
        "- Évitez la sur-optimisation : des paramètres trop ajustés échouent en production.",
        "- Utilisez un faible pourcentage du capital par trade (5–15 %).",
        "- Combinez avec des filtres de marché (volume, volatilité) pour réduire les faux signaux.",
        "",
        "---",
        "",
        "## 6. Limites et risques",
        "",
        "- **Données historiques** : les backtests supposent une liquidité parfaite.",
        "- **Slippage** : les frais réels et le glissement de prix ne sont pas entièrement modélisés.",
        "- **Biais de survie** : les données peuvent surreprésenter les périodes favorables.",
        "- **Volatilité du Bitcoin** : les conditions de marché peuvent changer radicalement.",
        "",
        "---",
        "",
        "*Rapport généré par TradeGPT BTC Optimizer — simulation uniquement.*",
    ]

    return "\n".join(lines)
