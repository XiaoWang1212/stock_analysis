<template>
  <div class="groups-section">
    <div class="groups-header">
      <h3>股票群組管理</h3>
      <p class="groups-description">您可以創建最多6個群組來管理您的股票</p>
    </div>

    <div class="groups-container">
      <!-- 遮罩層 -->
      <div
        v-if="selectedGroup !== null"
        class="overlay"
        @click="handleOverlayClick"
      ></div>

      <div class="groups-grid">
        <group-card
          v-for="(group, index) in groups"
          :key="index"
          :ref="
            (el) => {
              if (el) cardRefs[index] = el;
            }
          "
          :group="group"
          :index="index"
          :is-expanded="selectedGroup === index"
          :chart-data="chartData"
          @toggle="$emit('toggle-group', index)"
          @update-name="$emit('update-group-name', index, $event)"
          @add-stock="$emit('add-stock', index)"
          @remove-stock="$emit('remove-stock', index, $event)"
          @navigate="$emit('navigate', $event)"
        />
      </div>
    </div>
  </div>
</template>

<script>
  import GroupCard from "./GroupCard.vue";

  export default {
    name: "GroupsList",
    components: {
      GroupCard,
    },
    props: {
      groups: {
        type: Array,
        default: () => [],
      },
      selectedGroup: {
        type: Number,
        default: null,
      },
      chartData: {
        type: Object,
        default: () => ({}),
      },
    },
    data() {
      return {
        cardRefs: [],
      };
    },
    emits: [
      "toggle-group",
      "update-group-name",
      "add-stock",
      "remove-stock",
      "navigate",
    ],
    methods: {
      handleOverlayClick() {
        if (this.selectedGroup !== null && this.cardRefs[this.selectedGroup]) {
          this.cardRefs[this.selectedGroup].handleCardClick();
        }
      },
    },
  };
</script>

<style scoped>
  .groups-section {
    margin: 30px 0;
  }

  .groups-header {
    margin-bottom: 30px;
    text-align: center;
  }

  .groups-header h3 {
    font-size: 1.5em;
    margin-bottom: 10px;
    color: #2c3e50;
  }

  .groups-description {
    color: #666;
    font-size: 1em;
  }

  .groups-container {
    position: relative;
  }

  .overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.5);
    z-index: 998;
    animation: fadeIn 0.3s ease;
  }

  .groups-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 25px;
    position: relative;
  }

  @media (max-width: 768px) {
    .groups-grid {
      grid-template-columns: 1fr;
    }
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
</style>
