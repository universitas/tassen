import { Provider } from 'react-redux'
import configureStore from './configureStore'
import App from './App'

export const rootStore = configureStore()

export default () => (
  <Provider store={rootStore}>
    <App />
  </Provider>
)