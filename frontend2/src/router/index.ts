import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";

// Remove 'static/' (or 'static') from the base URL so that we get 'example.com/' instead of 'example.com/static/' as base
const defaultBaseUrl = import.meta.env.BASE_URL;
const baseUrl = defaultBaseUrl.substring(0, defaultBaseUrl.lastIndexOf('static'));

const router = createRouter({
  history: createWebHistory(baseUrl),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/about/",
      name: "about",
      // route level code-splitting
      // this generates a separate chunk (About.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
      component: () => import("../views/AboutView.vue"),
    },
  ],
});

export default router;
