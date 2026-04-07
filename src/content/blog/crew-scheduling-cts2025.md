---
title: "Crew Scheduling Problems in Airline Operations"
date: 2025-07-16 15:55:00 +0800
---

## Problem Statement

机组排班的目的是为各航班指派飞行所需的各岗位人员，同时结合机组人员的培训、休假等占位任务，生成特定时间段的日程安排。由于航班计划的变动，人员培训、值班、休假等占位任务的调整，机组排班通常在实际运行的前一周完成，属于航空公司的短期计划问题。
<svg version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 681.6131459980794 268.2680596938593" width="681.6131459980794" height="268.2680596938593"><!-- svg-source:excalidraw --><metadata></metadata><defs><style class="style-fonts">
      @font-face { font-family: Excalifont; src: url(data:font/woff2;base64,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); }</style></defs><rect x="0" y="0" width="681.6131459980794" height="268.2680596938593" fill="#ffffff"></rect><g stroke-linecap="round"><g transform="translate(181.78043440811496 52.94935729571523) rotate(0 228.10957048826566 -0.7930161046046891)"><path d="M-0.49 1.03 C75.25 0.5, 379.08 -1.78, 455.14 -2.26 M1.45 0.53 C77.5 0.06, 381.71 -0.88, 457.28 -1.07" stroke="#1e1e1e" stroke-width="2" fill="none"></path></g><g transform="translate(181.78043440811496 52.94935729571523) rotate(0 228.10957048826566 -0.7930161046046891)"><path d="M433.81 7.55 C443.79 2.79, 449.27 0.93, 457.28 -1.07 M433.81 7.55 C439.66 4.2, 446.36 2.23, 457.28 -1.07" stroke="#1e1e1e" stroke-width="2" fill="none"></path></g><g transform="translate(181.78043440811496 52.94935729571523) rotate(0 228.10957048826566 -0.7930161046046891)"><path d="M433.77 -9.55 C443.89 -8.25, 449.39 -4.04, 457.28 -1.07 M433.77 -9.55 C439.73 -8.07, 446.44 -5.19, 457.28 -1.07" stroke="#1e1e1e" stroke-width="2" fill="none"></path></g></g><mask></mask><g transform="translate(610.9139272480794 14.397163839752011) rotate(0 30.349609375 16.27619931313231)"><text x="0" y="22.9429305517913" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="26.04191890101169px" fill="#1e1e1e" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">Time</text></g><g stroke-linecap="round"><g transform="translate(173.2761424279192 123.4259968235401) rotate(0 237.67590919621853 -2.7778020336536002)"><path d="M0 0 C79.23 -0.93, 396.13 -4.63, 475.35 -5.56 M0 0 C79.23 -0.93, 396.13 -4.63, 475.35 -5.56" stroke="#1971c2" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(173.62336933782655 172.62520882609795) rotate(0 238.19676280668443 -2.7778152792585153)"><path d="M0 0 C79.4 -0.93, 396.99 -4.63, 476.39 -5.56 M0 0 C79.4 -0.93, 396.99 -4.63, 476.39 -5.56" stroke="#1971c2" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(171.88721491988258 74.7075778635681) rotate(0 236.2870247363979 -2.4305751237462943)"><path d="M0 0 C78.76 -0.81, 393.81 -4.05, 472.57 -4.86 M0 0 C78.76 -0.81, 393.81 -4.05, 472.57 -4.86" stroke="#a5d8ff" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(171.2462050780935 222.94618703289387) rotate(0 242.5370826235197 -1.7361279267341256)"><path d="M0 0 C80.85 -0.58, 404.23 -2.89, 485.07 -3.47 M0 0 C80.85 -0.58, 404.23 -2.89, 485.07 -3.47" stroke="#e03131" stroke-width="1" fill="none"></path></g></g><mask></mask><g transform="translate(140.11611492202357 62.20744884371953) rotate(0 8.801513671875 16.27619931313231)"><text x="0" y="22.9429305517913" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="26.04191890101169px" fill="#a5d8ff" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">A</text></g><g transform="translate(139.12652253360935 107.73740107320064) rotate(0 9.908218383789062 16.276199313132306)"><text x="0" y="22.9429305517913" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="26.04191890101169px" fill="#1971c2" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">B</text></g><g transform="translate(139.82097635342396 157.04345008717533) rotate(0 8.1895751953125 16.276199313132306)"><text x="0" y="22.9429305517913" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="26.04191890101169px" fill="#1971c2" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">C</text></g><g transform="translate(138.43207533659717 204.26615088731106) rotate(0 10.155593872070312 16.276199313132306)"><text x="0" y="22.9429305517913" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="26.04191890101169px" fill="#e03131" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">D</text></g><g stroke-linecap="round"><g transform="translate(259.75458433901963 122.88008699112991) rotate(0 14.573830038440107 48.08325571300923)"><path d="M-0.24 0.99 C4.71 16.87, 24.87 80.32, 29.91 96.07 M-1.83 0.46 C3.02 16.47, 24.11 81.55, 29.36 97.56" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(259.75458433901963 122.88008699112991) rotate(0 14.573830038440107 48.08325571300923)"><path d="M13.96 77.86 C20.58 85.36, 23.62 91.69, 29.36 97.56 M13.96 77.86 C18.6 82.89, 22.28 86.98, 29.36 97.56" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(259.75458433901963 122.88008699112991) rotate(0 14.573830038440107 48.08325571300923)"><path d="M30.22 72.57 C31.76 81.71, 29.68 89.7, 29.36 97.56 M30.22 72.57 C30.84 78.86, 30.54 84.23, 29.36 97.56" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(259.00856104109545 95.53927833584633) rotate(0 6.104509199182203 -10.082684207596337)"><path d="M-0.42 0.51 C1.68 -2.98, 10.04 -17.18, 12.22 -20.58 M0.36 0.3 C2.43 -3.17, 9.77 -16.57, 11.8 -20.09" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(259.00856104109545 95.53927833584633) rotate(0 6.104509199182203 -10.082684207596337)"><path d="M9.89 -8.46 C10.84 -11.09, 10.28 -13.25, 11.8 -20.09 M9.89 -8.46 C10.82 -12.37, 11.49 -16.28, 11.8 -20.09" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(259.00856104109545 95.53927833584633) rotate(0 6.104509199182203 -10.082684207596337)"><path d="M2.86 -12.41 C5.42 -14.11, 6.47 -15.37, 11.8 -20.09 M2.86 -12.41 C6.22 -14.92, 9.35 -17.45, 11.8 -20.09" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(472.290777486751 218.61925342815888) rotate(0 24.439328068514527 -73.3447387991222)"><path d="M0 0 C8.15 -24.45, 40.73 -122.24, 48.88 -146.69 M0 0 C8.15 -24.45, 40.73 -122.24, 48.88 -146.69" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(472.290777486751 218.61925342815888) rotate(0 24.439328068514527 -73.3447387991222)"><path d="M49.56 -121.7 C49.37 -128.8, 49.17 -135.91, 48.88 -146.69 M49.56 -121.7 C49.36 -128.98, 49.16 -136.27, 48.88 -146.69" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(472.290777486751 218.61925342815888) rotate(0 24.439328068514527 -73.3447387991222)"><path d="M33.34 -127.1 C37.76 -132.67, 42.18 -138.24, 48.88 -146.69 M33.34 -127.1 C37.87 -132.81, 42.4 -138.52, 48.88 -146.69" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(218.76268881011097 220.54232370923356) rotate(0 12.105070436847953 -47.897148662073235)"><path d="M0 0 C4.04 -15.97, 20.18 -79.83, 24.21 -95.79 M0 0 C4.04 -15.97, 20.18 -79.83, 24.21 -95.79" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(218.76268881011097 220.54232370923356) rotate(0 12.105070436847953 -47.897148662073235)"><path d="M26.74 -70.92 C26.15 -76.75, 25.56 -82.57, 24.21 -95.79 M26.74 -70.92 C26.13 -76.93, 25.52 -82.94, 24.21 -95.79" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(218.76268881011097 220.54232370923356) rotate(0 12.105070436847953 -47.897148662073235)"><path d="M10.16 -75.11 C13.45 -79.96, 16.74 -84.8, 24.21 -95.79 M10.16 -75.11 C13.56 -80.11, 16.95 -85.11, 24.21 -95.79" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(575.5503160781153 166.48196757253928) rotate(0 12.927504575618542 -23.15727425203147)"><path d="M0 0 C4.31 -7.72, 21.55 -38.6, 25.86 -46.31 M0 0 C4.31 -7.72, 21.55 -38.6, 25.86 -46.31" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(575.5503160781153 166.48196757253928) rotate(0 12.927504575618542 -23.15727425203147)"><path d="M21.87 -21.63 C23 -28.64, 24.13 -35.64, 25.86 -46.31 M21.87 -21.63 C22.69 -26.71, 23.51 -31.8, 25.86 -46.31" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(575.5503160781153 166.48196757253928) rotate(0 12.927504575618542 -23.15727425203147)"><path d="M6.94 -29.97 C12.31 -34.61, 17.68 -39.25, 25.86 -46.31 M6.94 -29.97 C10.83 -33.33, 14.73 -36.7, 25.86 -46.31" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g transform="translate(10 139.9860249964645) rotate(0 62.54424285888672 10.875852238392035)"><text x="0" y="15.330601315237415" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="17.40136358142726px" fill="#1e1e1e" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">layover ariport</text></g><g transform="translate(198.6356309522497 149.42436315671563) rotate(0 17.19542694091797 11.869096175234626)"><text x="0" y="16.730677968610728" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="18.9905538803754px" fill="#2f9e44" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">a-11</text></g><g transform="translate(294.4899492067056 101.34709668350875) rotate(0 15.069122314453125 11.444303991525281)"><text x="0" y="16.131890906454036" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="18.31088638644045px" fill="#2f9e44" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">bus</text></g><g transform="translate(403.46529032451207 173.46305752688025) rotate(0 4.679954528808594 10.896214457867563)"><text x="0" y="15.359303899810117" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="17.4339431325881px" fill="#2f9e44" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">e</text></g><g transform="translate(232.59023784325834 96.53927833584633) rotate(0 18.141647338867188 12.670404327641783)"><text x="0" y="17.860201940243854" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="20.27264692422685px" fill="#2f9e44" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">b-11</text></g><g transform="translate(258.4319076514587 151.8283487474983) rotate(0 19.673538208007812 11.067803306217725)"><text x="0" y="15.601175540444505" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="17.70848528994836px" fill="#2f9e44" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">c-23</text></g><g transform="translate(16.73889508745816 207.11729689202807) rotate(0 56.412925720214844 11.765181584614343)"><text x="0" y="16.58419996167238" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="18.82429053538295px" fill="#1e1e1e" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">base ariport</text></g><g transform="translate(38.27988718349479 56.46645912713899) rotate(0 38.93022155761719 19.748479945937007)"><text x="0" y="13.918728665896404" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="15.798783956749608px" fill="#1e1e1e" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">no layover</text><text x="0" y="33.667208611833416" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="15.798783956749608px" fill="#1e1e1e" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">  ariport</text></g><g stroke-linecap="round"><g transform="translate(433.4015867146297 222.5922491863143) rotate(0 16.426419756199458 0)"><path d="M-0.54 -0.49 C4.82 -0.45, 26.85 0.03, 32.33 0.17 M0.18 0.44 C5.69 0.32, 27.76 -0.54, 33.29 -0.7" stroke="#e03131" stroke-width="4" fill="none"></path></g></g><mask></mask><g transform="translate(431.65136206685133 225.79735952882083) rotate(0 21.066513061523438 16.235350082519233)"><text x="0" y="11.442674738159555" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="12.988280066015385px" fill="#e03131" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">ground</text><text x="0" y="27.678024820678786" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="12.988280066015385px" fill="#e03131" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic"> duty</text></g><g stroke-linecap="round"><g transform="translate(595.1552856822987 71.4689281210911) rotate(0 22.142288510666077 72.99750322862708)"><path d="M0 0 C7.38 24.33, 36.9 121.66, 44.28 146 M0 0 C7.38 24.33, 36.9 121.66, 44.28 146" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(595.1552856822987 71.4689281210911) rotate(0 22.142288510666077 72.99750322862708)"><path d="M29.28 126 C34.38 132.79, 39.47 139.57, 44.28 146 M29.28 126 C34.35 132.75, 39.42 139.51, 44.28 146" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(595.1552856822987 71.4689281210911) rotate(0 22.142288510666077 72.99750322862708)"><path d="M45.65 121.03 C45.19 129.51, 44.72 137.98, 44.28 146 M45.65 121.03 C45.19 129.46, 44.73 137.9, 44.28 146" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask><g transform="translate(526.2900354688439 189.48894547399848) rotate(0 19.195632934570312 11.067818589608018)"><text x="0" y="15.601197083911462" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="17.70850974337283px" fill="#2f9e44" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">g-45</text></g><g transform="translate(479.8152630333289 124.58442176770505) rotate(0 6.470939636230469 16.276199313132306)"><text x="0" y="22.9429305517913" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="26.04191890101169px" fill="#2f9e44" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">f</text></g><g transform="translate(563.9506627621245 145.41797522858266) rotate(0 17.17535400390625 9.846764017604706)"><text x="0" y="13.87999855921559" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="15.754822428167525px" fill="#2f9e44" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">h-45</text></g><g stroke-linecap="round"><g transform="translate(538.8678024419814 219.9571977436313) rotate(0 15.528442008756315 -25.81071549859875)"><path d="M0.49 0.21 C5.84 -8.76, 26.4 -44.14, 31.31 -52.72 M-0.71 -0.73 C4.58 -9.07, 25.01 -43.58, 30.49 -51.77" stroke="#1e1e1e" stroke-width="0.5" fill="none"></path></g><g transform="translate(538.8678024419814 219.9571977436313) rotate(0 15.528442008756315 -25.81071549859875)"><path d="M25.29 -27.31 C26.64 -32.64, 25.66 -40.7, 30.49 -51.77 M25.29 -27.31 C26.69 -35.35, 28.64 -42.79, 30.49 -51.77" stroke="#1e1e1e" stroke-width="0.5" fill="none"></path></g><g transform="translate(538.8678024419814 219.9571977436313) rotate(0 15.528442008756315 -25.81071549859875)"><path d="M10.79 -36.37 C15.61 -39.64, 18.03 -45.58, 30.49 -51.77 M10.79 -36.37 C16.89 -41.44, 23.56 -45.94, 30.49 -51.77" stroke="#1e1e1e" stroke-width="0.5" fill="none"></path></g></g><mask></mask><g transform="translate(618.5275241300266 123.78314418207847) rotate(0 6.939659118652344 16.276199313132306)"><text x="0" y="22.9429305517913" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="26.04191890101169px" fill="#2f9e44" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">k</text></g><g stroke-linecap="round"><g transform="translate(293.8105225587995 73.27218257981013) rotate(0 15.20773329325402 47.799234728917796)"><path d="M-1.02 -0.28 C3.98 15.71, 24.02 79.49, 29.46 95.34" stroke="#1e1e1e" stroke-width="1.5" fill="none" stroke-dasharray="1.5 7"></path></g><g transform="translate(293.8105225587995 73.27218257981013) rotate(0 15.20773329325402 47.799234728917796)"><path d="M14.04 75.66 C17.41 79.22, 21.38 87.82, 29.46 95.34" stroke="#1e1e1e" stroke-width="1.5" fill="none" stroke-dasharray="1.5 5"></path></g><g transform="translate(293.8105225587995 73.27218257981013) rotate(0 15.20773329325402 47.799234728917796)"><path d="M30.3 70.36 C29.49 75.13, 29.32 85.08, 29.46 95.34" stroke="#1e1e1e" stroke-width="1.5" fill="none" stroke-dasharray="1.5 5"></path></g></g><mask></mask><g stroke-linecap="round"><g transform="translate(374.1060978080642 27.077476898758903) rotate(0 0.4006235094230526 107.77349351462269)"><path d="M0.74 -0.12 C0.83 35.6, 1.3 178.61, 1.5 214.67" stroke="#1e1e1e" stroke-width="1.5" fill="none" stroke-dasharray="8 9"></path></g></g><mask></mask><g transform="translate(483.98003273493885 10) rotate(0 31.391212463378906 16.27619931313231)"><text x="0" y="22.9429305517913" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="26.04191890101169px" fill="#1e1e1e" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">day2</text></g><g transform="translate(286.86265942595935 12.403863323660374) rotate(0 27.836753845214844 16.27619931313231)"><text x="0" y="22.9429305517913" font-family="Excalifont, Xiaolai, sans-serif, Segoe UI Emoji" font-size="26.04191890101169px" fill="#1e1e1e" text-anchor="start" style="white-space: pre;" direction="ltr" dominant-baseline="alphabetic">day1</text></g><g stroke-linecap="round"><g transform="translate(395.43703607374255 172.68111715570925) rotate(0 9.118083773231042 24.26988248918727)"><path d="M0 0 C3.04 8.09, 15.2 40.45, 18.24 48.54" stroke="#1e1e1e" stroke-width="1" fill="none" stroke-dasharray="8 8.5"></path></g><g transform="translate(395.43703607374255 172.68111715570925) rotate(0 9.118083773231042 24.26988248918727)"><path d="M1.97 29.56 C7.3 35.77, 12.62 41.99, 18.24 48.54" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g><g transform="translate(395.43703607374255 172.68111715570925) rotate(0 9.118083773231042 24.26988248918727)"><path d="M17.98 23.54 C18.06 31.73, 18.15 39.91, 18.24 48.54" stroke="#1e1e1e" stroke-width="1" fill="none"></path></g></g><mask></mask></svg>

