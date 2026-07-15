const initialState = {
  formData: {
    hcp_name: '',
    hcp_id: null,
    interaction_type: 'Meeting',
    date: '',
    time: '',
    attendees: '',
    topics_discussed: '',
    sentiment: 'Neutral',
    outcomes: '',
    follow_up_actions: '',
    materials_shared: [],
    samples_distributed: [],
    ai_suggested_followups: [],
    voice_note_summary: ''
  },
  hcpSearchResults: [],
  materials: [],
  samples: [],
  loading: false,
  error: null,
  aiProcessing: false,
  chatMessages: [],
  interactionId: null
};

const interactionReducer = (state = initialState, action) => {
  switch (action.type) {
    case 'UPDATE_FORM_FIELD':
      return {
        ...state,
        formData: {
          ...state.formData,
          [action.payload.field]: action.payload.value
        }
      };
    
    case 'UPDATE_FORM_DATA':
      return {
        ...state,
        formData: {
          ...state.formData,
          ...action.payload
        }
      };
    
    case 'RESET_FORM':
      return {
        ...state,
        formData: initialState.formData,
        interactionId: null
      };
    
    case 'SET_HCP_SEARCH_RESULTS':
      return {
        ...state,
        hcpSearchResults: action.payload
      };
    
    case 'SET_MATERIALS':
      return {
        ...state,
        materials: action.payload
      };
    
    case 'SET_SAMPLES':
      return {
        ...state,
        samples: action.payload
      };
    
    case 'ADD_MATERIAL':
      return {
        ...state,
        formData: {
          ...state.formData,
          materials_shared: [...state.formData.materials_shared, action.payload]
        }
      };
    
    case 'REMOVE_MATERIAL':
      return {
        ...state,
        formData: {
          ...state.formData,
          materials_shared: state.formData.materials_shared.filter((_, index) => index !== action.payload)
        }
      };
    
    case 'ADD_SAMPLE':
      return {
        ...state,
        formData: {
          ...state.formData,
          samples_distributed: [...state.formData.samples_distributed, action.payload]
        }
      };
    
    case 'REMOVE_SAMPLE':
      return {
        ...state,
        formData: {
          ...state.formData,
          samples_distributed: state.formData.samples_distributed.filter((_, index) => index !== action.payload)
        }
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload
      };
    
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload
      };
    
    case 'SET_AI_PROCESSING':
      return {
        ...state,
        aiProcessing: action.payload
      };
    
    case 'ADD_CHAT_MESSAGE':
      return {
        ...state,
        chatMessages: [...state.chatMessages, action.payload]
      };
    
    case 'CLEAR_CHAT_MESSAGES':
      return {
        ...state,
        chatMessages: []
      };
    
    case 'SET_INTERACTION_ID':
      return {
        ...state,
        interactionId: action.payload
      };
    
    default:
      return state;
  }
};

export default interactionReducer;
