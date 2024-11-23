<template>
  <div class="death-rate-view">
    <h1>死亡率分析</h1>
    <death-rate-chart />
    <death-rate-analysis />
  </div>
</template>

<script>
  import DeathRateChart from "@/components/death/DeathRateChart.vue";
  import DeathRateAnalysis from "@/components/death/DeathRateAnalysis.vue";

  export default {
    name: "DeathRateView",
    components: {
      DeathRateChart,
      DeathRateAnalysis,
    },
  };
</script>

<style scoped>
  .death-rate-view {
    padding: 20px;
  }

  h1 {
    margin-bottom: 20px;
    color: #333;
  }
</style>