---

**硬约束**（违反-10'）：
①`地勤任务`必须执行
②仅允许值勤日的`开始或结束`进行置位
③`地点衔接`
④有`资质`才能飞
⑤连接时间约束：`飞行或飞行置位`任务，飞机尾号不同，前序和后续任务间隔不小于3小时；`大巴置位`而言，与相邻飞行任务之间最小间隔时间为2小时。
⑥每个值勤日内`飞行任务`数量不超过4个，总任务数量不超过6个
⑦飞行值勤日开始前`最小休息时间`设为12小时
⑧飞行值勤日`总飞行时间`不超过8小时、`值勤时间`不超过12小时
⑨计划期内的`总飞行值勤时间`不得超过60小时

---

⑩ **值四休二**：一个飞行周期最多横跨4个日历日，并且飞行周期开始前必须连续休息2个完整的日历日
![Pasted image 20250717114107](/assets/posts/crew-scheduling-cts2025/attachments/Pasted%20image%2020250717114107.png)

```
情况①表示如果飞行周期中出现少于2个完整日历日的休息，则认为当前飞行周期尚未结束；如果出现2个及以上完整日历日的休息，则认为当前飞行周期已结束，可以开始新的飞行周期。

情况②③④表示飞行周期后可接置位或占位任务，此时不视为飞行周期，不参与横跨4个日历日的计算。但此后的飞行周期开始时间距离上一值勤日应保证2个完整日历日的休息，遵守则②合规，否则④违规；如果此后不包含飞行值勤日，认为不构成飞行周期，无需考虑2个完整日历日的休息。
```

