import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import RouteForm from './components/RouteForm';
import RouteCards from './components/RouteCards';
import MapView from './components/MapView';
import TimelineSlider from './components/TimelineSlider';
import RiskRulesModal from './components/RiskRulesModal';
import { AlertCircle } from 'lucide-react';

export default function App() {
  const [routesData, setRoutesData] = useState(null);
  const [activeRouteId, setActiveRouteId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isRulesModalOpen, setIsRulesModalOpen] = useState(false);

  // Timeline & Heatmap State
  const [currentHour, setCurrentHour] = useState(0);
  const [activeMetric, setActiveMetric] = useState('risk');
  const [showHeatmap, setShowHeatmap] = useState(true);

  const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

  const handleCalculateRoute = async (formData) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE}/api/routes/plan/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.error || `HTTP error ${response.status}`);
      }

      const data = await response.json();
      setRoutesData(data);
      if (data.routes && data.routes.length > 0) {
        const rec = data.routes.find((r) => r.is_recommended) || data.routes[0];
        setActiveRouteId(rec.route_id);
      }
      setCurrentHour(0);
    } catch (err) {
      console.error("Routing error:", err);
      setError(err.message || "Failed to calculate routes. Please verify inputs.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const defaultDate = new Date();
    defaultDate.setMinutes(defaultDate.getMinutes() - defaultDate.getTimezoneOffset());

    handleCalculateRoute({
      origin: "Chicago, IL",
      destination: "Denver, CO",
      departure_time: defaultDate.toISOString(),
      load_weight_lbs: 35000,
      sample_interval_miles: 25,
    });
  }, []);

  return (
    <div className="min-h-screen bg-black text-white flex flex-col font-sans">
      <Navbar onOpenRules={() => setIsRulesModalOpen(true)} />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 space-y-4">
        {error && (
          <div className="bg-zinc-950 border border-zinc-700 rounded p-4 flex items-center gap-3 text-white text-xs font-mono">
            <AlertCircle className="w-4 h-4 text-white shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <RouteForm onSubmit={handleCalculateRoute} isLoading={isLoading} />

        <div className="space-y-3">
          <div className="h-[560px] w-full">
            <MapView
              routes={routesData?.routes}
              activeRouteId={activeRouteId}
              onSelectRoute={setActiveRouteId}
              origin={routesData?.origin}
              destination={routesData?.destination}
              timeline={routesData?.heatmap_timeline}
              currentHour={currentHour}
              activeMetric={activeMetric}
              showHeatmap={showHeatmap}
            />
          </div>

          {routesData?.heatmap_timeline && (
            <TimelineSlider
              timeline={routesData.heatmap_timeline}
              currentHour={currentHour}
              onHourChange={setCurrentHour}
              activeMetric={activeMetric}
              onMetricChange={setActiveMetric}
              showHeatmap={showHeatmap}
              onToggleHeatmap={() => setShowHeatmap(!showHeatmap)}
            />
          )}

          {routesData?.routes && (
            <RouteCards
              routes={routesData.routes}
              activeRouteId={activeRouteId}
              onSelectRoute={setActiveRouteId}
            />
          )}
        </div>
      </main>

      <RiskRulesModal
        isOpen={isRulesModalOpen}
        onClose={() => setIsRulesModalOpen(false)}
      />
    </div>
  );
}
