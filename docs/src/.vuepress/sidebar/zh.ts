import {sidebar} from "vuepress-theme-hope";

export const zhSidebar = sidebar({
    "/": [
        "",
        {
            icon: "discover",
            text: "使用",
            prefix: "demo/",
            link: "demo/",
            children: "structure",
        },
        {
            text: "构建",
            icon: "note",
            prefix: "guide/",
            link: "guide/",
            children: [
                "step1",
                "step2",
                "step3"
            ],
        }
    ],
});