---
**软约束**（违反-0.5'）：
①外站过夜：不在base过夜，但在layover airport过夜
②置位（大巴 or 航班）
③未覆盖航班（5' per）
**潜在约束**：
①计划期要从staystation出发
②两个连续休息日前尽可能回base
 `否则，会产生3次外站过夜的违规`

---

## Task

- **输入**：航班、机长、占位任务、大巴、资质匹配、可过夜机场等数据。
- **输出**：为期7天的每位机长的个人任务排班表。
- **目标**：最大化“飞行值勤日日均飞时”，同时最小化因“未覆盖航班”、“新增过夜站点”、“外站过夜天数”、“置位次数”和“违规次数”导致的扣分。
- **约束**：必须遵守地点衔接、时间衔接、任务数量、飞行时长、值勤时长、休息时间、值勤周期、总工时和资质共10大类规则。
**Input：**
<img src="/assets/posts/crew-scheduling-cts2025/attachments/Pasted%20image%2020250717130531.png" alt="Pasted image 20250717130531" width="600" loading="lazy" />

**Output：**
<img src="/assets/posts/crew-scheduling-cts2025/attachments/Pasted%20image%2020250717130721.png" alt="Pasted image 20250717130721" width="600" loading="lazy" />

---

## Challenge

1. 计划期是一个被*截断*的短周期。事实上计划期开始，并不能完全假定所有飞行员都是available
 `尤其是启发式方法，短视，可能会带来"资源雪崩"和"波谷效应"`
