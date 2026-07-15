import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import InteractionForm from './InteractionForm';
import AIChatPanel from './AIChatPanel';
import { logInteraction, resetForm } from '../../store/actions';

const LogInteraction = () => {
  const dispatch = useDispatch();
  const { formData, loading, aiProcessing, interactionId } = useSelector((state) => state.interaction);

  const handleLogInteraction = async () => {
    if (!formData.hcp_name || !formData.interaction_type || !formData.date) {
      alert('Please fill in the required fields via the AI Assistant: HCP Name, Interaction Type, and Date');
      return;
    }
    try {
      const interactionData = {
        ...formData,
        hcp_id: formData.hcp_id || 1,
        date: formData.date
      };
      await dispatch(logInteraction(interactionData));
    } catch (error) {
      alert('Error logging interaction: ' + error.message);
    }
  };

  const handleReset = () => {
    if (window.confirm('Reset form? All data will be lost.')) {
      dispatch(resetForm());
    }
  };

  return (
    <div className="min-h-screen px-4 py-6 md:px-6">
      <div className="max-w-7xl mx-auto">

        {/* Page Header */}
        <div className="mb-6 flex items-start justify-between">
          <div>
            <div className="flex items-center space-x-2 mb-1">
              <span className="text-xs font-semibold uppercase tracking-widest text-sky-400">HCP Module</span>
              <span className="text-white/20">›</span>
              <span className="text-xs font-semibold uppercase tracking-widest text-white/50">Log Interaction</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-bold text-white">
              Log HCP{' '}
              <span className="gradient-text">Interaction</span>
            </h1>
            <p className="text-white/50 text-sm mt-1">
              Describe your visit naturally — our AI fills the form automatically
            </p>
          </div>

          {/* Stats row */}
          <div className="hidden md:flex items-center space-x-3">
            {[
              { label: 'HCP Name', value: formData.hcp_name || '—', icon: '👤' },
              { label: 'Sentiment', value: formData.sentiment || '—', icon: '💬' },
              { label: 'Date', value: formData.date || '—', icon: '📅' },
            ].map((stat) => (
              <div key={stat.label} className="glass px-3 py-2 text-center min-w-[90px]">
                <div className="text-lg">{stat.icon}</div>
                <div className="text-white font-semibold text-xs truncate max-w-[80px]">{stat.value}</div>
                <div className="text-white/40 text-xs">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Left: Form */}
          <div className="flex flex-col space-y-4">
            <InteractionForm aiProcessing={aiProcessing} />

            {/* Action Buttons */}
            <div className="flex space-x-3">
              <button
                onClick={handleLogInteraction}
                disabled={loading || aiProcessing}
                className="btn-gradient flex-1 py-3 px-6 text-sm font-semibold flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                    </svg>
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span>Log Interaction</span>
                  </>
                )}
              </button>
              <button
                onClick={handleReset}
                disabled={loading || aiProcessing}
                className="smooth py-3 px-5 text-sm font-medium rounded-xl text-white/60 border border-white/10 hover:border-white/20 hover:text-white/80 hover:bg-white/5 disabled:opacity-40"
              >
                Reset
              </button>
            </div>

            {/* Success Banner */}
            {interactionId && (
              <div className="glass p-4 border border-emerald-500/30 rounded-xl flex items-center space-x-3">
                <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                  <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <p className="text-emerald-400 text-sm font-semibold">Interaction Logged Successfully!</p>
                  <p className="text-white/50 text-xs mt-0.5">Reference ID: #{interactionId}</p>
                </div>
              </div>
            )}
          </div>

          {/* Right: AI Chat */}
          <div>
            <AIChatPanel />
          </div>
        </div>
      </div>
    </div>
  );
};

export default LogInteraction;
