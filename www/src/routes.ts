import type {RouteRecordRaw} from "vue-router";
import * as pages from "@/pages";


enum EmissionsLocations {
  Auckland = "EMISSIONS_AUCKLAND",
  Hamilton = "EMISSIONS_HAMILTON",
  Christchurch = "EMISSIONS_CHRISTCHURCH",
  Oamaru = "EMISSIONS_OAMARU",
  Queenstown = "EMISSIONS_QUEENSTOWN",
  Wellington = "EMISSIONS_WELLINGTON"
}

enum ModeShareLocations {
  Auckland = "MODE_SHARE_AUCKLAND",
  Hamilton = "MODE_SHARE_HAMILTON",
  Christchurch = "MODE_SHARE_CHRISTCHURCH",
  Oamaru = "MODE_SHARE_OAMARU",
  Queenstown = "MODE_SHARE_QUEENSTOWN",
  Wellington = "MODE_SHARE_WELLINGTON"
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
const routes: RouteRecordRaw[] = [
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
        path: "hamilton",
        name: RouterLocations.Emissions.Hamilton,
        component: pages.emissions.Hamilton
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
        path: "queenstown",
        name: RouterLocations.Emissions.Queenstown,
        component: pages.emissions.Queenstown
      },
      {
        path: "wellington",
        name: RouterLocations.Emissions.Wellington,
        component: pages.emissions.Wellington
      },
      {
        path: "/:pathMatch(.*)*",
        redirect: {name: RouterLocations.Emissions.Christchurch}
      }
    ]
  },
  {
    path: "/mode-share",
    component: pages.modeShare.ModeShareBase,
    children: [
      {
        path: "auckland",
        name: RouterLocations.ModeShare.Auckland,
        component: pages.modeShare.Auckland
      },
      {
        path: "hamilton",
        name: RouterLocations.ModeShare.Hamilton,
        component: pages.modeShare.Hamilton
      },
      {
        path: "christchurch",
        name: RouterLocations.ModeShare.Christchurch,
        component: pages.modeShare.Christchurch
      },
      {
        path: "wellington",
        name: RouterLocations.ModeShare.Wellington,
        component: pages.modeShare.Wellington
      },
      {
        path: "oamaru",
        name: RouterLocations.ModeShare.Oamaru,
        component: pages.modeShare.Oamaru
      },
      {
        path: "queenstown",
        name: RouterLocations.ModeShare.Queenstown,
        component: pages.modeShare.Queenstown
      },
      {
        path: "/:pathMatch(.*)*",
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
    path: "/:pathMatch(.*)*",
    name: RouterLocations.Root.Root,
    redirect: {name: RouterLocations.Root.About}
  }
];
export default routes;
export {RouterLocations}