2. 可以在计划期前对部分飞行员进行*提前置位*。
 `但不知道理想置位地点`
3. 贪心方法会生成大量*低效FDP*，尽管能增加航班覆盖率，但会造成日均飞时的下降和大量的外站过夜和置位。（未解决）
 `必然会影响航班覆盖率，我们期待的是 尽可能多的形成高任务密度的FDP，如果仅仅是增加一个FDP去多覆盖2个航班，我们认为是效率不高的`
4. 以机长为中心 还是 以航班为中心 构造启发式算法
 `crew-focus更能考虑到机长的整个任务周期特性，但慢；flight-focus能较快的构造出一个性能还不错的初始解，但离最优的距离比较远`

## Methodology

```

```

### 贪心策略

1. 资质优先
 优先选择能飞航班较少的机组（“窄资质”机组）。逻辑是：这些机组的选择面很窄，先把他们能飞的、困难的任务分配掉，剩下更容易的任务可以留给“宽资质”的万能机组去解决。
2. 基地优先
 优先选择能让机组在模拟的“终点”回到基地的方案
3. 负潜力优先
 优先选择未来机会更多的方案，避免让机组飞到一个“死胡同”机场
4. 等待时间优先
 指两次任务间的“休息”时间。优先选择等待更短的方案，即衔接更紧凑的。
