import { defineConfig } from 'vitepress'

// Explicit base for GitHub Pages project site
// Local dev runs at "/", Pages runs at "/projects-registry/"
export default defineConfig({
  title: 'Projects Registry',
  description: 'Data-driven index of open projects',
  srcDir: '.',
  base: process.env.GITHUB_ACTIONS ? '/projects-registry/' : '/',
  themeConfig: {
    nav: [{ text: 'Home', link: '/' }],
    sidebar: false,
  },
  vite: {
    // Allow VitePress to import the JSON dataset from dist/
    server: { fs: { strict: false } },
  },
})
