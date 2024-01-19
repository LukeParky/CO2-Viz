import {RouteConfig} from "vue-router";
import MapPage from "@/pages/MapPage.vue";

/**
 * Sets router url endpoints to specific pages
 */
const routes: RouteConfig[] = [
  {
    path: "/",
    name: "Map",
    component: MapPage
  },
  {
    path: '*',
    redirect: '/'
  }
];
export default routes;
