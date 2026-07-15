import React, { useState, useRef, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { clearChatMessages, chatWithAgent } from '../../store/actions';

const AIChatPanel = () => {
  const dispatch = useDispatch();
  const { chatMessages, aiProcessing } = useSelector((state) => state.interaction);
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [speakingMessageId, setSpeakingMessageId] = useState(null);
  const [autoRead, setAutoRead] = useState(false);
  const messagesEndRef = useRef(null);
  const recognitionRef = useRef(null);
  const textareaRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  // Init Speech Recognition
  useEffect(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SR) {
      const rec = new SR();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = 'en-US';
      rec.onstart = () => setIsListening(true);
      rec.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) setInput((p) => p + (p ? ' ' : '') + transcript);
      };
      rec.onerror = () => setIsListening(false);
      rec.onend = () => setIsListening(false);
      recognitionRef.current = rec;
    }
  }, []);

  // Auto-read new AI messages
  useEffect(() => {
    if (autoRead && chatMessages.length > 0) {
      const last = chatMessages[chatMessages.length - 1];
      if (last.role === 'assistant') speak(last.content, chatMessages.length - 1);
    }
  }, [chatMessages]); // eslint-disable-line

  const toggleListening = () => {
    if (!recognitionRef.current) {
      alert('Voice dictation requires Chrome or Edge browser.');
      return;
    }
    if (isListening) {
      recognitionRef.current.stop();
    } else {
      try { recognitionRef.current.start(); } catch (e) { console.error(e); }
    }
  };

  const speak = (text, messageIndex) => {
    if (!('speechSynthesis' in window)) return;
    if (speakingMessageId === messageIndex) {
      window.speechSynthesis.cancel();
      setSpeakingMessageId(null);
      return;
    }
    window.speechSynthesis.cancel();
    const cleanText = text.replace(/[*#`_\-]/g, ' ');
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.onend = () => setSpeakingMessageId(null);
    utterance.onerror = () => setSpeakingMessageId(null);
    setSpeakingMessageId(messageIndex);
    window.speechSynthesis.speak(utterance);
  };

  const handleSend = async () => {
    if (!input.trim()) return;
    if ('speechSynthesis' in window) { window.speechSynthesis.cancel(); setSpeakingMessageId(null); }
    const msg = input.trim();
    setInput('');
    try { await dispatch(chatWithAgent(msg, chatMessages)); }
    catch (e) { console.error(e); }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const handleClearChat = () => {
    if ('speechSynthesis' in window) window.speechSynthesis.cancel();
    setSpeakingMessageId(null);
    dispatch(clearChatMessages());
  };

  const examplePrompts = [
    "Met Dr. Smith, discussed Product X efficacy, positive sentiment",
    "Actually, the date was yesterday",
    "Shared a Product X Brochure and 5 sample packs",
  ];

  return (
    <div className="glass flex flex-col overflow-hidden h-full" style={{ minHeight: '600px' }}>
      {/* Panel Header */}
      <div className="px-5 py-4 border-b border-white/10 flex items-center justify-between"
        style={{ background: 'linear-gradient(135deg, rgba(2,132,199,0.15) 0%, rgba(14,165,233,0.08) 100%)' }}>
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center"
              style={{ background: 'linear-gradient(135deg, #0284c7, #0ea5e9)' }}>
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-emerald-400 border-2 border-gray-900"></span>
          </div>
          <div>
            <h2 className="text-white font-bold text-base">AI Voice Assistant</h2>
            <div className="flex items-center space-x-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></div>
              <p className="text-white/40 text-xs">LangGraph · llama-3.1-8b</p>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <label className="flex items-center space-x-1.5 cursor-pointer group">
            <div className="relative">
              <input type="checkbox" checked={autoRead} onChange={(e) => setAutoRead(e.target.checked)} className="sr-only"/>
              <div className={`w-9 h-5 rounded-full transition-colors ${autoRead ? 'bg-sky-600' : 'bg-white/10'}`}></div>
              <div className={`absolute top-0.5 left-0.5 w-4 h-4 bg-white rounded-full shadow-sm transition-transform ${autoRead ? 'translate-x-4' : ''}`}></div>
            </div>
            <span className="text-xs text-white/50 group-hover:text-white/80 smooth">Auto-Read</span>
          </label>
          <button onClick={handleClearChat}
            className="smooth text-xs text-white/40 hover:text-red-400 px-2 py-1 rounded-lg hover:bg-red-400/10 border border-transparent hover:border-red-400/20">
            Clear
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3" style={{ maxHeight: '420px', minHeight: '300px' }}>
        {chatMessages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center py-8 text-center">
            <div className="w-14 h-14 rounded-2xl flex items-center justify-center mb-3 mx-auto"
              style={{ background: 'rgba(14,165,233,0.12)', border: '1px solid rgba(14,165,233,0.25)' }}>
              <svg className="w-6 h-6 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <p className="text-white/60 text-sm font-medium mb-1">Start describing your HCP visit</p>
            <p className="text-white/30 text-xs mb-5">Type or use the microphone to dictate</p>
            <div className="space-y-2 w-full max-w-xs">
              {examplePrompts.map((p, i) => (
                <button key={i} onClick={() => setInput(p)}
                  className="smooth w-full text-left text-xs px-3 py-2.5 rounded-xl text-white/50 hover:text-white/80 hover:bg-white/5 border border-white/8 hover:border-white/15 truncate">
                  "{p}"
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {chatMessages.map((message, index) => (
              <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex flex-col ${message.role === 'user' ? 'items-end' : 'items-start'} max-w-[85%]`}>
                  {message.role === 'assistant' && (
                    <div className="flex items-center space-x-1.5 mb-1">
                      <div className="w-4 h-4 rounded-full flex items-center justify-center"
                        style={{ background: 'linear-gradient(135deg, #0284c7, #0ea5e9)' }}>
                        <svg className="w-2 h-2 text-white" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M10 2a6 6 0 00-6 6v3.586l-.707.707A1 1 0 004 14h12a1 1 0 00.707-1.707L16 11.586V8a6 6 0 00-6-6z"/>
                        </svg>
                      </div>
                      <span className="text-white/30 text-xs">AI Assistant</span>
                    </div>
                  )}

                  <div className={`rounded-2xl px-4 py-3 text-sm shadow-md ${
                    message.role === 'user'
                      ? 'text-white rounded-tr-sm'
                      : 'text-white/90 rounded-tl-sm'
                  }`}
                    style={message.role === 'user'
                      ? { background: 'linear-gradient(135deg, #0284c7, #0ea5e9)' }
                      : { background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.1)' }}>
                    <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                  </div>

                  {message.role === 'assistant' && (
                    <button onClick={() => speak(message.content, index)}
                      className={`smooth mt-1.5 flex items-center space-x-1.5 text-xs px-2.5 py-1 rounded-full border ${
                        speakingMessageId === index
                          ? 'text-sky-300 border-sky-500/40 bg-sky-500/10'
                          : 'text-white/30 border-white/10 hover:text-white/60 hover:border-white/20 hover:bg-white/5'
                      }`}>
                      {speakingMessageId === index ? (
                        <>
                          <span className="flex items-end space-x-0.5 h-3">
                            <span className="w-0.5 h-full bg-sky-400 rounded-full audio-bar"></span>
                            <span className="w-0.5 h-full bg-sky-400 rounded-full audio-bar"></span>
                            <span className="w-0.5 h-full bg-sky-400 rounded-full audio-bar"></span>
                          </span>
                          <span>Stop</span>
                        </>
                      ) : (
                        <>
                          <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"/>
                          </svg>
                          <span>Speak</span>
                        </>
                      )}
                    </button>
                  )}
                </div>
              </div>
            ))}

            {aiProcessing && (
              <div className="flex justify-start">
                <div className="flex items-center space-x-3 px-4 py-3 rounded-2xl rounded-tl-sm"
                  style={{ background: 'rgba(255,255,255,0.08)', border: '1px solid rgba(255,255,255,0.1)' }}>
                  <div className="flex space-x-1 items-center">
                    <div className="w-2 h-2 rounded-full bg-sky-400 animate-bounce"></div>
                    <div className="w-2 h-2 rounded-full bg-sky-400 animate-bounce" style={{ animationDelay: '0.15s' }}></div>
                    <div className="w-2 h-2 rounded-full bg-sky-400 animate-bounce" style={{ animationDelay: '0.3s' }}></div>
                  </div>
                  <span className="text-white/40 text-xs">AI is processing...</span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-white/8" style={{ background: 'rgba(0,0,0,0.2)' }}>
        {isListening && (
          <div className="mb-3 flex items-center space-x-2 px-3 py-2 rounded-xl"
            style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)' }}>
            <div className="relative w-3 h-3 flex-shrink-0">
              <div className="w-3 h-3 rounded-full bg-red-500 animate-ping absolute"></div>
              <div className="w-3 h-3 rounded-full bg-red-500 relative"></div>
            </div>
            <span className="text-red-400 text-xs font-semibold">Listening... speak now</span>
          </div>
        )}

        <div className="flex items-end space-x-2">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={isListening ? "Listening to your voice..." : "Describe your HCP interaction..."}
              rows={2}
              disabled={aiProcessing}
              className="w-full pl-4 pr-12 py-3 text-sm rounded-xl resize-none disabled:opacity-50 smooth placeholder-white/20 text-white/90"
              style={{
                background: 'rgba(255,255,255,0.07)',
                border: isListening ? '1px solid rgba(239,68,68,0.5)' : '1px solid rgba(255,255,255,0.12)',
                outline: 'none',
              }}
              onFocus={(e) => e.target.style.borderColor = 'rgba(139,92,246,0.6)'}
              onBlur={(e) => e.target.style.borderColor = isListening ? 'rgba(239,68,68,0.5)' : 'rgba(255,255,255,0.12)'}
            />
            {/* Microphone Button */}
            <button
              onClick={toggleListening}
              disabled={aiProcessing}
              className={`absolute right-3 bottom-2.5 w-7 h-7 rounded-lg flex items-center justify-center smooth disabled:opacity-40 ${
                isListening
                  ? 'bg-red-500 text-white mic-active'
                  : 'text-white/30 hover:text-white/60 hover:bg-white/10'
              }`}
              title={isListening ? "Stop recording" : "Start voice dictation"}>
              {isListening ? (
                <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 002 0V8a1 1 0 00-1-1zm4 0a1 1 0 00-1 1v4a1 1 0 002 0V8a1 1 0 00-1-1z" clipRule="evenodd"/>
                </svg>
              ) : (
                <svg className="w-4 h-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 005.946 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd"/>
                </svg>
              )}
            </button>
          </div>

          {/* Send Button */}
          <button
            onClick={handleSend}
            disabled={aiProcessing || !input.trim()}
            className="btn-gradient w-12 h-[72px] rounded-xl flex items-center justify-center flex-shrink-0">
            {aiProcessing ? (
              <svg className="animate-spin w-4 h-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
            ) : (
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
              </svg>
            )}
          </button>
        </div>

        <div className="flex items-center justify-between mt-2 px-1">
          <span className="text-white/20 text-xs">Press Enter to send · Shift+Enter for new line</span>
          <span className="text-white/20 text-xs">{input.length} chars</span>
        </div>
      </div>
    </div>
  );
};

export default AIChatPanel;
