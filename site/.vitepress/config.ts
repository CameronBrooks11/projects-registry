import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Projects Registry',
  description: 'Data-driven index of open projects',
  srcDir: '.',
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' }
    ]
  },
  vite: {
    server: { fs: { strict: false } } // allow importing dist/index.json
  }
})
