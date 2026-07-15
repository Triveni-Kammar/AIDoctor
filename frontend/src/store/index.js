import { createStore, applyMiddleware, combineReducers } from 'redux';
import { thunk } from 'redux-thunk';
import interactionReducer from './reducers';

const rootReducer = combineReducers({
  interaction: interactionReducer,
});

const store = createStore(rootReducer, applyMiddleware(thunk));

export default store;
