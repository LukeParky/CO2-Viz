import {RouteConfig} from "vue-router";
import * as pages from "@/pages";


enum EmissionsLocations {
  Auckland = "EMISSIONS_AUCKLAND",
  Hamilton = "EMISSIONS_HAMILTON",
  Christchurch = "EMISSIONS_CHRISTCHURCH",
  Oamaru = "EMISSIONS_OAMARU",
  Queenstown = "EMISSIONS_QUEENSTOWN",
  Wellington = "EMISSIONS_WELLINGTON"
}

enum ModeShareFlowLocations {
  Auckland = "MODE_SHARE_FLOW_AUCKLAND",
  Hamilton = "MODE_SHARE_FLOW_HAMILTON",
  Christchurch = "MODE_SHARE_FLOW_CHRISTCHURCH",
  Oamaru = "MODE_SHARE_FLOW_OAMARU",
  Queenstown = "MODE_SHARE_FLOW_QUEENSTOWN",
  Wellington = "MODE_SHARE_FLOW_WELLINGTON"
}

enum ModeShare2023Locations {
  Auckland = "MODE_SHARE_2023_AUCKLAND",
  Hamilton = "MODE_SHARE_2023_HAMILTON",
  Christchurch = "MODE_SHARE_2023_CHRISTCHURCH",
  Oamaru = "MODE_SHARE_2023_OAMARU",
  Queenstown = "MODE_SHARE_2023_QUEENSTOWN",
  Wellington = "MODE_SHARE_2023_WELLINGTON"
}

enum RootLocations {
  About = "ROOT_ABOUT",
  Root = "ROOT_ROOT",
}

const RouterLocations = {
  Emissions: EmissionsLocations,
  ModeShareFlow: ModeShareFlowLocations,
  ModeShare2023: ModeShare2023Locations,
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
        path: "*",
        redirect: {name: RouterLocations.Emissions.Christchurch}
      }
    ]
  },
  {
    path: "/mode-share-flow",
    component: pages.modeShareFlow.ModeShareBase,
    children: [
      {
        path: "auckland",
        name: RouterLocations.ModeShareFlow.Auckland,
        component: pages.modeShareFlow.Auckland
      },
      {
        path: "hamilton",
        name: RouterLocations.ModeShareFlow.Hamilton,
        component: pages.modeShareFlow.Hamilton
      },
      {
        path: "christchurch",
        name: RouterLocations.ModeShareFlow.Christchurch,
        component: pages.modeShareFlow.Christchurch
      },
      {
        path: "wellington",
        name: RouterLocations.ModeShareFlow.Wellington,
        component: pages.modeShareFlow.Wellington
      },
      {
        path: "oamaru",
        name: RouterLocations.ModeShareFlow.Oamaru,
        component: pages.modeShareFlow.Oamaru
      },
      {
        path: "queenstown",
        name: RouterLocations.ModeShareFlow.Queenstown,
        component: pages.modeShareFlow.Queenstown
      },
      {
        path: "*",
        redirect: {name: RouterLocations.ModeShareFlow.Christchurch}
      }
    ]
  },
  {
    path: "/mode-share-2023",
    component: pages.modeShare2023.ModeShareBase,
    children: [
      {
        path: "auckland",
        name: RouterLocations.ModeShare2023.Auckland,
        component: pages.modeShare2023.Auckland
      },
      {
        path: "hamilton",
        name: RouterLocations.ModeShare2023.Hamilton,
        component: pages.modeShare2023.Hamilton
      },
      {
        path: "christchurch",
        name: RouterLocations.ModeShare2023.Christchurch,
        component: pages.modeShare2023.Christchurch
      },
      {
        path: "wellington",
        name: RouterLocations.ModeShare2023.Wellington,
        component: pages.modeShare2023.Wellington
      },
      {
        path: "oamaru",
        name: RouterLocations.ModeShare2023.Oamaru,
        component: pages.modeShare2023.Oamaru
      },
      {
        path: "queenstown",
        name: RouterLocations.ModeShare2023.Queenstown,
        component: pages.modeShare2023.Queenstown
      },
      {
        path: "*",
        redirect: {name: RouterLocations.ModeShare2023.Christchurch}
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
    redirect: {name: RouterLocations.Root.About}
  }
];
export default routes;
export {RouterLocations}
