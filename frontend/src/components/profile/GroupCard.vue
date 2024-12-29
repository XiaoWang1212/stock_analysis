<template>
  <div
    class="group-card"
    :class="{ expanded: isExpanded, collapsing: isCollapsing }"
    @click="handleCardClick"
  >
    <div class="expand-handle">
      <span class="material-icons">
        {{ isExpanded ? "expand_less" : "expand_more" }}
      </span>
    </div>

    <div class="group-content">
      <group-header
        :name="group.name"
        :index="index"
        @update-name="$emit('update-name', $event)"
        @add-stock="$emit('add-stock')"
      />

      <stock-list
        :stocks="group.stocks"
        :chart-data="chartData"
        :is-expanded="isExpanded"
        @navigate="$emit('navigate', $event)"
        @remove-stock="$emit('remove-stock', $event)"
      />
    </div>
  </div>
</template>

<script>
  import GroupHeader from "./GroupHeader.vue";
  import StockList from "./StockList.vue";

  export default {
    name: "GroupCard",
    components: {
      GroupHeader,
      StockList,
    },
    data() {
      return {
        isCollapsing: false,
      };
    },
    props: {
      group: {
        type: Object,
        required: true,
      },
      index: {
        type: Number,
        required: true,
      },
      isExpanded: {
        type: Boolean,
        default: false,
      },
      chartData: {
        type: Object,
        default: () => ({}),
      },
    },
    emits: ["toggle", "update-name", "add-stock", "remove-stock", "navigate"],
    methods: {
      handleCardClick(event) {
        if (this.isExpanded) {
          this.isCollapsing = true;
          setTimeout(() => {
            this.isCollapsing = false;
            this.$emit("toggle");
          }, 300);
        } else {
          const card = event.currentTarget;
          const rect = card.getBoundingClientRect();
          card.style.setProperty("--original-width", `${rect.width}px`);
          card.style.setProperty("--original-height", `${rect.height}px`);
          card.style.setProperty("--original-top", `${rect.top}px`);
          card.style.setProperty("--original-left", `${rect.left}px`);
          this.$emit("toggle");
        }
      },
    },
  };
</script>

<style scoped>
  .group-card {
    background: white;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #e9ecef;
    min-height: 200px;
    cursor: pointer;
    width: auto;
    box-sizing: border-box;
    position: relative;
    z-index: 1;
    transform-origin: top left;
    transition: all 0.3s ease-out;
  }

  .group-card:not(.expanded):hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .group-card.expanded {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 90vw;
    height: 90vh;
    background: white;
    z-index: 999;
    overflow-y: auto;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    isolation: isolate;
    animation: expandFromOrigin 0.3s ease-out forwards;
  }

  .group-card.collapsing {
    animation: collapseToOrigin 0.3s ease-out forwards;
  }

  .group-content {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .expand-handle {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.05);
    transition: background 0.2s;
    z-index: 2;
  }

  .expand-handle:hover {
    background: rgba(0, 0, 0, 0.1);
  }

  .expanded .group-content {
    height: calc(100% - 60px);
    overflow-y: auto;
  }

  @keyframes expandFromOrigin {
    0% {
      transform: translate(0, 0) scale(1);
      width: var(--original-width);
      height: var(--original-height);
      top: var(--original-top);
      left: var(--original-left);
    }
    100% {
      transform: translate(-50%, -50%) scale(1);
      width: 90vw;
      height: 90vh;
      top: 50%;
      left: 50%;
    }
  }

  @keyframes collapseToOrigin {
    0% {
      transform: translate(-50%, -50%) scale(1);
      width: 90vw;
      height: 90vh;
      top: 50%;
      left: 50%;
    }
    100% {
      transform: translate(0, 0) scale(1);
      width: var(--original-width);
      height: var(--original-height);
      top: var(--original-top);
      left: var(--original-left);
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

  @media (max-width: 768px) {
    .group-card {
      min-height: 180px;
    }

    .group-card.expanded {
      width: 95vw;
      height: 95vh;
      padding: 20px;
    }
  }

  /* 確保元素在展開時的層級關係正確 */
  .group-card {
    position: relative;
    isolation: isolate;
  }

  .group-content {
    position: relative;
    z-index: 1;
  }

  .expanded .group-content {
    z-index: 1000;
  }
</style>
