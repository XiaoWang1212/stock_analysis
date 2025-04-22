<template>
  <div class="sentiment-analysis" v-if="sentiment">
    <h4>市場情感分析</h4>

    <div class="sentiment-summary">
      <div class="sentiment-score">
        <div class="sentiment-label">當前市場情感:</div>
        <div
          class="sentiment-value"
          :class="getSentimentClass(sentiment.score)"
        >
          {{ getSentimentText(sentiment.score) }}
          ({{ sentiment.score.toFixed(2) }})
        </div>
      </div>

      <div class="sentiment-impact">
        <div class="sentiment-label">對預測影響:</div>
        <div class="impact-badge" :class="getImpactClass(sentiment.impact)">
          {{ sentiment.impact }}
        </div>
      </div>
    </div>

    <div class="chart-container" ref="sentimentChartContainer"></div>

    <div class="top-news-section" v-if="top5News && top5News.length">
      <h4>影響最大的關鍵新聞</h4>
      <div class="news-list">
        <div
          v-for="(news, index) in top5News"
          :key="index"
          class="news-item"
          :class="getNewsImpactClass(news.impact)"
        >
          <div class="news-header">
            <div
              class="impact-indicator"
              :class="
                news.impact_direction === '正面' ? 'positive' : 'negative'
              "
            >
              {{ news.impact_direction }}
            </div>
            <div class="impact-score">
              影響力: {{ Math.abs(news.impact).toFixed(2) }}
            </div>
          </div>
          <div class="news-title">
            <a :href="news.link" target="_blank" rel="noopener noreferrer">
              {{ news.title }}
              <i class="external-link-icon">↗</i>
            </a>
          </div>
        </div>
      </div>
    </div>

    <div class="sentiment-explanation">
      <h5>情感分析說明</h5>
      <p>
        市場情感分數範圍從 -1 (極度負面) 到 +1 (極度正面)，數值接近 0
        表示中性情感。
      </p>
      <p>
        當市場情感明顯偏向正面或負面時，可能對股價預測產生相應影響。此分析結合新聞、社交媒體等多方資料。
      </p>
    </div>
  </div>
</template>

