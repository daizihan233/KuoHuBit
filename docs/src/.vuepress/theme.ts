import {hopeTheme} from "vuepress-theme-hope";
import {zhNavbar} from "./navbar/index.js";
import {zhSidebar} from "./sidebar/index.js";

export default hopeTheme({
    hostname: "https://bot.khbit.cn",

    author: {
        name: "KuoHu",
        url: "https://khbit.cn",
    },

    iconAssets: "iconfont",

    logo: "/logo.svg",

    repo: "daizihan233/KuoHuBit",

    docsDir: "docs/src",

    locales: {
        /**
         * Chinese locale config
         */
        "/": {
            // navbar
            navbar: zhNavbar,

            // sidebar
            sidebar: zhSidebar,

            footer: "今天你写Bug了吗？",

            displayFooter: true,

            // page meta
            metaLocales: {
                editLink: "在 GitHub 上编辑此页",
            },
        },
    },

    encrypt: {
        config: {
            "/demo/sese.html": ["bukeyisese"]
        },
    },

    plugins: {
        comment: {
            /**
             * Using Giscus
             */
            // provider: "Giscus",
            // repo: "vuepress-theme-hope/giscus-discussions",
            // repoId: "R_kgDOG_Pt2A",
            // category: "Announcements",
            // categoryId: "DIC_kwDOG_Pt2M4COD69",

            /**
             * Using Twikoo
             */
            // provider: "Twikoo",
            // envId: "https://twikoo.ccknbc.vercel.app",

            /**
             * Using Waline
             */
            provider: "Waline",
            serverURL: "https://bdoc-waline-git-whitesource-configure-hantools-foxmailcom.vercel.app",
            emoji: [
                '//unpkg.com/@waline/emojis@1.1.0/bmoji',
                '//unpkg.com/@waline/emojis@1.1.0/bilibili',
                '//unpkg.com/@waline/emojis@1.1.0/qq',
            ],
            requiredMeta: ['nick', 'mail']
        },

        // all features are enabled for demo, only preserve features you need here
        mdEnhance: {
            align: true,
            attrs: true,
            chart: true,
            codetabs: true,
            demo: true,
            echarts: true,
            figure: true,
            flowchart: true,
            gfm: true,
            imgLazyload: true,
            imgSize: true,
            include: true,
            katex: true,
            mark: true,
            mermaid: true,
            playground: {
                presets: ["ts", "vue"],
            },
            presentation: {
                plugins: ["highlight", "math", "search", "notes", "zoom"],
            },
            stylize: [
                {
                    matcher: "Recommended",
                    replacer: ({tag}) => {
                        if (tag === "em")
                            return {
                                tag: "Badge",
                                attrs: {type: "tip"},
                                content: "Recommended",
                            };
                    },
                },
            ],
            sub: true,
            sup: true,
            tabs: true,
            vPre: true,
            vuePlayground: true,
        },

        // uncomment these if you want a pwa
        // pwa: {
        //   favicon: "/favicon.ico",
        //   cacheHTML: true,
        //   cachePic: true,
        //   appendBase: true,
        //   apple: {
        //     icon: "/assets/icon/apple-icon-152.png",
        //     statusBarColor: "black",
        //   },
        //   msTile: {
        //     image: "/assets/icon/ms-icon-144.png",
        //     color: "#ffffff",
        //   },
        //   manifest: {
        //     icons: [
        //       {
        //         src: "/assets/icon/chrome-mask-512.png",
        //         sizes: "512x512",
        //         purpose: "maskable",
        //         type: "image/png",
        //       },
        //       {
        //         src: "/assets/icon/chrome-mask-192.png",
        //         sizes: "192x192",
        //         purpose: "maskable",
        //         type: "image/png",
        //       },
        //       {
        //         src: "/assets/icon/chrome-512.png",
        //         sizes: "512x512",
        //         type: "image/png",
        //       },
        //       {
        //         src: "/assets/icon/chrome-192.png",
        //         sizes: "192x192",
        //         type: "image/png",
        //       },
        //     ],
        //     shortcuts: [
        //       {
        //         name: "Demo",
        //         short_name: "Demo",
        //         url: "/demo/",
        //         icons: [
        //           {
        //             src: "/assets/icon/guide-maskable.png",
        //             sizes: "192x192",
        //             purpose: "maskable",
        //             type: "image/png",
        //           },
        //         ],
        //       },
        //     ],
        //   },
        // },
    },
});
