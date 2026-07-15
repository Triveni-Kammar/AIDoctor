import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const updateFormField = (field, value) => ({
  type: 'UPDATE_FORM_FIELD',
  payload: { field, value }
});

export const updateFormData = (data) => ({
  type: 'UPDATE_FORM_DATA',
  payload: data
});

export const resetForm = () => ({
  type: 'RESET_FORM'
});

export const setHcpSearchResults = (results) => ({
  type: 'SET_HCP_SEARCH_RESULTS',
  payload: results
});

export const setMaterials = (materials) => ({
  type: 'SET_MATERIALS',
  payload: materials
});

export const setSamples = (samples) => ({
  type: 'SET_SAMPLES',
  payload: samples
});

export const addMaterial = (material) => ({
  type: 'ADD_MATERIAL',
  payload: material
});

export const removeMaterial = (index) => ({
  type: 'REMOVE_MATERIAL',
  payload: index
});

export const addSample = (sample) => ({
  type: 'ADD_SAMPLE',
  payload: sample
});

export const removeSample = (index) => ({
  type: 'REMOVE_SAMPLE',
  payload: index
});

export const setLoading = (loading) => ({
  type: 'SET_LOADING',
  payload: loading
});

export const setError = (error) => ({
  type: 'SET_ERROR',
  payload: error
});

export const setAiProcessing = (processing) => ({
  type: 'SET_AI_PROCESSING',
  payload: processing
});

export const addChatMessage = (message) => ({
  type: 'ADD_CHAT_MESSAGE',
  payload: message
});

export const clearChatMessages = () => ({
  type: 'CLEAR_CHAT_MESSAGES'
});

export const setInteractionId = (id) => ({
  type: 'SET_INTERACTION_ID',
  payload: id
});

// Async actions
export const searchHCPs = (query) => async (dispatch) => {
  try {
    dispatch(setLoading(true));
    const response = await axios.get(`${API_URL}/api/hcps/search`, {
      params: { query }
    });
    dispatch(setHcpSearchResults(response.data.results));
  } catch (error) {
    dispatch(setError(error.message));
  } finally {
    dispatch(setLoading(false));
  }
};

export const fillFormFromDescription = (description) => async (dispatch) => {
  try {
    dispatch(setAiProcessing(true));
    const response = await axios.post(`${API_URL}/api/agent/fill-form`, {
      description
    });
    dispatch(updateFormData(response.data.form_data));
    dispatch(addChatMessage({
      role: 'assistant',
      content: 'I\'ve filled the form based on your description. Please review and let me know if any corrections are needed.'
    }));
    return response.data;
  } catch (error) {
    dispatch(setError(error.message));
    throw error;
  } finally {
    dispatch(setAiProcessing(false));
  }
};

export const correctFormData = (currentData, correctionInstruction) => async (dispatch) => {
  try {
    dispatch(setAiProcessing(true));
    const response = await axios.post(`${API_URL}/api/agent/correct`, {
      current_data: currentData,
      correction_instruction: correctionInstruction
    });
    dispatch(updateFormData(response.data.corrected_data));
    dispatch(addChatMessage({
      role: 'assistant',
      content: 'I\'ve applied the correction. Please review the updated form.'
    }));
    return response.data;
  } catch (error) {
    dispatch(setError(error.message));
    throw error;
  } finally {
    dispatch(setAiProcessing(false));
  }
};

export const logInteraction = (interactionData) => async (dispatch) => {
  try {
    dispatch(setLoading(true));
    const response = await axios.post(`${API_URL}/api/interactions/log`, interactionData);
    dispatch(setInteractionId(response.data.id));
    return response.data;
  } catch (error) {
    dispatch(setError(error.message));
    throw error;
  } finally {
    dispatch(setLoading(false));
  }
};

export const chatWithAgent = (message, conversationHistory) => async (dispatch, getState) => {
  try {
    dispatch(setAiProcessing(true));
    dispatch(addChatMessage({ role: 'user', content: message }));
    
    // Get the current form data from Redux state
    const { formData } = getState().interaction;
    
    // Clean history to ensure correct payload format
    const cleanHistory = (conversationHistory || [])
      .filter(m => m.role === 'user' || m.role === 'assistant')
      .map(m => ({ role: m.role, content: m.content }));

    const response = await axios.post(`${API_URL}/api/agent/chat`, {
      message,
      conversation_history: cleanHistory,
      current_form_data: formData
    });
    
    dispatch(addChatMessage({
      role: 'assistant',
      content: response.data.response
    }));

    if (response.data.form_data) {
      dispatch(updateFormData(response.data.form_data));
    }
    
    return response.data;
  } catch (error) {
    dispatch(setError(error.message));
    throw error;
  } finally {
    dispatch(setAiProcessing(false));
  }
};

export const suggestFollowups = (interactionContext) => async (dispatch) => {
  try {
    const response = await axios.post(`${API_URL}/api/agent/suggest-followups`, {
      interaction_context: interactionContext
    });
    dispatch(updateFormData({ ai_suggested_followups: response.data.suggestions }));
    return response.data;
  } catch (error) {
    dispatch(setError(error.message));
    throw error;
  }
};