<script>
  import Plotly from "plotly.js-dist";
  import { nextTick } from "vue";

  export default {
    name: "SentimentAnalysisChart",

    props: {
      sentiment: {
        type: Object,
        default: null,
      },
      symbol: {
        type: String,
        required: true,
      },
      top5News: {
        type: Array,
        default: () => [],
      },
    },

    watch: {
      sentiment: {
        handler(newVal) {
          if (newVal) {
            this.$nextTick(() => {
              this.renderSentimentChart();
            });
          }
        },
        deep: true,
      },
    },

    mounted() {
      if (this.sentiment) {
        this.renderSentimentChart();
      }
    },

    beforeUnmount() {
      this.cleanupChart();
    },

    methods: {
      cleanupChart() {
        if (this.$refs.sentimentChartContainer) {
          try {
            Plotly.purge(this.$refs.sentimentChartContainer);
          } catch (e) {
            console.warn("Failed to purge sentiment chart:", e);
          }
        }
      },

      getSentimentClass(score) {
        if (score > 0.2) return "very-positive";
        if (score > 0.05) return "positive";
        if (score < -0.2) return "very-negative";
        if (score < -0.05) return "negative";
        return "neutral";
      },

      getSentimentText(score) {
        if (score > 0.2) return "非常樂觀";
        if (score > 0.05) return "樂觀";
        if (score < -0.2) return "非常悲觀";
        if (score < -0.05) return "悲觀";
        return "中性";
      },

      getImpactClass(impact) {
        if (impact === "高") return "high-impact";
        if (impact === "中") return "medium-impact";
        return "low-impact";
      },

      getNewsImpactClass(impact) {
        const absImpact = Math.abs(impact);
        if (absImpact > 0.7) return "high-impact-news";
        if (absImpact > 0.3) return "medium-impact-news";
        return "low-impact-news";
      },

      async renderSentimentChart() {
        try {
          if (!this.sentiment || !this.sentiment.data) return;
          this.cleanupChart();
          await nextTick();

          const sentimentData = this.sentiment.data;
          const historicalDates = this.sentiment.historicalDates || [];
          const futureDates = this.sentiment.futureDates || [];

          // 歷史情感數據
          const traceHistorical = {
            x: historicalDates,
            y: sentimentData.recent,
            type: "scatter",
            mode: "lines",
            name: "歷史情感",
            line: {
              color: "rgba(75, 192, 192, 0.7)",
              width: 2,
            },
          };

          // 未來情感預測
          const traceFuture = {
            x: futureDates,
            y: sentimentData.future,
            type: "scatter",
            mode: "lines+markers",
            name: "預測情感",
            line: {
              color: "rgba(153, 102, 255, 0.7)",
              width: 2.5,
              dash: "dash",
            },
            marker: {
              size: 6,
              color: "rgba(153, 102, 255, 0.9)",
              symbol: "circle",
            },
          };

          // 零線 (中性情感基準)
          const traceZero = {
            x: [...historicalDates, ...futureDates],
            y: Array(historicalDates.length + futureDates.length).fill(0),
            type: "scatter",
            mode: "lines",
            name: "中性基準",
            line: {
              color: "rgba(128, 128, 128, 0.5)",
              width: 1,
              dash: "dot",
            },
            hoverinfo: "none",
          };

          const layout = {
            title: "市場情感走勢",
            titlefont: {
              size: 18,
              color: "#333",
            },
            xaxis: {
              title: "日期",
              showgrid: true,
              gridcolor: "rgba(233, 236, 239, 0.8)",
            },
            yaxis: {
              title: "情感分數",
              showgrid: true,
              gridcolor: "rgba(233, 236, 239, 0.8)",
              range: [-1, 1],
              tickvals: [-1, -0.5, 0, 0.5, 1],
              ticktext: ["極度負面", "負面", "中性", "正面", "極度正面"],
            },
            margin: { t: 60, b: 60, l: 70, r: 40 },
            legend: {
              orientation: "h",
              y: -0.2,
            },
            showlegend: true,
            hovermode: "closest",
            shapes: [
              // 當前日期的垂直線
              {
                type: "line",
                x0:
                  historicalDates.length > 0
                    ? historicalDates[historicalDates.length - 1]
                    : futureDates[0],
                y0: -1,
                x1:
                  historicalDates.length > 0
                    ? historicalDates[historicalDates.length - 1]
                    : futureDates[0],
                y1: 1,
                line: {
                  color: "rgba(0, 0, 0, 0.3)",
                  width: 1,
                  dash: "dot",
                },
              },
              // 正面情感區域 (淺綠色背景)
              {
                type: "rect",
                x0: historicalDates[0] || futureDates[0],
                x1:
                  futureDates[futureDates.length - 1] ||
                  historicalDates[historicalDates.length - 1],
                y0: 0,
                y1: 1,
                fillcolor: "rgba(75, 192, 192, 0.1)",
                line: { width: 0 },
              },
              // 負面情感區域 (淺紅色背景)
              {
                type: "rect",
                x0: historicalDates[0] || futureDates[0],
                x1:
                  futureDates[futureDates.length - 1] ||
                  historicalDates[historicalDates.length - 1],
                y0: -1,
                y1: 0,
                fillcolor: "rgba(255, 99, 132, 0.1)",
                line: { width: 0 },
              },
            ],
            plot_bgcolor: "#f8f9fa",
            paper_bgcolor: "#ffffff",
            height: 300,
          };

          const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ["select2d", "lasso2d"],
            displaylogo: false,
          };

          if (this.topNews && this.topNews.length) {
            // 為每個新聞創建一個標記點
            const newsMarkers = {
              x: [], // 新聞對應的日期點
              y: [], // 新聞對應的情感值
              type: "scatter",
              mode: "markers",
              name: "重要新聞",
              marker: {
                size: 10,
                color: "rgba(255, 0, 0, 0.7)",
                symbol: "star",
              },
              text: [], // 新聞標題作為懸停文本
              hoverinfo: "text+x+y",
            };

            // 假設新聞都在最近的日期點，您也可以從API獲取具體日期
            const recentDate = historicalDates[historicalDates.length - 1];

            this.topNews.forEach((news) => {
              newsMarkers.x.push(recentDate);
              // 使用新聞的情感影響值作為Y坐標
              newsMarkers.y.push(news.impact);
              newsMarkers.text.push(news.title);
            });

            // 添加到圖表
            Plotly.newPlot(
              this.$refs.sentimentChartContainer,
              [traceZero, traceHistorical, traceFuture, newsMarkers],
              layout,
              config
            );
          } else {
            Plotly.newPlot(
              this.$refs.sentimentChartContainer,
              [traceZero, traceHistorical, traceFuture],
              layout,
              config
            );
          }
        } catch (error) {
          console.error("Error rendering sentiment chart:", error);
        }
      },
    },
  };
