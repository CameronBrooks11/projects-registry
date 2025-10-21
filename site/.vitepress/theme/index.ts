import DefaultTheme from 'vitepress/theme'
import ProjectList from './components/ProjectList.vue'
import FilterBar from './components/FilterBar.vue'
import PendingList from './components/PendingList.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('ProjectList', ProjectList)
    app.component('FilterBar', FilterBar)
    app.component('PendingList', PendingList)
  },
}