5. **分层资质策略**（仍可探索）
 - 第一梯队：“浅资质”机长
     - 定义：只能飞很少几种任务的“专才”。
     - 策略：最优先派遣。
     - 逻辑分析：最不灵活的资源，机会窗口窄。必须在第一时间，将那些只有他们能干的活儿分配给他们。*优先解决最受限问题*的策略。
 - 第二梯队：“高资质”机长
     - 定义：能飞很多种任务的“通才”或“万金油”。
     - 策略：次优先派遣。
     - 逻辑分析：最大化这些高资质机长的价值，因为这些机长通常能够形成更长的飞行任务链。避免后期无将可用：防止“通才”在后期被一些简单的任务占用，导致真正需要他们时却分身乏术。
 - 第三梯队：“一般资质”机长
     - 定义：资质数量居中的主力军。
     - 策略：最后派遣。
     - 逻辑分析：这是前两个策略执行后的自然结果。
6. FDP质量贪心策略：
 当一个未覆盖的航班（按时间顺序）需要被分配时，算法会为所有合格的机组生成候选的FDP方案。直接保证了生成的FDP是任务饱满、效率高的，从根本上提升了日均飞时，减少了总执勤日
 `但航班覆盖率捉襟见肘`

### 主动置位

**动机**：计划期开始前，crew的分布极不均匀。`一个合理的分布：base airport的crew适当过剩，layover airport仅有少量机长，供大于需`，但是现在的数据分布是`会存在一个特别的机场，其crew大大大大量聚集，远超正常的分布`。
当前的数据分布极不均匀，直接用贪心算法，会有大量crew资源被限制以至于被浪费
![Pasted image 20250717144913](/assets/posts/crew-scheduling-cts2025/attachments/Pasted%20image%2020250717144913.png)
**置位回base**：（PASS）
 针对 部分机场 将所有crew尽可能置位回各自的base
