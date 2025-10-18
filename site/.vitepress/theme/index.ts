import DefaultTheme from 'vitepress/theme'
import ProjectList from './components/ProjectList.vue'
import FilterBar from './components/FilterBar.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('ProjectList', ProjectList)
    app.component('FilterBar', FilterBar)
  },
}
