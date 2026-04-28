import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import GenerateStrategy from './pages/GenerateStrategy'
import TemplatesPage from './pages/TemplatesPage'
import StrategyEditorPage from './pages/StrategyEditorPage'
import DebugStrategy from './pages/DebugStrategy'
import BacktestPage from './pages/BacktestPage'
import OptimizePage from './pages/OptimizePage'
import ComparePage from './pages/ComparePage'
import ReportsPage from './pages/ReportsPage'
import SettingsPage from './pages/SettingsPage'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/"          element={<Dashboard />} />
        <Route path="/generate"  element={<GenerateStrategy />} />
        <Route path="/templates" element={<TemplatesPage />} />
        <Route path="/editor"    element={<StrategyEditorPage />} />
        <Route path="/debug"     element={<DebugStrategy />} />
        <Route path="/backtest"  element={<BacktestPage />} />
        <Route path="/optimize"  element={<OptimizePage />} />
        <Route path="/compare"   element={<ComparePage />} />
        <Route path="/reports"   element={<ReportsPage />} />
        <Route path="/settings"  element={<SettingsPage />} />
      </Route>
    </Routes>
  )
}
