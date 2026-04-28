import { AlertTriangle } from 'lucide-react'

export default function RiskDisclaimer() {
  return (
    <div className="bg-yellow-900/30 border border-yellow-600/40 rounded-xl p-4 flex gap-3 items-start text-sm text-yellow-200">
      <AlertTriangle className="text-yellow-400 shrink-0 mt-0.5" size={18} />
      <div>
        <span className="font-semibold text-yellow-300">Simulation uniquement — </span>
        Les résultats affichés sont basés sur des données historiques et ne garantissent pas les performances futures.
        Ce projet ne constitue <strong>pas</strong> un conseil financier. Aucun ordre réel n'est exécuté.
      </div>
    </div>
  )
}
