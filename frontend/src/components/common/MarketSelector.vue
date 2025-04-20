<template>
  <div class="market-selector">
    <button
      class="market-btn"
      :class="{ active: selectedMarket === 'US' }"
      @click="selectMarket('US')"
    >
      美股
    </button>
    <button
      class="market-btn"
      :class="{ active: selectedMarket === 'TW' }"
      @click="selectMarket('TW')"
    >
      台股
    </button>
  </div>
</template>

<script>
  export default {
    name: "MarketSelector",
    props: {
      value: {
        type: String,
        default: "US",
      },
      modelValue: {
        type: String,
        default: "US",
      },
    },
    computed: {
      selectedMarket: {
        get() {
          return this.modelValue || this.value;
        },
        set(value) {
          this.$emit("update:modelValue", value);
          this.$emit("input", value);
        },
      },
    },
    methods: {
      selectMarket(market) {
        this.$emit("update:modelValue", market);
        this.$emit("input", market);
        this.$emit("market-change", market);

        console.log('Market selected:', market);
      },
    },
  };
</script>

<style scoped>
  .market-selector {
    display: flex;
    margin-bottom: 20px;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid #ddd;
    width: max-content;
  }

  .market-btn {
    padding: 10px 20px;
    border: none;
    background-color: #f5f5f5;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.3s ease;
  }

  .market-btn:first-child {
    border-right: 1px solid #ddd;
  }

  .market-btn.active {
    background-color: #4a6bff;
    color: white;
  }

  .market-btn:hover:not(.active) {
    background-color: #e0e0e0;
  }
</style>
