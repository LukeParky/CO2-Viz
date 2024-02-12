import {RouteConfig} from "vue-router";
import AucklandCo2Sa1Page from "@/pages/AucklandCo2Sa1Page.vue";
import ChristchurchCo2Sa1Page from "@/pages/ChristchurchCo2Sa1Page.vue"
import OamaruCo2Sa1Page from "@/pages/OamaruCo2Sa1Page.vue"
import WellingtonCo2Sa1Page from "@/pages/WellingtonCo2Sa1Page.vue";

/**
 * Sets router url endpoints to specific pages
 */
const routes: RouteConfig[] = [
  {
    path: "/auckland",
    name: "Auckland",
    component: AucklandCo2Sa1Page
  },
  {
    path: "/christchurch",
    name: "Christchurch",
    component: ChristchurchCo2Sa1Page
  },
  {
    path: "/oamaru",
    name: "Oamaru",
    component: OamaruCo2Sa1Page
  },
  {
    path: "/wellington",
    name: "Wellington",
    component: WellingtonCo2Sa1Page
  },
  {
    path: '*',
    redirect: '/christchurch'
  }
];
export default routes;
