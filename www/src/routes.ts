import {RouteConfig} from "vue-router";
import * as pages from "@/pages";


enum EmissionsLocations {
  Auckland = "EMISSIONS_AUCKLAND",
  Christchurch = "EMISSIONS_CHRISTCHURCH",
  Oamaru = "EMISSIONS_OAMARU",
  Wellington = "EMISSIONS_WELLINGTON"
}

enum ModeShareLocations {
  Christchurch = "MODE_SHARE_CHRISTCHURCH",
}

enum RootLocations {
  About = "ROOT_ABOUT",
  Root = "ROOT_ROOT",
}

const RouterLocations = {
  Emissions: EmissionsLocations,
  ModeShare: ModeShareLocations,
  Root: RootLocations,
}

/**
 * Sets router url endpoints to specific pages
 */
const routes: RouteConfig[] = [
  {
    path: "/emissions",
    component: pages.emissions.EmissionsBase,
    children: [
      {
        path: "auckland",
        name: RouterLocations.Emissions.Auckland,
        component: pages.emissions.Auckland
      },
      {
        path: "christchurch",
        name: RouterLocations.Emissions.Christchurch,
        component: pages.emissions.Christchurch
      },
      {
        path: "oamaru",
        name: RouterLocations.Emissions.Oamaru,
        component: pages.emissions.Oamaru
      },
      {
        path: "wellington",
        name: RouterLocations.Emissions.Wellington,
        component: pages.emissions.Wellington
      },
      {
        path: "*",
        redirect: {name: RouterLocations.Emissions.Christchurch}
      }
    ]
  },
  {
    path: "/mode-share",
    component: pages.modeShare.ModeShareBase,
    children: [
      {
        path: "christchurch",
        name: RouterLocations.ModeShare.Christchurch,
        component: pages.modeShare.Christchurch
      },
      {
        path: "*",
        redirect: {name: RouterLocations.ModeShare.Christchurch}
      }
    ]
  },
  {
    path: "/about",
    name: RouterLocations.Root.About,
    component: pages.AboutPage
  },
  {
    path: '*',
    name: RouterLocations.Root.Root,
    redirect: {name: RouterLocations.Emissions.Christchurch}
  }
];
export default routes;
export {RouterLocations}
