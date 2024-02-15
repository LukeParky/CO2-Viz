import {RouteConfig} from "vue-router";
import {AboutPage, AucklandCo2Sa1Page, ChristchurchCo2Sa1Page, OamaruCo2Sa1Page, WellingtonCo2Sa1Page} from "@/pages";


enum routerLocations {
  AboutPage = "ABOUT_PAGE",
  AucklandCo2Sa1Page = "AUCKLAND_CO2_SA1_PAGE",
  ChristchurchCo2Sa1Page = "CHRISTCHURCH_CO2_SA1_PAGE",
  OamaruCo2Sa1Page = "OAMARU_CO2_SA1_PAGE",
  RootPage = "ROOT_PAGE",
  WellingtonCo2Sa1Page = "WELLINGTON_CO2_SA1_PAGE"
}

/**
 * Sets router url endpoints to specific pages
 */
const routes: RouteConfig[] = [
  {
    path: "/auckland",
    name: routerLocations.AucklandCo2Sa1Page,
    component: AucklandCo2Sa1Page
  },
  {
    path: "/christchurch",
    name: routerLocations.ChristchurchCo2Sa1Page,
    component: ChristchurchCo2Sa1Page
  },
  {
    path: "/oamaru",
    name: routerLocations.OamaruCo2Sa1Page,
    component: OamaruCo2Sa1Page
  },
  {
    path: "/wellington",
    name: routerLocations.WellingtonCo2Sa1Page,
    component: WellingtonCo2Sa1Page
  },
  {
    path: "/about",
    name: routerLocations.AboutPage,
    component: AboutPage
  },
  {
    path: '*',
    name: routerLocations.RootPage,
    redirect: {name: routerLocations.ChristchurchCo2Sa1Page}
  }
];
export default routes;
export {routerLocations}
