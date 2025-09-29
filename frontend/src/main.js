import './index.css'

import { createPinia } from 'pinia'
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import {
  Alert,
  Badge,
  Button,
  Card,
  Dialog,
  ErrorMessage,
  FeatherIcon,
  frappeRequest,
  FrappeUI,
  Input,
  setConfig,
} from 'frappe-ui'

// create a pinia instance
let pinia = createPinia()

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)
app.use(FrappeUI)
app.use(pinia)
app.use(router)

// Register global components
app.component('Button', Button)
app.component('Input', Input)
app.component('ErrorMessage', ErrorMessage)
app.component('Dialog', Dialog)
app.component('Alert', Alert)
app.component('Badge', Badge)
app.component('FeatherIcon', FeatherIcon)
app.component('Card', Card)

app.mount('#app')
