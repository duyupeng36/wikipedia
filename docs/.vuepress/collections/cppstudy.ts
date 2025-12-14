import { defineCollection } from 'vuepress-theme-plume'

export default defineCollection({
  // doc 类型，该类型带有侧边栏
  type: 'doc',
  // 文档集合所在目录，相对于 `docs`
  dir: 'cppstudy',
  // `dir` 所指向的目录中的所有 markdown 文件，其 permalink 需要以 `linkPrefix` 配置作为前缀
  // 如果 前缀不一致，则无法生成侧边栏。
  // 所以请确保  markdown 文件的 permalink 都以 `linkPrefix` 开头
  linkPrefix: '/cppstudy',
  // 文档标题，它将用于在页面的面包屑导航中显示
  title: 'cppstudy',
  // 手动配置侧边栏结构
  sidebar: [
    {
      text: 'C++: 基础语法',
      collapsed: true,
      items: [
        {
          text: "第一章 基本概念",
          link: '001-基本概念.md'
        },
        {
          text: "第二章 基本数据类型",
          link: '002-基本数据类型.md'
        },
        {
          text: "第三章 处理基本数据类型",
          link: '003-处理基本数据类型.md'
        },
        {
          text: "第四章 决策",
          link: '004-决策.md'
        },
        {
          text: "第五章 数组和循环",
          link: '005-数组和循环.md'
        },
        {
          text: "第六章 指针和引用",
          link: '006-指针和引用.md'
        },
        {
          text: "第七章 操作字符串",
          link: '007-操作字符串.md'
        },
      ]
    },
  ],
  sidebarCollapsed: true,
})