**两日闲人交集**：(PASS)

1. 对29日的所有航班进行一次**有逻辑**的预分配，这次分配至少要**尊重机长的初始位置和飞行资质**，确定29日的闲人集合`AA`。
2. 基于这个更真实的预分配结果，来确定29日结束后，每个机长的位置。
3. 用这个更准确的30日初始位置数据，去计算30日的闲人集合 `BB`。
这样，我们得到的 `BB` 集合与 `AA` 的交集也就是该机场未来两天的“闲人”，是可以毫无顾虑的置位，以支援其他机场。

![Pasted image 20250717161240](/assets/posts/crew-scheduling-cts2025/attachments/Pasted%20image%2020250717161240.png)

##### 逆转时间（Accept）

`一种基于动态规划 反向递推思想 的启发式方法`
本质上是一种两阶段式的启发式架构。
**第一阶段**：将时间轴逆转，从尾到头通过贪心算法生成排班计划。
 不用考虑staystation的约束，可以生成一个近似的 启发式的 理论最优解
**第二阶段**：
 **STEP1**：如果第一阶段 生成的理论最优排班计划 中，存在crew的最后到达地 和 staystation一致，我们认为这些crew的staystation本身就是ideal，因此这部分的crew的排班计划可以被认为是 ideal计划。因此`锁定`这部分crew的排班计划。若增加一趟主动提前置位能到ideal的，只有任务链合规，也锁定排班计划。
