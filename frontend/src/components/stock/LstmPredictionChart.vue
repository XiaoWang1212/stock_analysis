<template>
  <div class="lstm-prediction">
    <h3>{{ symbol }}</h3>
    <div v-if="loading" class="loading">載入中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="!prediction" class="no-data">無預測數據可用</div>
    <div v-else>
      <div class="prediction-summary">
        <div class="price-info">
          <div>當前價格: ${{ prediction.current_price.toFixed(2) }}</div>
          <div>
            預測下一交易日:
            <span :class="prediction.price_change_percent > 0 ? 'up' : 'down'">
              ${{ prediction.predicted_next_price.toFixed(2) }} ({{
                prediction.price_change_percent > 0 ? "+" : ""
              }}{{ prediction.price_change_percent.toFixed(2) }}%)
            </span>
          </div>
        </div>
        <div
          class="signal"
          :class="prediction.signal === '買入' ? 'buy' : 'sell'"
        >
          {{ prediction.signal }}
        </div>
      </div>

      <div class="chart-container" ref="chartContainer"></div>

      <div class="future-predictions">
        <h4>未來 7 天預測</h4>
        <table>
          <thead>
            <tr>
              <th>日期</th>
              <th>預測價格</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(pred, index) in prediction.future_predictions"
              :key="index"
            >
              <td>{{ pred.date }}</td>
              <td
                :class="
                  index === 0
                    ? 'current'
                    : pred.price >
                      prediction.future_predictions[index - 1].price
                    ? 'up'
                    : 'down'
                "
              >
                ${{ pred.price.toFixed(2) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="model-info">
        <div>預測準確度: {{ prediction.prediction_accuracy.toFixed(2) }}%</div>
        <div>RMSE: {{ prediction.rmse.toFixed(4) }}</div>
      </div>
    </div>

    <sentiment-analysis-chart
      v-if="prediction && prediction.sentiment_data"
      :sentiment="getSentimentObject()"
      :top5News="getTop5News()"
      :symbol="symbol"
    />
  </div>
</template>

<script>
  import Plotly from "plotly.js-dist";
  import { mapActions, mapState } from "vuex";
  import { nextTick } from "vue";
  import SentimentAnalysisChart from "./SentimentAnalysisChart.vue";

  export default {
    components: {
      SentimentAnalysisChart,
    },

    props: {
      symbol: {
        type: String,
        required: true,
      },
      market: {
        type: String,
        default: "US",
      },
    },

    computed: {
      ...mapState("stockApp", ["loading", "error", "lstmPrediction"]),

      prediction() {
        return this.lstmPrediction;
      },


    },

    watch: {
      symbol(newSymbol, oldSymbol) {
        if (newSymbol !== oldSymbol) {
          this.loadPrediction();
        }
      },

      lstmPrediction(newData) {
        if (newData) {
          this.$nextTick(() => {
            this.renderChart();
          });
        }
      },
    },

    mounted() {
      this.loadPrediction();
    },

    beforeUnmount() {
      this.cleanupChart();
      this.resetLstmPrediction();
    },

    methods: {
      ...mapActions("stockApp", ["fetchLstmPrediction", "resetLstmPrediction"]),

      async loadPrediction() {
        if (!this.symbol) return;

        this.cleanupChart();
        await this.fetchLstmPrediction(this.symbol);
      },

      getSentimentObject() {
        if (!this.prediction || !this.prediction.sentiment_data) return null;

        return {
          score: this.prediction.sentiment_score,
          impact: this.prediction.sentiment_impact,
          data: this.prediction.sentiment_data,
          historicalDates: this.prediction.historical_data.dates,
          futureDates: this.prediction.future_predictions.map((p) => p.date),
        };
      },

      getTop5News() {
        if (!this.prediction || !this.prediction.sentiment_data) return [];

        return this.prediction.top_5_news;
      },

      cleanupChart() {
        if (this.$refs.chartContainer) {
          try {
            Plotly.purge(this.$refs.chartContainer);
          } catch (e) {
            console.warn("Failed to purge chart:", e);
          }
        }

        if (this.$refs.sentimentChartContainer) {
          try {
            Plotly.purge(this.$refs.sentimentChartContainer);
          } catch (e) {
            console.warn("Failed to purge sentiment chart:", e);
          }
        }
      },

      async renderChart() {
        try {
          if (!this.prediction) return;

          await nextTick();

          let historicalDates = [];
          let historicalPrices = [];

          if (this.prediction.historical_data) {
            historicalDates = this.prediction.historical_data.dates;
            historicalPrices = this.prediction.historical_data.prices;
          }

          const futureDates = this.prediction.future_predictions.map(
            (d) => d.date
          );
          const futurePrices = this.prediction.future_predictions.map(
            (d) => d.price
          );

          const traceHistorical = {
            x: historicalDates,
            y: historicalPrices,
            type: "scatter",
            mode: "lines",
            name: "歷史價格",
            line: {
              color: "#2894FF",
              width: 1.5,
            },
          };

          const traceFuture = {
            x: futureDates,
            y: futurePrices,
            type: "scatter",
            mode: "lines+markers",
            name: "預測價格",
            line: {
              color: "#FFA042",
              width: 2.5,
              dash: "dash",
            },
            marker: {
              size: 8,
              color: "#FFA042",
              symbol: "circle",
            },
          };

          const traceCurrent = {
            x: [
              historicalDates.length > 0
                ? historicalDates[historicalDates.length - 1]
                : futureDates[0],
            ],
            y: [this.prediction.current_price],
            type: "scatter",
            mode: "markers",
            name: "當前價格",
            marker: {
              size: 12,
              color: "#02DF82",
              symbol: "diamond",
            },
          };

          const traces = [];
          if (historicalDates.length > 0) {
            traces.push(traceHistorical);
          }
          traces.push(traceCurrent);
          traces.push(traceFuture);

          const allPrices = [
            ...historicalPrices,
            ...futurePrices,
            this.prediction.current_price,
          ];
          const validPrices = allPrices.filter((p) => p !== null && !isNaN(p));
          const minPrice = Math.min(...validPrices) * 0.95;
          const maxPrice = Math.max(...validPrices) * 1.05;

          const layout = {
            title: `${this.symbol} 股價預測分析`,
            titlefont: {
              size: 22,
              color: "white",
            },
            xaxis: {
              title: "日期",
              showgrid: true,
              color: '#BEBEBE',
              gridcolor: "#7B7B7B",
              zeroline: true,
              zerolinecolor: "rgba(0, 0, 0, 0.1)",
            },
            yaxis: {
              title: "價格 ($)",
              showgrid: true,
              color: '#BEBEBE',
              gridcolor: "#7B7B7B",
              zeroline: true,
              zerolinecolor: "rgba(0, 0, 0, 0.1)",
              range: [minPrice, maxPrice],
            },
            margin: { t: 70, b: 70, l: 70, r: 40 },
            legend: {
              orientation: "h",
              y: -0.2,
              //bgcolor: "rgba(255, 255, 255, 0.9)",
              //bordercolor: "rgba(0, 0, 0, 0.1)",
              //borderwidth: 1,
              font: {
                color: "#BEBEBE"
              },
            },
            showlegend: true,
            hovermode: "closest",
            hoverlabel: {
              bgcolor: "#FFF",
              bordercolor: "#999",
              font: { size: 12, family: "Arial" },
            },
            paper_bgcolor: '#4F4F4F',
            plot_bgcolor: '#4F4F4F',
            shapes: [
              // 添加當前日期的垂直線
              {
                type: "line",
                x0:
                  historicalDates.length > 0
                    ? historicalDates[historicalDates.length - 1]
                    : futureDates[0],
                y0: minPrice,
                x1:
                  historicalDates.length > 0
                    ? historicalDates[historicalDates.length - 1]
                    : futureDates[0],
                y1: maxPrice,
                line: {
                  color: "white",
                  width: 1,
                  dash: "dot",
                },
              },
            ],
            annotations: [
              // 添加當前價格標註
              {
                x:
                  historicalDates.length > 0
                    ? historicalDates[historicalDates.length - 1]
                    : futureDates[0],
                y: this.prediction.current_price,
                xref: "x",
                yref: "y",
                text: `$${this.prediction.current_price.toFixed(2)}`,
                showarrow: true,
                arrowhead: 2,
                arrowsize: 1,
                arrowwidth: 2,
                arrowcolor: "#00DB00",
                ax: 20,
                ay: -40,
                bordercolor: "#c7c7c7",
                borderwidth: 1,
                borderpad: 4,
                bgcolor: "#F0F0F0",
                opacity: 0.8,
              },
              // 添加未來預測標註
              {
                x: futureDates[futureDates.length - 1],
                y: futurePrices[futurePrices.length - 1],
                xref: "x",
                yref: "y",
                text: `預測: $${futurePrices[futurePrices.length - 1].toFixed(
                  2
                )}`,
                showarrow: true,
                arrowhead: 2,
                arrowsize: 1,
                arrowwidth: 2,
                arrowcolor: "#FF8000",
                ax: 20,
                ay: -40,
                bordercolor: "#ff5722",
                borderwidth: 1,
                borderpad: 4,
                bgcolor: "#F0F0F0",
                opacity: 0.8,
              },
            ],
          };

          // 設置圖表配置
          const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: [
              "select2d",
              "lasso2d",
              "hoverClosestCartesian",
              "hoverCompareCartesian",
            ],
            displaylogo: false,
            toImageButtonOptions: {
              format: "png",
              filename: `${this.symbol}_prediction`,
              height: 500,
              width: 700,
              scale: 2,
            },
          };

          // 渲染圖表
          Plotly.newPlot(this.$refs.chartContainer, traces, layout, config);

          // 添加圖表事件監聽器
          // this.$refs.chartContainer.on('plotly_hover', (data) => {
          //   const pointData = data.points[0];
          //   const curveNumber = pointData.curveNumber;

          //   if (curveNumber === 2) { // 預測曲線
          //     const index = pointData.pointIndex;
          //     const date = futureDates[index];
          //     const price = futurePrices[index];

          //     // 可以在這裡更新一些額外的資訊顯示
          //     console.log(`Hover on prediction: ${date}, $${price.toFixed(2)}`);
          //   }
          // });
        } catch (error) {
          console.error("Error rendering chart:", error);
        }
      },
    },
  };
</script>

<style scoped>
  .lstm-prediction {
    padding: 20px;
    border: 2px solid #7B7B7B;
    border-radius: 8px;
    background: #4F4F4F;
    margin-bottom: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  }

  .loading {
    text-align: center;
    padding: 50px;
    color: #6c757d;
    font-style: italic;
    background-color: rgba(248, 249, 250, 0.7);
    border-radius: 6px;
  }

  .no-data {
    text-align: center;
    padding: 30px;
    color: #6c757d;
    background-color: #f8f9fa;
    border-radius: 6px;
    font-weight: 500;
  }

  .error {
    color: #dc3545;
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    padding: 12px 15px;
    border-radius: 4px;
    margin: 15px 0;
  }

  .prediction-summary {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    padding: 15px;
    background-color: #4F4F4F;
    border-radius: 6px;
    border: 1px solid #7B7B7B;
    border-left: 4px solid #66B3FF;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  }

  .price-info {
    text-align: start;
    font-size: 18px;
    line-height: 1.5;
  }

  .signal {
    padding: 12px 24px;
    border-radius: 30px;
    font-weight: bold;
    color: white;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-size: 16px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
  }

  .buy {
    background-color: #28a745;
  }

  .sell {
    background-color: #dc3545;
  }

  .up {
    color: #28a745;
    font-weight: bold;
  }

  .down {
    color: #dc3545;
    font-weight: bold;
  }

  .chart-container {
    height: 450px;
    margin: 25px 0;
    border: 1px solid #7B7B7B;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 5px rgba(0, 0, 0, 0.03);
  }

  .future-predictions {
    margin-top: 25px;
    background-color: #4F4F4F;
    border: 1px solid #7B7B7B;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  }

  .future-predictions h4 {
    margin-top: 0;
    color: white;
    margin-bottom: 15px;
    font-size: 18px;
    border-bottom: 1px solid #dee2e6;
    padding-bottom: 10px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    border: 1px solid #dee2e6;
  }

  th {
    font-weight: 600;
    padding: 12px;
    text-align: center;
    border-bottom: 2px solid #dee2e6;
    color: white;
  }

  td {
    padding: 12px;
    border-bottom: 1px solid #dee2e6;
  }

  .model-info {
    margin-top: 25px;
    color: white;
    font-size: 14px;
    display: flex;
    justify-content: space-between;
    padding: 15px;
    background-color: #4F4F4F;
    border: 1px solid #7B7B7B;
    border-radius: 6px;
  }

  .current {
    font-weight: bold;
    border: 4px solid #FFA042;
    color: white;
  }

  h3 {
    margin-top: 0;
    color: white;
    padding-bottom: 10px;
    border-bottom: 1px solid #dee2e6;
    margin-bottom: 20px;
    font-size: 22px;
    font-weight: 600;
    letter-spacing: 0.5px;
  }

  /* 響應式設計 */
  @media (max-width: 768px) {
    .prediction-summary {
      flex-direction: column;
      text-align: center;
    }

    .signal {
      margin-top: 15px;
    }

    .chart-container {
      height: 300px;
    }

    .model-info {
      flex-direction: column;
      gap: 8px;
    }
  }
</style>
