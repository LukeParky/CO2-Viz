import {RouteConfig} from "vue-router";
import * as pages from "@/pages";


enum routerLocations {
  AboutPage = "ABOUT_PAGE",
  AucklandCo2Sa1Page = "AUCKLAND_CO2_SA1_PAGE",
  ChristchurchCo2Sa1Page = "CHRISTCHURCH_CO2_SA1_PAGE",
  ChristchurchModeSharePage = "CHRISTCHURCH_MODE_SHARE_PAGE",
  OamaruCo2Sa1Page = "OAMARU_CO2_SA1_PAGE",
  RootPage = "ROOT_PAGE",
  WellingtonCo2Sa1Page = "WELLINGTON_CO2_SA1_PAGE"
}

/**
 * Sets router url endpoints to specific pages
 */
const routes: RouteConfig[] = [
  {
    path: "/mode-share/christchurch",
    name: routerLocations.ChristchurchModeSharePage,
    component: pages.modeShare.Christchurch
  },
  {
    path: "/auckland",
    name: routerLocations.AucklandCo2Sa1Page,
    component: pages.emissions.Auckland
  },
  {
    path: "/christchurch",
    name: routerLocations.ChristchurchCo2Sa1Page,
    component: pages.emissions.Christchurch
  },
  {
    path: "/oamaru",
    name: routerLocations.OamaruCo2Sa1Page,
    component: pages.emissions.Oamaru
  },
  {
    path: "/wellington",
    name: routerLocations.WellingtonCo2Sa1Page,
    component: pages.emissions.Wellington
  },
  {
    path: "/about",
    name: routerLocations.AboutPage,
    component: pages.AboutPage
  },
  {
    path: '*',
    name: routerLocations.RootPage,
    redirect: {name: routerLocations.ChristchurchCo2Sa1Page}
  }
];
export default routes;
export {routerLocations}