</script>

<style scoped>
  .sentiment-analysis {
    margin-top: 35px;
    padding: 20px;
    border-radius: 8px;
    background-color: #f8f9fa;
    border: 1px solid #e9ecef;
  }

  .sentiment-analysis h4 {
    margin-top: 0;
    color: #495057;
    margin-bottom: 15px;
    font-size: 18px;
    border-bottom: 1px solid #dee2e6;
    padding-bottom: 10px;
  }

  .sentiment-summary {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }

  .sentiment-score,
  .sentiment-impact {
    flex: 1;
    min-width: 200px;
    padding: 15px;
    background-color: white;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    margin: 5px;
  }

  .sentiment-label {
    font-weight: 500;
    color: #6c757d;
    margin-bottom: 8px;
  }

  .sentiment-value {
    font-size: 18px;
    font-weight: bold;
  }

  .very-positive {
    color: #28a745;
  }
  .positive {
    color: #4dbd74;
  }
  .neutral {
    color: #6c757d;
  }
  .negative {
    color: #f86c6b;
  }
  .very-negative {
    color: #dc3545;
  }

  .impact-badge {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 15px;
    font-weight: bold;
    color: white;
    font-size: 14px;
  }

  .high-impact {
    background-color: #dc3545;
  }
  .medium-impact {
    background-color: #ffc107;
  }
  .low-impact {
    background-color: #6c757d;
  }

  .chart-container {
    height: 350px;
    margin: 25px 0;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 5px rgba(0, 0, 0, 0.03);
  }

  .top-news-section {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #e9ecef;
  }

  .top-news-section h4 {
    color: #495057;
    margin-bottom: 20px;
    font-weight: 600;
  }

  .news-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }

  .news-item {
    padding: 15px;
    border-radius: 8px;
    transition: all 0.2s ease;
    border-left: 4px solid transparent;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    background-color: white;
  }

  .news-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
  }

  .news-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }

  .impact-indicator {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 700;
    color: white;
  }

  .impact-indicator.positive {
    background-color: #28a745;
  }

  .impact-indicator.negative {
    background-color: #dc3545;
  }

  .impact-score {
    font-size: 13px;
    font-weight: 500;
    color: #6c757d;
  }

  .news-title {
    font-size: 15px;
    line-height: 1.4;
  }

  .news-title a {
    color: #343a40;
    text-decoration: none;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .news-title a:hover {
    color: #0d6efd;
    text-decoration: underline;
  }

  .external-link-icon {
    font-style: normal;
    color: #6c757d;
    font-size: 14px;
    opacity: 0.7;
    margin-left: 6px;
  }

  .high-impact-news {
    border-left-color: #dc3545;
  }

  .medium-impact-news {
    border-left-color: #ffc107;
  }

  .low-impact-news {
    border-left-color: #6c757d;
  }

  .sentiment-explanation {
    margin-top: 20px;
    padding: 15px;
    background-color: rgba(255, 255, 255, 0.7);
    border-radius: 6px;
    border-left: 3px solid #17a2b8;
  }

  .sentiment-explanation h5 {
    margin-top: 0;
    color: #495057;
    margin-bottom: 10px;
    font-size: 16px;
  }

  .sentiment-explanation p {
    margin-bottom: 10px;
    color: #6c757d;
    font-size: 14px;
    line-height: 1.6;
  }

  @media (max-width: 768px) {
    .sentiment-summary {
      flex-direction: column;
    }

    .chart-container {
      height: 280px;
    }

    .news-item {
      padding: 12px;
    }

    .news-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 5px;
    }
  }
</style>
