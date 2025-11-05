import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'

// Font Awesome
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faServer,
  faFileAlt,
  faCloudUploadAlt,
  faFile,
  faTimes,
  faUpload,
  faSpinner,
  faCheckCircle,
  faExclamationCircle,
  faInfoCircle,
  faList,
  faArrowRight,
  faArrowLeft,
  faDatabase,
  faSyncAlt,
  faExclamationTriangle,
  faMicrochip,
  faGlobe,
  faNetworkWired,
  faMapMarkerAlt,
  faClock,
  faInbox,
  faPlayCircle,
  faStopCircle,
  faPauseCircle,
  faTimesCircle,
  faQuestionCircle,
  faCode,
  faEdit,
  faMagic,
  faEraser,
} from '@fortawesome/free-solid-svg-icons'

// Add icons to library
library.add(
  faServer,
  faFileAlt,
  faCloudUploadAlt,
  faFile,
  faTimes,
  faUpload,
  faSpinner,
  faCheckCircle,
  faExclamationCircle,
  faInfoCircle,
  faList,
  faArrowRight,
  faArrowLeft,
  faDatabase,
  faSyncAlt,
  faExclamationTriangle,
  faMicrochip,
  faGlobe,
  faNetworkWired,
  faMapMarkerAlt,
  faClock,
  faInbox,
  faPlayCircle,
  faStopCircle,
  faPauseCircle,
  faTimesCircle,
  faQuestionCircle,
  faCode,
  faEdit,
  faMagic,
  faEraser,
)

const app = createApp(App)

app.component('FontAwesomeIcon', FontAwesomeIcon)
app.use(router)
app.mount('#app')