`原数据中大概有2/3的Crew的staystation和base相同，经过实验验证：大概有1/2的Crew的staystation就是ideal的`  &  `初步分析，对于crew而言base是ideal的可能性很大`
 **STEP2**：针对STEP1中未锁定的机长，尽可能将其置位回各自的base，实在回不去的就留在原地。更新staystation，将`未锁定Crew`和`未覆盖航班`带入正向贪心过程，生成排班计划。
 **STEP3**：合并两阶段的排班计划，共同构成初始解。
![Pasted image 20250717171518](/assets/posts/crew-scheduling-cts2025/attachments/Pasted%20image%2020250717171518.png)
**比较研究**，逆转时间的两阶段架构 和 单纯正向贪心架构的 对比如下，融合反向递推的两阶段架构能带来 航班覆盖率的大幅提升，但外站过夜和置位次数也大幅增加。
<img src="/assets/posts/crew-scheduling-cts2025/attachments/Pasted%20image%2020250717144608.png" alt="Pasted image 20250717144608" width="500" loading="lazy" />

### 中间改进过程

```
贪心算法部分，我们是以航班为中心，中间改进过程，我们真的飞行任务较少的飞行员，将其打乱，以Crew为中心，进行贪心搜索
```

### 融合策略

对于`正-反 两阶段`可以尝试在正反阶段采用不同的贪心策略，使初始解的结构不在单一，可能会更有利于后续的优化

### 立-破-立策略（未实现）

```
LNS or ALNS的哲学思想是在初始解基础上先破后立，那么后续优化过程的好坏就非常依赖于初始解的结构。

这种 初始解-优化 范式 的解耦结构 限制了优化模块的性能

能否 参考diffusion的思路，先在不考虑 任务重叠等硬约束的情况下，仅考虑时间先后，将所有航班 都 分配给机长 先把航班覆盖率拉到100%，然后再进行破坏，按照 硬约束规则 进行破坏，使得最终解是合规的

“立破立”的策略，能够在保障覆盖率的情况下进行优化
```

## Appendix

| <img src="/assets/posts/crew-scheduling-cts2025/attachments/43c49ed5343dd06098bc8b78ea5b07d.jpg" alt="43c49ed5343dd06098bc8b78ea5b07d" width="350" loading="lazy" /> | <img src="/assets/posts/crew-scheduling-cts2025/attachments/1af085e1cc3f20a3b91b42c7b84df82.jpg" alt="1af085e1cc3f20a3b91b42c7b84df82" width="350" loading="lazy" /> |
| --------------------------------------------------------- | --------------------------------------------------------- |
| <img src="/assets/posts/crew-scheduling-cts2025/attachments/c3bcbe07437db0d550dab8866834e27.jpg" alt="c3bcbe07437db0d550dab8866834e27" width="350" loading="lazy" /> | <img src="/assets/posts/crew-scheduling-cts2025/attachments/8b06c6c15bf34a7ff88649e61251209.jpg" alt="8b06c6c15bf34a7ff88649e61251209" width="350" loading="lazy" /> |
| <img src="/assets/posts/crew-scheduling-cts2025/attachments/Pasted%20image%2020250717204516.png" alt="Pasted image 20250717204516" width="350" loading="lazy" />     | <img src="/assets/posts/crew-scheduling-cts2025/attachments/ecfccfd39c062f200c26db55b8bbe23.jpg" alt="ecfccfd39c062f200c26db55b8bbe23" width="350" loading="lazy" /> |
