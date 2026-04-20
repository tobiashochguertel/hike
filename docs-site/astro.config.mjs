import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://tobiashochguertel.github.io',
  base: '/hike',
  output: 'static',
  integrations: [
    starlight({
      title: 'Hike',
      description: 'Documentation for the Hike Markdown browser fork maintained by Tobias Hochguertel.',
      disable404Route: true,
      social: [
        { icon: 'github', label: 'GitHub', href: 'https://github.com/tobiashochguertel/hike' },
      ],
      customCss: ['./src/styles/custom.css'],
      expressiveCode: {
        themes: ['github-dark', 'github-light'],
      },
      sidebar: [
        {
          label: 'Start Here',
          items: [
            { label: 'Overview', slug: 'index' },
            { label: 'Getting Started', slug: 'guides/getting-started' },
            { label: 'Viewing & Navigation', slug: 'guides/viewing-and-navigation' },
          ],
        },
        {
          label: 'CLI Reference',
          items: [
            { label: 'CLI Overview', slug: 'cli' },
            {
              label: 'Commands',
              items: [
                { label: 'open', slug: 'cli/open' },
                { label: 'config', slug: 'cli/config' },
                { label: 'schema', slug: 'cli/schema' },
                { label: 'env', slug: 'cli/env' },
                { label: 'bindings & themes', slug: 'cli/bindings-and-themes' },
              ],
            },
            { label: 'In-App Command Line', slug: 'commands' },
          ],
        },
        {
          label: 'Configuration',
          items: [
            { label: 'Overview', slug: 'configuration' },
            { label: 'Files, Environment & Schemas', slug: 'configuration/files-and-environment' },
            { label: 'Keybindings', slug: 'configuration/keybindings' },
            { label: 'File Browser & Startup', slug: 'configuration/file-browser-and-startup' },
            { label: 'UI, Layout & Content', slug: 'configuration/ui-and-content' },
          ],
        },
        {
          label: 'Project',
          items: [
            { label: 'License', slug: 'license' },
            { label: 'Change Log', slug: 'changelog' },
          ],
        },
      ],
    }),
  ],
});
