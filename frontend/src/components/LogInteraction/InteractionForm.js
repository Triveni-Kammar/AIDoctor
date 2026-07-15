import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { updateFormField } from '../../store/actions';
import { INTERACTION_TYPES, SENTIMENT_OPTIONS } from '../../utils/constants';

const FieldRow = ({ label, required, children, icon }) => (
  <div className="mb-4">
    <label className="flex items-center space-x-1.5 text-xs font-semibold text-white/60 uppercase tracking-wider mb-1.5">
      {icon && <span>{icon}</span>}
      <span>{label}</span>
      {required && <span className="text-purple-400">*</span>}
    </label>
    {children}
  </div>
);

const ReadField = ({ value, placeholder }) => (
  <div className="field-dark px-3 py-2.5 text-sm min-h-[38px] flex items-center">
    {value ? (
      <span className="text-white/90">{value}</span>
    ) : (
      <span className="text-white/25 text-xs italic">{placeholder || 'Auto-filled by AI...'}</span>
    )}
  </div>
);

const InteractionForm = ({ aiProcessing }) => {
  const { formData } = useSelector((state) => state.interaction);

  const getSentimentStyle = (s) => {
    if (s === 'Positive') return 'text-emerald-400 border-emerald-500/40 bg-emerald-500/10';
    if (s === 'Negative') return 'text-red-400 border-red-500/40 bg-red-500/10';
    return 'text-amber-400 border-amber-500/40 bg-amber-500/10';
  };

  const getSentimentIcon = (s) => {
    if (s === 'Positive') return '😊';
    if (s === 'Negative') return '😟';
    return '😐';
  };

  return (
    <div className="glass overflow-hidden">
      {/* Card Header */}
      <div className="px-5 py-4 border-b border-white/10"
        style={{ background: 'linear-gradient(135deg, rgba(2,132,199,0.15) 0%, rgba(14,165,233,0.08) 100%)' }}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, #0284c7, #0ea5e9)' }}>
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h2 className="text-white font-bold text-base">Interaction Details</h2>
              <p className="text-white/40 text-xs">AI-controlled form</p>
            </div>
          </div>
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold badge-glow"
            style={{ background: 'rgba(14,165,233,0.15)', border: '1px solid rgba(14,165,233,0.3)', color: '#38bdf8' }}>
            <span className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-pulse inline-block"></span>
            <span>🔒 AI-First Mode</span>
          </span>
        </div>
      </div>

      {/* Info Banner */}
      <div className="mx-5 mt-4 px-4 py-3 rounded-xl text-xs leading-relaxed flex items-start space-x-2"
        style={{ background: 'rgba(14,165,233,0.08)', border: '1px solid rgba(14,165,233,0.15)' }}>
        <span className="text-lg flex-shrink-0">✨</span>
        <span className="text-sky-300">
          <strong className="text-sky-200">Form fills automatically.</strong> Use the{' '}
          <strong className="text-cyan-300">AI Voice Assistant</strong> on the right — speak or type your
          interaction details and corrections.
        </span>
      </div>

      {/* Form Fields */}
      <div className="p-5 space-y-0">
        <FieldRow label="HCP Name" required icon="👤">
          <ReadField value={formData.hcp_name} placeholder="e.g. Dr. Smith" />
        </FieldRow>

        <div className="grid grid-cols-2 gap-3 mb-4">
          <FieldRow label="Type" required icon="📋">
            {formData.interaction_type ? (
              <div className="field-dark px-3 py-2.5 text-sm">
                <span className="text-purple-300 font-medium">{formData.interaction_type}</span>
              </div>
            ) : (
              <ReadField placeholder="Meeting / Call / Email" />
            )}
          </FieldRow>
          <FieldRow label="Sentiment" icon="💬">
            {formData.sentiment ? (
              <div className={`px-3 py-2.5 text-sm rounded-xl border font-semibold flex items-center space-x-2 ${getSentimentStyle(formData.sentiment)}`}>
                <span>{getSentimentIcon(formData.sentiment)}</span>
                <span>{formData.sentiment}</span>
              </div>
            ) : (
              <ReadField placeholder="Auto-detected..." />
            )}
          </FieldRow>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-4">
          <FieldRow label="Date" required icon="📅">
            <ReadField value={formData.date} placeholder="YYYY-MM-DD" />
          </FieldRow>
          <FieldRow label="Time" icon="🕐">
            <ReadField value={formData.time} placeholder="HH:MM" />
          </FieldRow>
        </div>

        <FieldRow label="Attendees" icon="👥">
          <ReadField value={formData.attendees} />
        </FieldRow>

        <FieldRow label="Topics Discussed" icon="💡">
          <div className="field-dark px-3 py-2.5 text-sm min-h-[70px]">
            {formData.topics_discussed ? (
              <span className="text-white/90">{formData.topics_discussed}</span>
            ) : (
              <span className="text-white/25 text-xs italic">Topics discussed will appear here...</span>
            )}
          </div>
        </FieldRow>

        {/* Materials */}
        <FieldRow label="Materials Shared" icon="📄">
          <div className="rounded-xl border border-white/10 p-3 min-h-[56px]"
            style={{ background: 'rgba(255,255,255,0.04)' }}>
            {formData.materials_shared.length === 0 ? (
              <p className="text-white/25 text-xs italic">No materials yet — tell the AI assistant</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {formData.materials_shared.map((m, i) => (
                  <span key={m.id || i} className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-blue-300"
                    style={{ background: 'rgba(96,165,250,0.12)', border: '1px solid rgba(96,165,250,0.25)' }}>
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    <span>{m.name}</span>
                  </span>
                ))}
              </div>
            )}
          </div>
        </FieldRow>

        {/* Samples */}
        <FieldRow label="Samples Distributed" icon="💊">
          <div className="rounded-xl border border-white/10 p-3 min-h-[56px]"
            style={{ background: 'rgba(255,255,255,0.04)' }}>
            {formData.samples_distributed.length === 0 ? (
              <p className="text-white/25 text-xs italic">No samples yet — tell the AI assistant</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {formData.samples_distributed.map((s, i) => (
                  <span key={s.id || i} className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-emerald-300"
                    style={{ background: 'rgba(52,211,153,0.12)', border: '1px solid rgba(52,211,153,0.25)' }}>
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                    </svg>
                    <span>{s.name}{s.quantity ? ` ×${s.quantity}` : ''}</span>
                  </span>
                ))}
              </div>
            )}
          </div>
        </FieldRow>

        <FieldRow label="Outcomes" icon="🎯">
          <div className="field-dark px-3 py-2.5 text-sm min-h-[60px]">
            {formData.outcomes ? (
              <span className="text-white/90">{formData.outcomes}</span>
            ) : (
              <span className="text-white/25 text-xs italic">Outcomes noted by AI...</span>
            )}
          </div>
        </FieldRow>

        <FieldRow label="Follow-up Actions" icon="📌">
          <div className="field-dark px-3 py-2.5 text-sm min-h-[60px]">
            {formData.follow_up_actions ? (
              <span className="text-white/90">{formData.follow_up_actions}</span>
            ) : (
              <span className="text-white/25 text-xs italic">Follow-up actions from AI...</span>
            )}
          </div>
        </FieldRow>

        {/* AI Suggested Follow-ups */}
        {formData.ai_suggested_followups && formData.ai_suggested_followups.length > 0 && (
          <div className="mt-2 p-4 rounded-xl"
            style={{ background: 'linear-gradient(135deg, rgba(2,132,199,0.1), rgba(14,165,233,0.08))', border: '1px solid rgba(14,165,233,0.25)' }}>
            <h3 className="text-xs font-bold text-sky-300 mb-3 flex items-center space-x-1.5">
              <span>💡</span>
              <span>AI Suggested Follow-ups</span>
            </h3>
            <ul className="space-y-2">
              {formData.ai_suggested_followups.map((followup, index) => (
                <li key={index} className="flex items-start space-x-2 text-xs text-white/70">
                  <span className="text-sky-400 mt-0.5 flex-shrink-0">→</span>
                  <span>{followup}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default InteractionForm;
