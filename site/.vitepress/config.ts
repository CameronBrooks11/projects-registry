import { defineConfig } from 'vitepress'

// GitHub Pages (project site) needs a base; local dev uses "/"
export default defineConfig({
  title: 'Projects Registry',
  description: 'Data-driven index of open projects',
  srcDir: '.',
  base: process.env.GITHUB_ACTIONS ? '/projects-registry/' : '/',
  themeConfig: {
    nav: [{ text: 'Home', link: '/' }],
  },
  vite: {
    // Allow importing JSON built into /dist from the repo root
    server: { fs: { strict: false } }
  }
})
