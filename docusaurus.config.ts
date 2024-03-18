import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: '🐍 Python-Basis-Notes',
  tagline: '你的Python入门好帮手：一份包含了Python基础学习需要的知识框架 🐍 + 爬虫基础 🕷️ + numpy基础 📊 + pandas基础 🐼 + 深度学习 🍥 + 脚本库 📚',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://zhiyu1998.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/Python-Basis-Notes/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'facebook', // Usually your GitHub org/user name.
  projectName: 'docusaurus', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        },
        blog: {
          showReadingTime: true,
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/facebook/docusaurus/tree/main/packages/create-docusaurus/templates/shared/',
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    // Replace with your project's social card
    image: 'img/docusaurus-social-card.jpg',
    navbar: {
      title: 'Python-Basis-Notes',
      logo: {
        alt: 'My Site Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: '文档',
        },
        // {to: '/blog', label: 'Blog', position: 'left'},
        {
          href: 'https://github.com/zhiyu1998/Python-Basis-Notes',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: '文档',
          items: [
            {
              label: '点击进入',
              to: '/docs/intro',
            },
          ],
        },
        {
          title: '另一个文档',
          items: [
            {
              label: 'Java基础',
              href: 'https://zhiyu1998.github.io/Computer-Science-Learn-Notes/Java/basic/basic.html',
            },
            {
              label: 'Java大厂面试',
              href: 'https://zhiyu1998.github.io/Computer-Science-Learn-Notes/Java/eightpart/giant.html',
            },
          ],
        },
        {
          title: '更多',
          items: [
            // {
            //   label: '博客（未来）',
            //   to: '/blog',
            // },
            {
              label: 'GitHub',
              href: 'https://github.com/zhiyu1998/Python-Basis-Notes',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Python-Basis-Notes, Inc. Built with zhiyu1998.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
