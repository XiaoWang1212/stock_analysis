<template>
    <div class="home-page">
        <div class="main-info">
            <div class="home-title">預判市場走勢，領先一步看見市場變化</div>
            <div class="start-button" @click="toLogin">開始分析</div>
        </div>
        <div class="home-image"></div>
    </div>
        <div class="function-flame">
            <div class="function-descript">
                <div class="function-title">提供多種視覺化圖表</div>
                <i class="fa-solid fa-line-chart"></i>
                <div class="function-content">我們提供了多達10種的視覺化圖表，讓您對股市的脈動一目了然</div>
            </div>
            <div class="function-descript">
                <div class="function-title">最先進的AI智能預測</div>
                <i class="fa-solid fa-gears"></i>
                <div class="function-content">利用AI能預測，分析未來7天的股價，以及可能影響價格相關訊息，讓您一手掌握股票趨勢</div>
            </div>
            <div class="function-descript">
                <div class="function-title">創建專屬的股票群組</div>
                <i class="fa-solid fa-coins"></i>
                <div class="function-content">您可以在這裡創建屬於自己的股票群組，管理並監測心目中的理想股</div>
            </div>
        </div>
</template>

<script>
    export default {
        name: "HomePage",
        methods: {
            toLogin (){
                this.$router.push({
                    name: "Login"
                });
            },
        },
    };
</script>

<style scoped>
    .home-page {
        padding: 30px;
        max-width: 1300px;
        margin: 0 auto;
        display: flex;
        justify-content: center;
        height: 100vh;
    }
    .main-info{
        padding-top: 100px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .home-title{
        width: 100%;
        color: white;
        font-size: 40px;
        font-weight: bold;
        text-align: start;
        margin-bottom: 30px;
        position: relative;
        top: -100px;
    }
    .start-button{
        width: 100px;
        padding: 12px 24px;
        font-size: 16px;
        color: white;
        border-radius: 8px;
        background-color: #5b5b5b;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        top: -100px;
    }
    .start-button:hover{
        background-color: #66b3ff;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }
    .home-image{
        background-image: url("@/assets/photos/stock_analysis_bg.JPG");
        background-size: cover;
        width: 40%;
        height: 80%;
        border-radius: 10px 150px;
        margin-left: 30px;
        box-shadow: 8px 8px 8px #4F4F4F;
    }
    .function-flame{
        display: grid;
        justify-content: center;
        align-items: center;
        grid-template-columns: repeat(3, 30%);
        gap: 3%;
        height: 100vh;
        padding-bottom: 50px;
    }
    .function-descript{
        background-color: #4F4F4F;
        border-radius: 8px;
        padding: 20px;
        height: 40%;
    }
    .function-title{
        font-size: 23px;
        font-weight: bold;
        color: white;
        margin-bottom: 10px;
    }

    .fa-solid{
        font-size: 80px;
        color: white;
        margin: 25px;
    }

    .function-content{
        font-size: 20px;
        color: white;
    }

    @media (max-width: 1050px){
        .function-descript{
            height: 45%;
        }
    }

    @media (max-width: 850px){
        .home-image{
            display: none;
        }
        .function-flame{
            grid-template-columns: 80%;
            height: 150vh;
        }
        .function-descript{
            height: 85%;
        }
    }
</style>