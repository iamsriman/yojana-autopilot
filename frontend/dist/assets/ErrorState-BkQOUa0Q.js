import{c as r,j as e}from"./index-BRT2DfPZ.js";import{B as a}from"./Button-BARSYDpS.js";import{C as i}from"./Card-BAAnb7H8.js";/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const l=r("CircleAlert",[["circle",{cx:"12",cy:"12",r:"10",key:"1mglay"}],["line",{x1:"12",x2:"12",y1:"8",y2:"12",key:"1pkeuh"}],["line",{x1:"12",x2:"12.01",y1:"16",y2:"16",key:"4dfq90"}]]);/**
 * @license lucide-react v0.468.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const c=r("RefreshCw",[["path",{d:"M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8",key:"v9h5vc"}],["path",{d:"M21 3v5h-5",key:"1q7to0"}],["path",{d:"M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16",key:"3uifl3"}],["path",{d:"M8 16H3v5",key:"1cv678"}]]);function x({message:t,onRetry:s}){return e.jsx(i,{className:"border-red-100 bg-red-50",children:e.jsxs("div",{className:"flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between",children:[e.jsxs("div",{className:"flex gap-3",children:[e.jsx(l,{className:"mt-0.5 h-5 w-5 shrink-0 text-danger","aria-hidden":"true"}),e.jsxs("div",{children:[e.jsx("h2",{className:"font-semibold text-red-900",children:"Unable to load this information"}),e.jsx("p",{className:"mt-1 text-sm leading-6 text-red-800",children:t})]})]}),s?e.jsx(a,{variant:"danger",icon:e.jsx(c,{className:"h-4 w-4"}),onClick:s,children:"Retry"}):null]})})}export{x as E};
