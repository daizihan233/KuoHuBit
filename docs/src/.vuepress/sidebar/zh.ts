// @ts-ignore
import {sidebar} from "vuepress-theme-hope";

export const zhSidebar = sidebar({
    "/": [
        "",
        {
            icon: "discover",
            text: "使用指南",
            prefix: "demo/",
            link: "demo/",
            children: "structure",
        },
        {
            text: "部署文档",
            icon: "note",
            prefix: "guide/",
            link: "guide/",
            children: [
                "step1",
                "step2",
                "step3"
            ],
        },
        {
            text: "疑难杂症",
            icon: "warn",
            prefix: "question/",
            link: "question/",
            children: "structure",
        }
    ],
});