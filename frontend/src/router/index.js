import { createRouter, createWebHistory } from "vue-router";
import HomeView from "@/views/HomeView.vue";
import HomeView2 from "@/views/HomeView2.vue";
import StockApp from "@/views/StockApp.vue";
import MovingAvgChart from "@/components/stock/MovingAvgChart.vue";
import StockHeatMap from "@/components/stock/StockHeatmap.vue";
import LoginView from "@/views/LoginView.vue";
import StockAnalysis from "@/components/stock/StockAnalysis.vue";
import TwStockCategories from "@/components/stock/TwStockCategories.vue";

const routes = [
  {
    path: "/login",
    name: "Login",
    component: LoginView,
    meta: {
      hideHeader: true,
    },
  },
  {
    path: "/home",
    name: "Home",
    component: HomeView,
  },
  {
    path: "/stock-app",
    name: "StockApp",
    component: StockApp,
    children: [
      {
        path: ":symbol?",
        name: "StockAnalysis",
        component: StockAnalysis,
        props: (route) => ({
          symbol: route.params.symbol,
          market: route.params.market,
          keepData: route.query.keepData === "true",
        }),
      },
    ],
  },
  {
    path: "/moving-avg/:symbol/:market?",
    name: "MovingAvgChart",
    component: MovingAvgChart,
    props: (route) => {
      const market =
        route.query.market || localStorage.getItem("selectedMarket") || "US";

      return {
        symbol: route.params.symbol,
        market: market,
      };
    },
  },
  {
    path: "/stock-heatmap",
    name: "StockHeatMap",
    component: StockHeatMap,
  },
  {
    path: "/home2",
    name: "Home2",
    component: HomeView2,
  },
  {
    path: "/tw-stock-categories",
    name: "TwStockCategories",
    component: TwStockCategories,
  },
  // 重定向
  {
    path: "/",
    redirect: "/login",
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
