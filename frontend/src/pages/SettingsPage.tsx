import { useQuery } from '@tanstack/react-query'
import { aiApi } from '../api/ai'
import { Settings, Info } from 'lucide-react'

export default function SettingsPage() {
  const { data: aiStatus } = useQuery({ queryKey: ['ai-status'], queryFn: aiApi.status })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <Settings size={22} className="text-cyan-400" /> Paramètres
        </h1>
        <p className="text-slate-400 text-sm mt-1">Configuration du fournisseur IA et de l'application.</p>
      </div>

      {/* Status IA */}
      <div className="bg-navy-800 border border-white/5 rounded-xl p-5">
        <h2 className="font-semibold text-white mb-4">État du fournisseur IA</h2>
        <div className="grid md:grid-cols-3 gap-4">
          <div className="bg-navy-900 rounded-xl p-3">
            <p className="text-xs text-slate-400 mb-1">Fournisseur</p>
            <p className="font-bold text-white capitalize">{aiStatus?.provider ?? '…'}</p>
          </div>
          <div className="bg-navy-900 rounded-xl p-3">
            <p className="text-xs text-slate-400 mb-1">Mode</p>
            <p className={`font-bold ${aiStatus?.mode === 'live' ? 'text-green-400' : 'text-yellow-400'}`}>
              {aiStatus?.mode === 'live' ? 'Connecté (live)' : 'Mock (sans clé API)'}
            </p>
          </div>
          <div className="bg-navy-900 rounded-xl p-3">
            <p className="text-xs text-slate-400 mb-1">Disponible</p>
            <p className={`font-bold ${aiStatus?.available ? 'text-green-400' : 'text-red-400'}`}>
              {aiStatus?.available ? 'Oui' : 'Non'}
            </p>
          </div>
        </div>
      </div>

      {/* Config via .env */}
      <div className="bg-navy-800 border border-white/5 rounded-xl p-5">
        <div className="flex items-center gap-2 mb-3">
          <Info size={16} className="text-blue-400" />
          <h2 className="font-semibold text-white">Configuration via .env</h2>
        </div>
        <p className="text-slate-400 text-sm mb-4">
          Toute la configuration est gérée via le fichier <code className="bg-navy-900 px-1.5 py-0.5 rounded text-cyan-300">.env</code> à la racine du projet.
          Aucune clé API n'est stockée dans l'interface.
        </p>

        <div className="bg-navy-900 rounded-xl p-4 font-mono text-xs text-slate-300 space-y-1">
          <p><span className="text-slate-500"># Fournisseur IA : openai | anthropic | mock</span></p>
          <p><span className="text-cyan-400">AI_PROVIDER</span>=mock</p>
          <p className="mt-2"><span className="text-slate-500"># Clés API (optionnel)</span></p>
          <p><span className="text-cyan-400">OPENAI_API_KEY</span>=sk-...</p>
          <p><span className="text-cyan-400">ANTHROPIC_API_KEY</span>=sk-ant-...</p>
          <p className="mt-2"><span className="text-slate-500"># Base de données</span></p>
          <p><span className="text-cyan-400">DATABASE_URL</span>=sqlite:///./tradegpt.db</p>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="bg-yellow-900/20 border border-yellow-600/30 rounded-xl p-5">
        <h2 className="font-semibold text-yellow-300 mb-2">⚠️ Avertissement légal</h2>
        <ul className="text-yellow-200/80 text-sm space-y-1">
          <li>• TradeGPT BTC Optimizer est un outil de <strong>simulation et d'analyse uniquement</strong>.</li>
          <li>• Les performances passées ne garantissent pas les performances futures.</li>
          <li>• Aucun ordre réel n'est jamais exécuté par cette application.</li>
          <li>• Ce logiciel ne constitue pas un conseil financier ou d'investissement.</li>
          <li>• Utilisez cet outil à vos propres risques et responsabilités.</li>
        </ul>
      </div>
    </div>
  )
}
