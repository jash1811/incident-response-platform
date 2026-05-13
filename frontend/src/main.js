import { createApp } from 'vue'
import { Quasar, Notify, Dialog, Loading } from 'quasar'
import { createPinia } from 'pinia'
import router from './router/index'
import App from './App.vue'

// Quasar icon font + CSS (dist build — works with plain Vite)
import '@quasar/extras/material-icons/material-icons.css'
import '@quasar/extras/roboto-font/roboto-font.css'
import 'quasar/dist/quasar.css'

// App-level styles
import './css/app.scss'

const app = createApp(App)

app.use(Quasar, {
  plugins: { Notify, Dialog, Loading },
  config: {
    notify: {
      position: 'top-right',
      timeout: 3000,
    },
  },
})

app.use(createPinia())
app.use(router)

app.mount('#app')
